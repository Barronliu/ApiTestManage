import urllib.parse
import base64
import gzip
from io import BytesIO
import json
from ..global_variable import *

def paser_shence_data(data_list):
    data_list_decoded = urllib.parse.unquote(data_list)
    data_list_base64_decoded = base64.b64decode(data_list_decoded)
    buff = BytesIO(data_list_base64_decoded)
    f = gzip.GzipFile(fileobj=buff)
    data = f.read().decode('utf-8')
    result_data = json.loads(data)[0]
    _data = {}
    if result_data:
        if 'event' in result_data.keys():
            _data['event'] = result_data['event']
            if 'element_name' in result_data['properties'].keys():
                element_name = result_data['properties']['element_name']
                _data['is_page'] = 0
                _data.update({element_name: result_data['properties']})
            elif 'page_name' in result_data['properties'].keys():
                page_name = result_data['properties']['page_name']
                _data['is_page'] = 1
                _data.update({page_name: result_data['properties']})
    return _data


def check_data_value(test_data, target_data):
    if isinstance(test_data, type(target_data)) and test_data == target_data:
        return True
    return False


def check_data_type(test_data, target_data):
    print("test_data_type: ", type(test_data))
    if target_data == "NUMBER":
        if isinstance(test_data, int):
            return True
    elif target_data == "STRING":
        if isinstance(test_data, str):
            return True
    elif target_data == "LIST":
        if isinstance(test_data, list):
            return True
    elif target_data == "SET":
        if isinstance(test_data, set):
            return True
    elif target_data == "DICT":
        if isinstance(test_data, dict):
            return True
    return False

def aggregate(tests_results):
    for detail in tests_results['details']:
        for element in detail['info']:
            tests_results['summary']['total'] += 1
            detail['total'] += 1
            if element['success']:
                detail['success'] += 1
                tests_results['summary']['success'] += 1
                continue
            detail['fail'] += 1
            tests_results['summary']['fail'] += 1
    if tests_results['summary']['fail'] != 0:
        tests_results['success'] = False
    return tests_results

def save_report(jump_res):
    report_file = os.path.join(SCRIPT_FILE, "maidian.txt")
    if os.path.exists(report_file):
        os.remove(report_file)
    with open(report_file, 'w') as f:
        f.write(jump_res)

if __name__ == "__main__":
    test_data = '123'
    target_data = "STRING"
    print(check_data_type(test_data, target_data))