from . import app, webapp
import io
from datetime import datetime


db = app.db


@app.route("/")
def home():
    return app.render_html("filehoster/htmlpages/home.html")


@app.route("/download/")
def redirect():
    return app.render_html("filehoster/htmlpages/download.html")


@app.route("/download/<filename>/")
def send(filename):
    file = db.find_one({"filename": filename})
    if file:
        filecl = io.BytesIO(file["data"])
        filecl.name = filename
        return app.send(filecl, attachment_filename=filename, as_attachment=True)
    else:
        return "<title>OOF</title>Error 404: File does not exist", 404


@app.route("/api/<requestform>", methods=["POST"])
def api():
    try:
        request = app.get_requests()
        file = request.files.get("file")
        if file is None or file.filename == "":
            return app.json({'success': False, 'error': str(ValueError("Invalid or empty file"))})
        data = file.read()
        if len(data) > 1024*1024*1024*10:
            return app.json({'success': False, 'error': str(ValueError("Limit to filesize is 10 GiB"))})
        db.insert_one({"filename": file.filename, "data": data}, bypass_document_validation=False)
        return app.json({'success': True, 'error': None})
    except Exception as e:
        return app.json({'success': False, 'error': str(e)})


@app.route("/upload/", methods=["GET", "POST"])
def upload():
    request = app.get_requests()
    file = request.files.get("img")
    if file is None or file.filename == "":
        return app.render_html("filehoster/htmlpages/upload.html")
    data = file.read()
    if len(data) >= 1024*1024*1024*10:
        return "Sorry but 10 GiB limit per file", 403
    db.insert_one({"filename": file.filename, "data": data}, bypass_document_validation=False)
    return app.render_html("filehoster/htmlpages/uploadcom.html").format(file.filename)


@app.route("/delete", methods=["DELETE"])
def delete():
    adminuser, adminpass = app.get_creds()
    request = app.get_requests()
    filename = request.args.get("file")
    user = request.args.get("user")
    password = request.args.get("pass")
    if user == adminuser and password == adminpass:
        start = datetime.now()
        db.delete_many({"filename": filename})
        end = datetime.now()
        ms = (end - start).microseconds / 1000
        return "Deleted {} within {}ms".format(str(filename), ms), 201
    else:
        return "Access Denied", 403


webapp.start()
while True:
    try:
        pass
    except KeyboardInterrupt:
        webapp.terminate()
        webapp.join()
        break
