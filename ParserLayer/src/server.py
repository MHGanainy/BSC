# Import statments
from flask import Flask, flash, request, redirect, url_for, session, jsonify, Response
import json, threading, shutil, os
import awscontroller as ac

# Flask config
app = Flask(__name__)
app.secret_key = "super secret key"  # Subject to change

# Helper Functions
def clear_parsedDocs():
    path_to_folder = "./parsedDocs"
    list_dir = os.listdir(path_to_folder)
    for filename in list_dir:
        file_path = os.path.join(path_to_folder, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)

#Welcome API
@app.route("/")
def welcome_api():
    return "NER LAYER"

#Recieve JSON API
@app.route("/submit", methods=['POST'])
def get_ocr():
    response = request.get_json(force=True)
    json_data = json.loads(response)
    ac.JSONQueue.append(json_data)
    return "Success"
    
    

# Initialize Main Function
if __name__ == "__main__":
    #Clear ParsedDocs Folder
    clear_parsedDocs()
    #Start Multithreaded Process
    b = threading.Thread(target=ac.monitorQueue, args=())
    b.daemon = True
    b.start()
    #Server Process
    app.run(host="0.0.0.0",threaded=True)