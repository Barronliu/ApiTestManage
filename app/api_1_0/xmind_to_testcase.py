from flask import jsonify, request, render_template, flash
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
    if not exists(join(FILE_ADDRESS, filename_ori)):
        return jsonify({'msg': '请上传文件', 'status': 0})
    zentao_csv_file = xmind_to_zentao_csv_file(filename_ori)
    if zentao_csv_file:
        filename_zandao = os.path.basename(zentao_csv_file)
        return jsonify({'data': filename_zandao, 'msg': '', 'status': 1})
    else:
        flash("测试用例转换失败")
        return jsonify({'msg': '测试用例转换失败', 'status': 0})


@api.route('/preview')
def preview_file():
    data = request.json
    file_address = data.get('importApiAddress')
    full_path = join(FILE_ADDRESS, file_address)

    if not exists(file_address):
        return jsonify({'msg': '请上传文件', 'status': 0})

    testsuites = get_xmind_testsuites(file_address)
    suite_count = 0
    for suite in testsuites:
        suite_count += len(suite.sub_suites)

    testcases = get_xmind_testcase_list(file_address)

    return render_template("templates/preview.html", name=file_address, suite=testcases, suite_count=suite_count)

