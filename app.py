from flask import Flask, url_for, render_template
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import os, sys

app = Flask(__name__)
# 写入了一个 SQLALCHEMY_DATABASE_URI 变量来告诉 SQLAlchemy 数据库连接地址
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATTONS'] = False  # 关闭对模型修改的监控

db = SQLAlchemy(app)


class User(db.Model):  # 表名将会是user（自动生成，小写处理）
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))


class Diary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(40))
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


@app.route('/')
def index():
    user = User.query.first()
    diarys = Diary.query.all()
    return render_template('index.html', user=user, diaries=diarys)

app.run()

