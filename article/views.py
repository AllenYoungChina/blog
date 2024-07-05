from flask import (
    Blueprint, request, abort, render_template, redirect, url_for, flash
)
from http import HTTPStatus
from flask_login import login_required, current_user

from app import db
from .models import Article

article_bp = Blueprint('article', __name__, url_prefix='article')


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
        return redirect(url_for('article.mine'))

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
    article = get_article(article_id)
    db.session.delete(article)
    db.session.commit()
    return redirect(url_for('article.mine'))


@article_bp.route('/mine')
@login_required
def mine():
    """我的文章"""
    article_list = db.session.execute(
        db.select(Article).filter(Article.user_id == current_user.id)
        .order_by(Article.created_at.desc())
    ).scalars()
    return render_template('article/mine.html', article_list=article_list)
