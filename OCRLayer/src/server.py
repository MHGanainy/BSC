# Imports
import os, shutil, sys, threading, json
import awstextractwrapper as atw
from flask import Flask, flash, request, redirect, url_for, session, jsonify, Response
from werkzeug.utils import secure_filename

# Initialize Global Variables
UPLOAD_FOLDER = "./uploads"
ALLOWED_EXTENSIONS = {"pdf", "png", "jpeg"}
# Flask config
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = "super secret key"  # Subject to change


# Initialize Functions
# Check if filename extension is allowed
def allowed_file(filename):
    return "." in filename and filename.rsplit(
        ".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Clear UPLOAD_FOLDER upon calling
def clear_folder():
    folder = UPLOAD_FOLDER
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print("Failed to delete %s. Reason: %s" % (file_path, e))


# Flask Methods API config


#Welcome API
@app.route("/")
def welcome_api():
    return Response(json.dumps(atw.JobResponseQueue),  mimetype='application/json')

#Check Completion
@app.route("/check")
def check_complete():
    if atw.compareCount():
        return "OK"
    return "INPROGRESS"
#Welcome API
@app.route("/startjob")
def startjob():
    atw.startJobForAll()
    #Background Process
    b = threading.Thread(target=atw.isJobQComplete, args=())
    b.daemon = True
    b.start()
    return "All Jobs Started"


# UPLOAD Document API POST METHOD
@app.route("/", methods=["POST"])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if not os.path.exists(app.config["UPLOAD_FOLDER"]+"/"+filename):
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                atw.uploadS3Object(app.config["UPLOAD_FOLDER"],filename)
                return atw.startJob(filename)
            else:
                return "File Already Exists"
    else:
        return "WRONG PROTOCOL SHOULD BE 'POST'"
    
# Initialize Main Function
if __name__ == "__main__":
    clear_folder()
    # atw.clear_bucket()
    #Server Process
    app.run(host="0.0.0.0")