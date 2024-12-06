# coding:utf8

import os
from string import Template
from flask import Flask, request, send_file
from werkzeug.utils import secure_filename


app = Flask(__name__)
pwd = os.path.dirname(__file__)

#定义文件的保存路径和文件名尾缀
UPLOAD_FOLDER = os.path.join(pwd,'save_file')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

HOST = "127.0.0.1"
PORT = 7000


@app.route('/index')
def index():
    """
    返回一个网页端提交的页面
    :return:
    """
    html = Template("""
    <!DOCTYPE html>
    <html>
       <body>
    
          <form action = "http://$HOST:$PORT/upload" method = "POST"
             enctype = "multipart/form-data">
             <input type = "file" name = "file" />
             <input type = "submit"/>
          </form>
    
       </body>
    </html>
    """)
    html = html.substitute({"HOST": HOST, "PORT": PORT})
    return html

def allowed_file(filename):
    """
    检验文件名尾缀是否满足格式要求
    :param filename:
    :return:
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """
    上传文件到save_file文件夹: 同名文件直接覆盖
    以requests上传举例
    wiht open('路径','rb') as file_obj:
        rsp = requests.post('http://localhost:5000/upload,files={'file':file_obj})
        print(rsp.text) --> file uploaded successfully
    """
    if 'file' not in request.files:
        return "No file part"
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return 'file uploaded successfully'
    return "file uploaded Fail"


@app.route("/download")
def download_file():
    """
    下载src_file目录下面的文件
    eg：下载当前目录下面的文件，eg:http://localhost:7000/download?filename=123.tar
    :return:
    """
    file_name = request.args.get('filename')
    print(f'文件名: {file_name=}')
    # file_path = os.path.join(pwd,'src_file',file_name)
    file_path = os.path.join(pwd,'save_file',file_name)
    if os.path.isfile(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "The downloaded file does not exist"


import requests

def getFile(filename):
    """
        下载文件
    """
    URL=f"http://{HOST}:{PORT}/upload"

    # f = open(r'D:\work\tools\file_server\templates\upload.html','rb')
    f = open(filename)
    rsp = requests.get(URL, files={'file':f})
    print(rsp.text)


if __name__ == '__main__':
    app.run(host=HOST, port=PORT)