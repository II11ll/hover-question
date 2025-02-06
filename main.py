import markdown
from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor
import xml.etree.ElementTree as etree

from flask import Flask, render_template
import os
import markdown

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
@app.route('/')
def index():
    files = [f for f in os.listdir(NOTES_DIR) if f.endswith('.md')]
    return render_template('index.html', files=files)

# 查看文件的内容，返回解析后的HTML页面
@app.route('/view/<filename>')
def view(filename):
    file_path = os.path.join(NOTES_DIR, filename)
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # 解析Markdown内容为HTML
    html_content = parse_markdown_with_hover(content)
    return render_template('view.html', filename=filename, html_content=html_content)


# 启动应用
if __name__ == '__main__':
    app.run(debug=True)