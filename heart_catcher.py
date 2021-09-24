from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Welcome to the heart catcher application</p>"