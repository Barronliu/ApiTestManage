from ..global_variable import *
import os


def request(flow):
    file_name = "data_list.txt"
    file_path = os.path.join(SCRIPT_FILE, file_name)
    if os.path.exists(file_path):
        os.remove(file_path)
    if flow.request.pretty_host == 'sdlog.mmbang.com':
        request_method = flow.request.method
        if request_method == 'POST':
            body = flow.request.urlencoded_form
            if "data_list" in body:
                with open(file_path, 'a') as f:
                    f.write(body["data_list"])
                    f.write('\n')
        elif request_method == 'GET':
            params = flow.request.query
            keys = params.keys()
            if "data_list" in keys:
                with open(file_path, 'a') as f:
                    f.write(params["data_list"])
                    f.write('\n')
        else:
            pass
