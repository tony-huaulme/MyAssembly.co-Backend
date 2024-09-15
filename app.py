from flask import Flask, redirect, url_for
from config import Config
from auth import google_blueprint, index

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config['SECRET_KEY']

app.register_blueprint(google_blueprint, url_prefix="/login")

@app.route("/")
def home():
    return index()

if __name__ == "__main__":
    app.run()
