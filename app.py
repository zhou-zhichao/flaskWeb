import flask
from flask import Flask, send_from_directory, render_template, g, request, flash, redirect, make_response, url_for

from datatool import *


# from werkzeug.utils import secure_filename


def create_app():
    # create and configure the app
    app = Flask(__name__)
    app.secret_key = 'dev'
    app.debug = True

    @app.before_request
    def before_request():
        if request.path == '/':
            g.file_tuple = read_filenames(os.path.join('file', 'standard'))
            # print(g.file_tuple)
        elif request.path == '/third':
            filenames = get_all_filenames(os.path.join('file', 'input'))
            # print(filenames)
            g.table_tuple = transform_list(filenames)
            g.table_tuple.reverse()
            # print(g.table_tuple)

            # s = [('人事', '1.1', '', '人事_1.1_自定义代码.xlsx', '', '数据元素'),
            #      ('学工', '1', '学工_1_重要业务结果.xlsx', '', '', '数据元素'),
            #      ('学工', '1.1', '学工_1.1_重要业务结果.xlsx', '学工_1.1_自定义代码.xlsx', '', '数据元素')]
        elif request.path == "/second":
            filenames = get_all_filenames(os.path.join('file', 'confirm'))
            filenames.reverse()
            print(filenames)
            g.confirm_tuple = confirm_list_to_tuple(filenames)
            print(g.confirm_tuple)

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    @app.route('/')
    def index():
        return render_template('数据标准文件管理.html', tuples=g.file_tuple)

    @app.route('/second')
    def second():
        return render_template('数据线落标检查.html', tuples=g.confirm_tuple)

    @app.route('/third')
    def third():
        print(g.table_tuple)
        return render_template('业务线数据落标.html', tuples=g.table_tuple)

    @app.route('/download_template/<file_name>')
    def download_template(file_name):
        return send_from_directory('file/template', file_name, as_attachment=True)

    @app.route('/download_file/<file_name>')
    def download_file(file_name):
        return send_from_directory('file/standard', file_name, as_attachment=True)

    @app.route('/confirm_download/<filename>')
    def confirm_download(filename):
        path = 'file/confirm/'
        return send_from_directory(path, filename, as_attachment=True)

    @app.route("/confirm/<filename>")
    def confirm(filename):
        status = xlsx_func(filename)
        if status == 1:
            flash("拆分外供数据报错，查看表头是否正确")
        elif status == 2:
            flash("对外数据要求报错，查看表头是否正确")
        elif status == 3:
            flash("查看上传文件和数据元素核对是否都有'表/视图名称', '字段名'")
        return redirect("/second")

    @app.route('/third/download/<file_name>')
    def third_download(file_name):
        m = re.search(r".*(?=_[^_]+$)", file_name)
        # 如果 m 不为空，说明找到了匹配
        if m:
            # 使用 m.group() 方法，返回匹配的字符串
            path = m.group()
        # 否则，返回 None
        else:
            path = None
        path = os.path.join("file", "input", path)
        return send_from_directory(path, file_name, as_attachment=True)

    @app.route('/zip_download/<file_name>')
    def zip_download(file_name):
        version = file_name.rsplit('.', 1)[0]
        return send_from_directory(f"file/input/{version}/", file_name, as_attachment=True)

    @app.route('/second/download/<filename>')
    def second_download(filename):
        path = 'file/confirm/' + filename.rsplit('_', 1)[0] + '_重要业务结果/'
        return send_from_directory(path, filename, as_attachment=True)

    @app.route('/submit', methods=['POST'])
    def submit():
        # 获取表单中的文本数据
        business = request.form.get('business')
        fileType = request.form.get('fileType')
        # 获取表单中的文件数据
        dataFile = request.files.get('dataFile')
        if fileType == "数据标准检查结果模板上传":
            dataFile.save('file/static/统计模板.xlsx')
            flash("上传成功！")
            return redirect("/")
        elif fileType == "重要业务结果文件模板上传":
            dataFile.save('file/template/XXXX产品名称_4.0.1.xlsx')
            flash("上传成功！")
            return redirect("/")
        elif fileType == "自定义代码文件模板上传":
            dataFile.save('file/template/XXXX产品名称_4.0.1_自定义代码.xlsx')
            flash("上传成功！")
            return redirect("/")
        # 验证文件是否存在并且符合要求
        elif dataFile and dataFile.filename.endswith('.xlsx'):
            # 为文件生成一个安全的文件名
            filename = business + "_" + fileType + ".xlsx"
            # 将文件保存到服务器的uploads目录下
            if fileType in ["标准代码", "标准层模型", "数据元素"]:
                filename = fileType + ".xlsx"
            dataFile.save(os.path.join('file/standard', filename))
            # 返回一个成功的响应
            response = make_response(redirect("/"))
            flash(f'{filename}上传成功！')
            return response
        else:
            # 返回一个失败的响应
            flash('文件上传失败，请检查文件类型是否正确！')
            return redirect("/")

    @app.route("/modify_submit", methods=['POST'])
    def modify_submit():
        dataFile = request.files.get('mo_file')
        title = request.form.get('title')
        title.strip()
        title = title.split("\r")[0]
        print(title)
        new_title = title.rsplit(".", 1)[0] + "确认." + title.rsplit(".", 1)[1]
        file_path = os.path.join('file', 'confirm', new_title)
        dataFile.save(file_path)

        # time.sleep(1)
        # print(g.confirm_tuple)
        # flash("保存成功")
        # 使用flask.after_this_request装饰器来注册一个函数

        @flask.after_this_request
        def do_something(response):
            # 在这里执行一些操作，例如打印日志或者删除临时文件等
            print("Saved file successfully")
            # 重定向到confirm函数，并传递文件名参数
            return redirect(url_for('confirm', filename=file_path))

        return redirect("/second")
        # return redirect(url_for('confirm', filename=file_path))

    @app.route("/business_submit", methods=['POST'])
    def business_submit():
        business = request.form.get('business')
        version = request.form.get('version')
        folder_path = "file/input/" + business + '_' + version + "/"
        print(folder_path)
        check_and_create_folder(folder_path)
        check_and_create_folder("file/confirm")
        code_file = request.files.get("code_file")
        business_result_file = request.files.get("business_result_file")
        code_file_exists = (code_file.filename != '')
        business_result_file_exists = (business_result_file.filename != '')
        if code_file_exists:
            code_file.filename = business + '_' + version + "_" + "自定义代码.xlsx"
            code_file_path = os.path.join(folder_path, code_file.filename)
            code_file.save(code_file_path)
            code_check("file/standard/标准代码.xlsx", code_file_path)
        if business_result_file_exists:
            business_result_file.filename = business + '_' + version + "_" + "重要业务结果.xlsx"
            business_result_file_path = os.path.join(folder_path, business_result_file.filename)
            business_result_file.save(business_result_file_path)
            print(business_result_file_path, '开始datatool')
            sep_on_sheet(business_result_file_path)
        if code_file_exists or business_result_file_exists:
            message = code_file.filename + "  " + business_result_file.filename + "上传成功"
            flash(message=message)
        else:
            message = "上传失败"
            flash(message=message)

        return redirect("/third")

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8088)
