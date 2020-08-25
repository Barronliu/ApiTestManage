from flask import jsonify, request
from . import api, login_required
from app.models import *
from ..util.excel_parser.excel_parser import excelHandle
from ..util.shence_parser.shence import *
from ..util.global_variable import *
from ..util.utils import *
from ..util.report.report import *


@api.route('/maidian/add', methods=['GET'])
@login_required
def add_maidian():
    """ 从埋点文档录入埋点需求 """
    file_address = request.args.get('fileAddress')
    if not file_address:
        return jsonify({'msg': '请上传文件', 'status': 0})
    excel_parser = excelHandle()
    maidian_data = excel_parser.parser_sheet(file_address)
    for event in maidian_data:
        _event_name = Maidian.query.filter_by(event=event['event']).all()
        if _event_name:
            for event_name in _event_name:
                db.session.delete(event_name)
        for element, value in event['page_and_element_names'].items():
            new_maidian = []
            for param in value:
                new_maidian.append(Maidian(event=event['event'], page_or_element_name=element, is_page=event['is_page'],
                                      params=param, params_type=value[param]))
            db.session.add_all(new_maidian)
            db.session.commit()
    return jsonify({'msg': '导入成功', 'status': 1})


@api.route('/maidian/find', methods=['GET'])
@login_required
def find_maidian():
    """ 查找埋点 """
    _data = {
        "event_name": "",
        "is_page": 0,
        "page_or_element_names": {}
    }
    _event_name = request.args.get('event_name')
    _element_name = request.args.get('element_name')
    if _event_name:
        event_name = Maidian.query.filter_by(event=_event_name).first()
        if not event_name:
            return jsonify({'msg': '事件名不存在', 'status': 1})

        is_page = event_name.is_page
        _data['event_name'] = _event_name
        _data['is_page'] = is_page

        if _element_name:
            element_name = Maidian.query.filter_by(event=_event_name, page_or_element_name=_element_name).all()
            _params = {}
            if element_name:
                for element in element_name:
                    _parm_name = element.params
                    _parm_type = element.params_type
                    _params.update({_parm_name: _parm_type})
                _data['page_or_element_names'].update({_element_name: _params})
                return jsonify({'data': _data, 'msg': '', 'status': 1})
            return jsonify({'msg': 'element name or page name not exist', 'status': 0})

        _events = Maidian.query.filter_by(event=_event_name).all()
        if _events:
            for element in _events:
                _params_for_element = Maidian.query.filter_by(page_or_element_name=element.page_or_element_name).all()
                if _params_for_element:
                    _params = {}
                    for param in _params_for_element:
                        _parm_name = param.params
                        _parm_type = param.params_type
                        _params.update({_parm_name: _parm_type})
                    _data['page_or_element_names'].update({element.page_or_element_name: _params})
        return jsonify({'data': _data, 'msg': '', 'status': 1})
    return jsonify({'msg': '请填写事件名称', 'status': 0})


@api.route('/maidian/check', methods=['GET'])
@login_required
def check_maidian():
    """ 核对埋点数据 """
    file_name = "data_list.txt"
    data_file = os.path.join(SCRIPT_FILE, file_name)
    results = {
        'success': True,
        'summary': {
            'test_time': '',
            'total': 0,
            'success': 0,
            'fail': 0,
            'skip': 0,
            'not_test': 0
        },
        'details': [],
    }
    results['summary']['test_time'] = get_current_time()

    with open(data_file, 'r') as f:
        for line in f:
            _data = paser_shence_data(line)

            if _data:
                _temp = {}
                event = _data['event']
                events = Maidian.query.filter_by(event=event).all()
                error_data = {'event_name': event, 'total': 0, 'success': 0, 'fail': 0, 'info': []}
                _info = {'element_name': '', 'success': True, 'reason': [], 'log': {}}
                if not events:
                    msg = '上报的事件名不存在，请确认文档是否已导入'
                    _info['log'].update({'target_data': {}, 'test_data': _data})
                    _info['success'] = False
                    _info['reason'].append(msg)
                    error_data['info'].append(_info)
                    results['details'].append(error_data)
                    continue
                for element in events:
                    _info = {'element_name': '', 'success': True, 'reason': [], 'log': {}}
                    err_flag = False
                    _element_name = element.page_or_element_name

                    #去除重复element
                    if (_element_name in _temp) and _temp[_element_name] == event:
                        continue
                    _temp[_element_name] = event

                    _info['element_name'] = _element_name
                    if _element_name in _data.keys():
                        if not check_data_value(_data['is_page'], element.is_page):
                            msg = "'is_page' should be {}".format(element.is_page)
                            _info['reason'].append(msg)
                            _info['log'].update({'target_data': element.to_dict(), 'test_data': _data})
                            error_data['info'].append(_info)
                            results['details'].append(error_data)
                            err_flag = True

                        _params_for_element = Maidian.query.filter_by(page_or_element_name=_element_name).all()
                        if _params_for_element:
                            for param in _params_for_element:
                                _parm_name = param.params
                                if _parm_name in _data[element.page_or_element_name].keys():
                                    if not check_data_type(_data[element.page_or_element_name][_parm_name],
                                                           param.params_type):
                                        msg = "{} param type should be {}".format(_parm_name, param.params_type)
                                        _info['reason'].append(msg)
                                        _info['log'].update({'target_data': element.to_dict(), 'test_data': _data})
                                        error_data['info'].append(_info)
                                        results['details'].append(error_data)
                                        err_flag = True
                                        continue
                                    else:
                                        _info['log'].update({'target_data': element.to_dict(), 'test_data': _data})
                                        error_data['info'].append(_info)
                                        results['details'].append(error_data)
                                        continue
                                msg = "{} 参数缺失".format(_parm_name)
                                _info['reason'].append(msg)
                                _info['log'].update({'target_data': element.to_dict(), 'test_data': _data})
                                error_data['info'].append(_info)
                                results['details'].append(error_data)
                                err_flag = True
                    else:
                        err_flag = True
                    if err_flag:
                        _info['success'] = False
        test_result = aggregate(results)

        return render_html_report_maidian(test_result)
