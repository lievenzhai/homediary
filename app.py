from flask import Flask, url_for, render_template
from datetime import datetime

now = datetime.now()

# 虚拟数据
name1 = '翟立元'
diaries1 = [
    {'date':'20200529', 'title':'翟子爱晶晶'},
    {'date':'20200528', 'title':'翟子爱葡萄'},
    {'date':'20200527', 'title':'晶晶爱葡萄'}
]


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', name=name1, diaries=diaries1)

app.run()

