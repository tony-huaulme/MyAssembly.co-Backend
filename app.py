from flask import Flask
from config import Config
from routes.file import handle_file
from routes.user import get_users, add_user
from routes.auth import google_blueprint, index

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config['SECRET_KEY']

app.register_blueprint(google_blueprint, url_prefix="/login")

@app.route("/")
def home():
    return index()

app.add_url_rule('/files/<path:filename>', view_func=handle_file, methods=['GET', 'POST', 'DELETE'])
app.add_url_rule('/users', view_func=get_users, methods=['GET'])
app.add_url_rule('/users', view_func=add_user, methods=['POST'])

if __name__ == "__main__":
    app.run()
