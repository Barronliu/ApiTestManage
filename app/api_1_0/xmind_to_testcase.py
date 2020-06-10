from flask import jsonify, request, render_template, flash, abort
from . import api, login_required
import os
from os.path import join, exists
from ..util.xmind2testcase.zentao import xmind_to_zentao_csv_file
from ..util.xmind2testcase.testlink import xmind_to_testlink_xml_file
from ..util.xmind2testcase.utils import get_xmind_testsuites, get_xmind_testcase_list
from ..util.global_variable import *


@api.route('/zentao', methods=['GET'])
def download_zentao_file():
    filename_ori = request.args.get("filename")
    full_adress = join(FILE_ADDRESS, filename_ori)
    if not exists(full_adress):
        return jsonify({'msg': '请上传文件', 'status': 0})
    zentao_csv_file = xmind_to_zentao_csv_file(full_adress)
    if zentao_csv_file:
        filename_zandao = os.path.basename(zentao_csv_file)
        return jsonify({'data': filename_zandao, 'msg': '', 'status': 1})
    else:
        flash("测试用例转换失败")
        return jsonify({'msg': '测试用例转换失败', 'status': 0})


@api.route('/preview', methods=['GET'])
def preview_file():
    filename_xmind = request.args.get("filename")
    full_adress = join(FILE_ADDRESS, filename_xmind)
    if not exists(full_adress):
        return jsonify({'msg': "请上传文件", 'status': 0})
    testsuites, _ = get_xmind_testsuites(full_adress)
    suite_count = 0
    for suite in testsuites:
        suite_count += len(suite.sub_suites)

    testcases = get_xmind_testcase_list(full_adress)
    csv_file_name = os.path.splitext(filename_xmind)[0] + ".csv"

    return render_template("preview.html", name=filename_xmind, suite=testcases, suite_count=suite_count, csv_name=csv_file_name)

