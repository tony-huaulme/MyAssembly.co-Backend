from flask import redirect, url_for
from flask_dance.contrib.google import make_google_blueprint, google
from config import Config

blueprint = make_google_blueprint(
    client_id=Config.GOOGLE_CLIENT_ID,
    client_secret=Config.GOOGLE_CLIENT_SECRET,
    scope=["profile", "email"]
)

def index():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/plus/v1/people/me")
    assert resp.ok, resp.text
    return "You are {email} on Google".format(email=resp.json()["emails"][0]["value"])

google_blueprint = blueprint