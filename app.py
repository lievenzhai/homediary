from flask import Flask, url_for, render_template, request, flash, redirect
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exists
import os, sys
from werkzeug.security import generate_password_hash, check_password_hash
import click
from flask_login import LoginManager, UserMixin,login_user,logout_user,login_required,current_user

app = Flask(__name__)
# 写入了一个 SQLALCHEMY_DATABASE_URI 变量来告诉 SQLAlchemy 数据库连接地址
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATTONS'] = False  # 关闭对模型修改的监控
app.config['SECRET_KEY'] = 'dev'
app.secret_key = 'dev'


db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(db.Model, UserMixin):  # 表名将会是user（自动生成，小写处理）
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class Diary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # user = db.Column(db.String(20))
    title = db.Column(db.String(60))
    article = db.Column(db.String(4000))
    author = db.Column(db.String(20))


# 定义时间
now = datetime.now()


@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)


@app.route('/',methods=['GET','POST'])
def index():
    if current_user.is_authenticated:
        if request.method == 'POST':
            if not current_user.is_authenticated:
                return redirect(url_for('index'))
        diaries = Diary.query.filter_by(author=current_user.username).all()
        return render_template('index.html', diaries=diaries)
    return redirect(url_for('login'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/diary', methods=['GET', 'POST'])
def diary():
    if request.method == 'POST':
        title = request.form.get('title')
        article = request.form.get('article')
        username = current_user.username
        if not title or len(title) > 60:
            flash('无效的输入')
            return redirect(url_for('diary'))  # ??
        diary = Diary(title=title, article=article, author=username)
        db.session.add(diary)
        db.session.commit()
        flash('新的日记已保存')
        return redirect(url_for('index'))
    diaries = Diary.query.all()
    return render_template('diary.html',diaries=diaries)


@app.route('/diary/edit<int:diary_id>', methods=['GET', 'POST'])
@login_required
def edit(diary_id):
    diary = Diary.query.get_or_404(diary_id)

    if request.method == 'POST':
        title = request.form['title']
        article = request.form['article']
        if not title or not article or len(title) > 60 or len(article) > 4000:
            flash('错误输入')
            return redirect(url_for('edit', diary_id=diary_id))

        diary.title = title
        diary.article = article
        db.session.commit()
        flash('编辑更新完成')
        return redirect(url_for('index'))
    return render_template('edit.html', diary=diary)


@app.route('/diary/delete/int:<diary_id>', methods=['POST'])
@login_required
def delete(diary_id):
    diary = Diary.query.get_or_404(diary_id)
    db.session.delete(diary)
    db.session.commit()
    flash('删除成功.')
    return redirect(url_for('index'))


@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form['password']
        if not username or not password or len(username) > 20 or len(password) > 128:
            flash('输入有误！')
            return redirect(url_for('register'))
        user = User(username=username)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()
        flash('注册成功！')
        return redirect(url_for('index'))
    return render_template('register.html')


@app.cli.command()
@click.option('--username', prompt=True, help='用户名用于登录')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='密码用于登录')
def admin(username, password):
    db.create_all()

    user = User.query.first()
    if user is not None:
        click.echo('更新用户')
        user.username = username
        user.set_password(password)
    else:
        click.echo('创建用户')
        user = User(username=username, name='管理员')
        user.set_password(password)
        db.session.add(user)

    db.session.commit()
    click.echo('创建完成')


@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    return user


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            flash('错误输入')
            return redirect(url_for('login'))
        #user = User.query.first()
        #if username == current_user.username and current_user.validate_password(password):
        user = User.query.filter(User.username == username).first()
        if user.validate_password(password):
            login_user(user)
            flash('登录成功！')
            return redirect(url_for('index'))
        flash('错误的用户名或密码')
        return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('再见')
    return redirect(url_for('index'))


@app.route('/settings', methods=['GET','POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']
        if not name or len(name) > 20:
            flash('设置错误')
            return redirect(url_for('setting'))
        current_user.name = name
        db.session.commit()
        flash('设置完成')
        return redirect(url_for('index'))
    return render_template('settings.html')


@app.route('/display/int:<diary_id>')
def display(diary_id):
    diary = Diary.query.get_or_404(diary_id)
    return render_template('display.html', diary=diary)


app.run()

