import os

from flask import Flask, send_from_directory, render_template, g, request, flash, redirect, make_response


# from werkzeug.utils import secure_filename

def read_filenames_with_version(folder):
    # 创建一个空列表来存储结果
    result = []
    # 遍历文件夹下的所有文件
    for file in os.listdir(folder):
        # 把文件名按照 _ 拆分成三段
        segments = file.split("_")
        # 如果拆分后的长度不是3，说明文件名不符合要求，跳过这个文件
        if len(segments) != 3:
            continue
        # 否则，把拆分后的三段分别赋值给业务线、版本、文件类型
        business, version, file_type = segments
        # 把这三个值作为一个元组添加到结果列表中
        result.append((business, version, file_type, file))
    # 返回结果列表
    return result


def read_filenames(folder):
    # 创建一个空列表来存储结果
    result = []
    # 遍历文件夹下的所有文件
    for file in os.listdir(folder):
        # 把文件名按照 _ 拆分成2段
        segments = file.split("_")
        # 如果拆分后的长度不是3，说明文件名不符合要求，跳过这个文件
        if len(segments) != 2:
            continue
        # 否则，把拆分后的三段分别赋值给业务线、版本、文件类型
        business, file_type = segments
        file_type = file_type.split('.')[0]
        # 把这三个值作为一个元组添加到结果列表中
        result.append((business, file_type, file))
    # 返回结果列表
    return result


def create_app():
    # create and configure the app
    app = Flask(__name__)
    app.secret_key = 'dev'
    app.debug = True

    @app.before_request
    def before_request():
        if request.path == '/':
            g.file_tuple = read_filenames('file/standard')
            print(g.file_tuple)


    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    @app.route('/')
    def index():
        return render_template('数据标准文件管理.html', tuples=g.file_tuple)

    @app.route('/second')
    def second():
        return render_template('数据线落标检查.html')

    @app.route('/third')
    def third():
        return render_template('业务线数据落标.html')

    @app.route('/download_template/<file_name>')
    def download_template(file_name):
        return send_from_directory('file/template', file_name, as_attachment=True)

    @app.route('/download_file/<file_name>')
    def download_file(file_name):
        return send_from_directory('file/standard', file_name, as_attachment=True)

    @app.route('/submit', methods=['POST'])
    def submit():
        # 获取表单中的文本数据
        business = request.form.get('business')
        fileType = request.form.get('fileType')
        # 获取表单中的文件数据
        dataFile = request.files.get('dataFile')
        # 验证文件是否存在并且符合要求
        if dataFile and dataFile.filename.endswith('.xlsx'):
            # 为文件生成一个安全的文件名
            filename = business + "_" + fileType + ".xlsx"
            # 将文件保存到服务器的uploads目录下
            dataFile.save(os.path.join('file/standard', filename))
            # 返回一个成功的响应
            response = make_response(redirect("/"))
            flash(f'{filename}上传成功！')
            return response
        else:
            # 返回一个失败的响应
            flash('文件上传失败，请检查文件类型是否正确！')
            return redirect("/")

    return app


if __name__ == '__main__':
    app = create_app()
    app.run()
