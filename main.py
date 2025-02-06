import markdown
from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor
import xml.etree.ElementTree as etree

from flask import Flask, render_template, jsonify, request
import subprocess
import os
import markdown

import configparser

config = configparser.ConfigParser()
config.read('config.ini')
allowed_ip = [config['url']['server_ip'],'127.0.0.1']
def limit_ip_address(func):
    def wrapper(*args, **kwargs):
        if request.remote_addr not in allowed_ip:
            return f'Forbidden, request IP {request.remote_addr}', 403  
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper

class HoverInlineProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        el = etree.Element('hover')
        el.text = m.group(1)
        return el, m.start(0), m.end(0)

class HoverExtension(Extension):
    def extendMarkdown(self, md):
        pattern = r'\{\{(.*?)\}\}'
        md.inlinePatterns.register(HoverInlineProcessor(pattern, md), 'hover', 175)

def parse_markdown_with_hover(md_text):
    md = markdown.Markdown(extensions=[HoverExtension()])
    return md.convert(md_text)


# md_text = "这是一个测试，{{这是一个悬停效果}}，看看它如何工作。"
# html_output = parse_markdown_with_hover(md_text)
# print(html_output)

app = Flask(__name__)

# 设置Markdown文件所在的目录
NOTES_DIR = os.path.join('static', 'note')

# 首页，列出所有Markdown文件
@limit_ip_address
@app.route('/')
def index():
    files = [f for f in os.listdir(NOTES_DIR) if f.endswith('.md')]
    return render_template('index.html', files=files)

# 查看文件的内容，返回解析后的HTML页面
@app.route('/view/<filename>')
@limit_ip_address
def view(filename):
    file_path = os.path.join(NOTES_DIR, filename)
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # 解析Markdown内容为HTML
    html_content = parse_markdown_with_hover(content)
    return render_template('view.html', filename=filename, html_content=html_content)
@app.route('/pull', methods=['GET'])
@limit_ip_address
def git_pull():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(current_dir,'static')
    result = subprocess.run(['git', 'pull'], cwd=os.path.join(static_dir, 'note'), check=True, text=True, capture_output=True)
    return jsonify({'success': True, 'output': result.stdout})
# 启动应用 gunicorn -w 1 -b 0.0.0.0:5001 main:app
# if __name__ == '__main__':
#     app.run(debug=True)