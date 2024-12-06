import os
import uuid
import sqlite3 # python内置
print(sqlite3.sqlite_version) # 查看版本

from flask import Flask, request, send_from_directory, render_template
 
app = Flask(__name__) # 以当前文件名作为应用名称

UPLOAD_FOLDER = 'save_file'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 设置最大文件上传大小为 100MB
 
# 创建保存文件的目录
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
 
# 初始化数据库
conn = sqlite3.connect('file_mapping.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS files
             (id INTEGER PRIMARY KEY, original_filename TEXT, new_filename TEXT)''')
conn.commit()
conn.close()
 
 
@app.route('/')
def index():
    return render_template("Upload.html")
 
 
@app.route('/upload', methods=['POST'])
def upload_file():
    """
        上传目录里所有文件
    """
    if request.method == 'POST':
        if 'folder' not in request.files:
            return 'No folder part'
        folder = request.files.getlist('folder')
        try:
            conn = sqlite3.connect('file_mapping.db')
            # noinspection PyShadowingNames
            c = conn.cursor()
            for file in folder:
                if file.filename == '':
                    return '没有选择文件'
                if file:
                    original_filename = file.filename
                    # 查询数据库，检查文件名是否已经存在
                    c.execute("SELECT id FROM files WHERE original_filename=?", (original_filename,))
                    existing_file = c.fetchone()
                    if existing_file:
                        continue
                    else:
                        # 生成唯一的文件名
                        new_filename = str(uuid.uuid4()) + os.path.splitext(original_filename)[1]
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
                        file.save(file_path)
                        # 存储原始文件名和新文件名的关联关系到数据库
                        c.execute("INSERT INTO files (original_filename, new_filename) VALUES (?, ?)",
                                  (original_filename, new_filename))
            conn.commit()
            return '文件上传完成'
        except Exception as e:
            return '文件上载过程中出错: {}'.format(str(e))
        finally:
            conn.close()
    else:
        return '请求方法不允许'
 
 
@app.route('/list_files', methods=['GET'])
def list_files():
    conn = sqlite3.connect('file_mapping.db')
    c = conn.cursor()
    c.execute("SELECT original_filename, new_filename FROM files")
    files = c.fetchall()
    conn.close()
    return render_template('Review.html', files=files)
 
 
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
 
 
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000, debug=True)
