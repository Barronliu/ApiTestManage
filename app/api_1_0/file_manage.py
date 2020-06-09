from flask import jsonify, request, abort, send_from_directory,flash
from . import api, login_required
from ..util.global_variable import *
from werkzeug.utils import secure_filename


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 上传文件
@api.route('/upload', methods=['POST'], strict_slashes=False)
@login_required
def api_upload():
    """ 文件上传 """
    if 'file' not in request.files:
        return jsonify({"msg": "请选择文件", "status": 3})
    data = request.files
    file = data['file']
    filename = secure_filename("temp" + file.filename)
    skip = request.form.get('skip')
    if file and allowed_file(filename):
        if os.path.exists(os.path.join(FILE_ADDRESS, filename)) and not skip:
            return jsonify({"msg": "文件已存在，请修改文件名字后再上传", "status": 0})
        else:
            file.save(os.path.join(FILE_ADDRESS, filename))
            return jsonify({'data': {'file_address': os.path.join(FILE_ADDRESS, filename), 'filename': filename}, "msg": "上传成功", "status": 1})
    flash('文件不存在或不支持的文件类型，请重新上传')
    return jsonify({'msg': '不支持的文件', 'status': 0})


#下载文件
@api.route('/downloadFile')
@login_required
def api_download_file():
    filename = request.args.get("filename")
    if filename and not os.path.exists(os.path.join(FILE_ADDRESS, filename)):
        abort(404)
    return send_from_directory(FILE_ADDRESS, filename, as_attachment=True)

@api.route('/checkFile', methods=['POST'], strict_slashes=False)
@login_required
def check_file():
    """ 检查文件是否存在 """
    data = request.json
    address = data.get('address')
    if os.path.exists(address):
        return jsonify({"msg": "文件已存在", "status": 0})
    else:
        return jsonify({"msg": "文件不存在", "status": 1})
