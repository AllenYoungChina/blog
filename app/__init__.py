import os

from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager

login_manager = LoginManager()


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


# 加载环境变量
load_dotenv()


def create_app():
    """工厂函数"""
    app = Flask(__name__, template_folder='../templates', static_folder='../static')

    app.config['DEBUG'] = os.environ.get('DEBUG')
    app.config['TESTING'] = os.environ.get('TESTING')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')

    # 注册Flask-SQLAlchemy
    db.init_app(app)
    with app.app_context():
        # 根据数据库表格反射获取用户模型类
        db.reflect()

    # 注册Flask-Login
    from user.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.execute(
            db.select(User).filter_by(id=user_id)
        ).scalar()
    login_manager.login_view = 'user.login'
    login_manager.login_message = '请先登录'
    login_manager.init_app(app)

    # 注册蓝图
    init_bp(app)

    # 测试路由
    @app.route('/hello')
    def hello_world():
        return 'Hello, World!'

    # 添加跟路由
    app.add_url_rule('/', 'article.index')

    return app


def init_bp(app):
    """注册路由"""
    from user.views import user_bp
    from article.views import article_bp

    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(article_bp, url_prefix='/article')
