from flask import jsonify, request
from . import api, login_required
import subprocess
from ..util.global_variable import *
from ..util.utils import get_host_ip


@api.route('/proxy/start', methods=['GET'])
@login_required
def start_proxy():
    """ 启动代理，开始录制埋点请求数据 """
    filename = "myscript.py"
    script_file = os.path.join(SCRIPT_FILE, filename)
    _data = {
        'ip': "",
        'port': "8888"
    }
    ip = get_host_ip()
    _data['ip'] = ip
    cmd = "mitmproxy --listen-host {} -p 8888 -s {}".format(ip, script_file)
    subprocess.call(cmd, shell=True)
    return jsonify({'data': _data, 'msg': '请上传文件', 'status': 1})