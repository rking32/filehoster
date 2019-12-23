from flask import Flask, send_file, request, jsonify
import io
import os
from pymongo import MongoClient
import sys
from datetime import datetime


if os.getenv("db"):
    client = MongoClient(os.getenv("db"))
else:
    print("No MongoDB found.\nExitting...")
    sys.exit()


db = client.users.files


# set these in your environment vars
# MUST
adminuser = os.getenv("adminuser")
adminpass = os.getenv("adminpass")


app = Flask(__name__)


@app.route("/")
def home():
    return """<title>Home Page</title>
Welcome to this file hosting server<br/><br/>
Click <a href=/upload>Here</a> to Upload a file<br>
After that simply go to <code>/download/filename</code>"""


@app.route("/download/")
def redirect():
    return """<title>Download File</title>Type your filename in the box below:<br/><br/>
  <form action="javascript:;" onsubmit="window.location = '/download/' + this.filename.value;">
    <input type="text" name="filename" id="filename">
    <button type=submit>
        ReDirect to Download
    </button>
  </form>"""


@app.route("/download/<filename>/")
def send(filename):
    file = db.find_one({"filename": filename})
    if file:
        filecl = io.BytesIO(file["data"])
        filecl.name = filename
        return send_file(filecl, attachment_filename=filename, as_attachment=True)
    else:
        return "<title>OOF</title>Error 404: File does not exist", 404


@app.route("/api/", methods=["POST"])
def api():
    try:
        file = request.files.get("file")
            if file is None or file.filename == "":
                return jsonify({'success': False, 'error': ValueError("Invalid or empty file")})
        data = file.read()
        if len(data) > 1024*1024*1024*10:
            return jsonify({'success': False, 'error': ValueError("Limit to filesize is 10 GiB")})
        db.insert_one({"filename": file.filename, "data": data}, bypass_document_validation=False)
        return jsonify({'success': True, 'error': None})
    except Exception as e:
        return jsonify({'success': False, 'error': e})


@app.route("/upload/")
def upload():
    file = request.files.get("img")
    if file is None or file.filename == "":
        return send_file("upload.html")
    data = file.read()
    if len(data) >= 1024*1024*1024*10:
        return "Sorry but 10 GiB limit per file", 405
    db.insert_one({"filename": file.filename, "data": data}, bypass_document_validation=False)
    return """<title>Done!</title>Saved Successfully<br/><br/>
<a href=/download/{}>Here</a> is your download link""".format(file.filename)


@app.route("/delete", methods=["DELETE"])
def delete():
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
        return "Access Denied", 405


app.run("0.0.0.0", port="8080")
