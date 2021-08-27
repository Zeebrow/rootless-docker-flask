from flask import Flask, Response, jsonify
import json, sys, os, getpass
app = Flask(__name__)

@app.route("/")
def indexhtml():
    return Response("Hello\n", mimetype="text/html")

@app.route("/sysinfo")
def sysinfo():
    return jsonify({
        "user-getpass": getpass.getuser(),
        "user-os.getuid": os.getuid(),
        "user-os.getgid": os.getgid(),
        "os.cwd": os.getcwd(),
        "os.path.expanduser": os.path.expanduser('~')
    })

@app.route("/health")
def health():
#    return json.dumps({
#        "name": "mysite.com",
#        "status": "ok"
#        })
    return jsonify(
        name="mysite",
        status="ok"
    )
