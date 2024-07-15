import os.path
import uuid

from flask import (
    Blueprint, request, abort, render_template, redirect, url_for, flash, send_from_directory, current_app
)
from http import HTTPStatus
from flask_login import login_required, current_user

from app import db, IMAGE_ROOT
from article.models import Article

from utils.tools import compress_image

article_bp = Blueprint('article', __name__, url_prefix='article')

MAX_IMAGE_SIZE = 3 * 1024 * 1024  # 图片大小最大为3MB
IMAGE_COMPRESS_THRESHOLD = 1 * 1024 * 1024  # 图片大小超过1MB时对图片进行压缩


def get_article(article_id, check_auth=True):
    """根据文章ID获取文章"""
    article = db.session.execute(
        db.select(Article).filter(Article.id == article_id)
    ).scalar()

    if article is None:
        abort(HTTPStatus.NOT_FOUND)

    if check_auth and article.user_id != current_user.id:
        abort(HTTPStatus.NOT_FOUND)

    return article


@article_bp.route('/')
def index():
    """主页"""
    article_list = db.session.execute(
        db.select(Article).order_by(Article.created_at.desc())
    ).scalars()
    return render_template('article/index.html', article_list=article_list)


@article_bp.route('/<int:article_id>')
def detail(article_id):
    """文章详情"""
    article = get_article(article_id, check_auth=False)
    return render_template('article/detail.html', article=article)


@article_bp.route('/add', methods=('GET', 'POST'))
@login_required
def add():
    """新增文章"""
    error = ''
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        if not title:
            print(title)
            error = '请输入文章标题'

        article = Article(title=title, content=content, user_id=current_user.id)
        db.session.add(article)
        db.session.commit()
        return redirect(url_for('article.index'))

    if error:
        flash(error)

    return render_template('article/add.html')


@article_bp.route('/update/<int:article_id>', methods=('GET', 'POST'))
@login_required
def update(article_id):
    """修改文章"""
    error = ''
    article = get_article(article_id)
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            error = '请输入文章标题'

        if not error:
            article.title = title
            article.content = content
            db.session.commit()

            return redirect(url_for('article.detail', article_id=article_id))

    if error:
        flash(error)

    return render_template('article/update.html', article=article)


@article_bp.route('/delete/<int:article_id>', methods=('POST',))
@login_required
def delete(article_id):
    """删除文章"""
    # TODO: 待删除相关图片
    article = get_article(article_id)
    db.session.delete(article)
    db.session.commit()
    return redirect(url_for('article.index'))


@article_bp.route('/upload', methods=('GET', 'POST'))
@login_required
def upload():
    """图片上传接口"""
    error = ''
    filename = ''
    if request.method == 'POST':
        if 'file' not in request.files or not request.files['file'].filename:
            error = '未选择图片'
        else:
            file = request.files['file']

            # 验证实际文件大小，注意这会消耗文件流
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)  # 重置文件指针

            if file_size > MAX_IMAGE_SIZE:
                error = '图片过大'
            else:
                suffix = file.filename.rsplit('.', 1)[1].lower()
                if suffix in ['jpg', 'jpeg', 'png']:
                    filename = str(uuid.uuid4()) + '.' + suffix
                    file_path = os.path.join(IMAGE_ROOT, filename)
                    file.save(file_path)

                    # 压缩图片
                    if file_size > IMAGE_COMPRESS_THRESHOLD:
                        compress_image(file_path)
                else:
                    error = '图片格式错误'

    if error:
        flash(error)

    return render_template(
        'article/upload.html', filename=url_for('article.uploaded_file', filename=filename)
    )


@article_bp.route('/upload/<filename>', methods=('GET', 'POST'))
def uploaded_file(filename):
    """图片获取接口"""
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
