# 文件上传 API 路由
import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app.utils.decorators import login_required
from app.utils.response import success_response

upload_bp = Blueprint('upload', __name__)

# 允许的图片扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# 最大文件大小 (5MB)
MAX_FILE_SIZE = 5 * 1024 * 1024


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@upload_bp.route('/image', methods=['POST'])
@login_required
def upload_image():
    """
    上传图片文件

    请求格式: multipart/form-data
    参数: file - 图片文件

    返回: 图片URL
    """
    # 检查是否有文件
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '没有文件部分'}), 400

    file = request.files['file']

    # 检查是否选择了文件
    if file.filename == '':
        return jsonify({'success': False, 'message': '未选择文件'}), 400

    # 检查文件类型
    if not allowed_file(file.filename):
        return jsonify({
            'success': False,
            'message': f'不支持的文件类型，仅支持: {", ".join(ALLOWED_EXTENSIONS)}'
        }), 400

    # 检查文件大小
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    if file_size > MAX_FILE_SIZE:
        return jsonify({
            'success': False,
            'message': f'文件大小超过限制 (最大 {MAX_FILE_SIZE // (1024*1024)}MB)'
        }), 400

    # 生成安全的文件名
    original_filename = secure_filename(file.filename)
    filename = f"{uuid.uuid4().hex}_{original_filename}"

    # 创建上传目录
    upload_dir = os.path.join(current_app.root_path, '..', 'uploads', 'images')
    os.makedirs(upload_dir, exist_ok=True)

    # 保存文件
    file_path = os.path.join(upload_dir, filename)
    file.save(file_path)

    # 返回访问URL
    file_url = f"/uploads/images/{filename}"

    return success_response(data={
        'url': file_url,
        'filename': filename
    }, message='上传成功')


@upload_bp.route('/images', methods=['POST'])
@login_required
def upload_images():
    """
    批量上传图片文件

    请求格式: multipart/form-data
    参数: files - 多个图片文件

    返回: 图片URL列表
    """
    # 检查是否有文件
    if 'files' not in request.files:
        return jsonify({'success': False, 'message': '没有文件部分'}), 400

    files = request.files.getlist('files')

    if not files or files[0].filename == '':
        return jsonify({'success': False, 'message': '未选择文件'}), 400

    # 创建上传目录
    upload_dir = os.path.join(current_app.root_path, '..', 'uploads', 'images')
    os.makedirs(upload_dir, exist_ok=True)

    uploaded_files = []

    for file in files:
        # 检查文件类型
        if not allowed_file(file.filename):
            continue

        # 检查文件大小
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        if file_size > MAX_FILE_SIZE:
            continue

        # 生成安全的文件名
        original_filename = secure_filename(file.filename)
        filename = f"{uuid.uuid4().hex}_{original_filename}"

        # 保存文件
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)

        # 返回访问URL
        file_url = f"/uploads/images/{filename}"
        uploaded_files.append({
            'url': file_url,
            'filename': filename,
            'original_name': file.filename
        })

    return success_response(data={'files': uploaded_files}, message=f'成功上传 {len(uploaded_files)} 个文件')
