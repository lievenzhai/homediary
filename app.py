from flask import Flask, url_for, render_template, request, flash, redirect
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import os, sys

app = Flask(__name__)
# 写入了一个 SQLALCHEMY_DATABASE_URI 变量来告诉 SQLAlchemy 数据库连接地址
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATTONS'] = False  # 关闭对模型修改的监控

db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'dev'


class User(db.Model):  # 表名将会是user（自动生成，小写处理）
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))


class Diary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # user = db.Column(db.String(20))
    title = db.Column(db.String(60))
    article = db.Column(db.String(4000))

# 定义时间
now = datetime.now()

# 虚拟数据
name1 = '翟立元'
diaries1 = [
    {'date':'20200529', 'title':'翟子爱晶晶'},
    {'date':'20200528', 'title':'翟子爱葡萄'},
    {'date':'20200527', 'title':'晶晶爱葡萄'}
]


@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)


@app.route('/')
def index():
    diaries = Diary.query.all()
    return render_template('index.html', diaries=diaries)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/diary', methods=['GET', 'POST'])
def diary():
    if request.method == 'POST':
        title = request.form.get('title')
        article = request.form.get('article')
        if not title or len(title) > 60:
            flash('无效的输入')
            return redirect(url_for('diary'))  # ??
        diary = Diary(title=title, article=article)
        db.session.add(diary)
        db.session.commit()
        flash('新的日记已保存')
        return redirect(url_for('index'))
    diaries = Diary.query.all()
    return render_template('diary.html',diaries=diaries)


@app.route('/diary/edit<int:diary_id>', methods=['GET', 'POST'])
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
def delete(diary_id):
    diary = Diary.query.get_or_404(diary_id)
    db.session.delete(diary)
    db.session.commit()
    flash('删除成功.')
    return redirect(url_for('index'))



app.run()

