import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

from pymaskinporten.config import load_config
from pymaskinporten.request_token import request_maskinporten_token

# Configure application
app = Flask(__name__)

# Load environment variables from .env file if it exists
load_dotenv()


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
def index():
    selected_env = None
    issuer_url = None
    config_error = None
    config = None

    try:
        config = load_config()
    except RuntimeError as e:
        config_error = str(e)

    if request.method == "POST":
        selected_env = request.form.get("environment")
        if selected_env == "prod":
            issuer_url = "https://maskinporten.no/token"
        elif selected_env == "test" or selected_env is None:
            issuer_url = "https://test.maskinporten.no/token"

    return render_template(
        "index.html",
        selected_env=selected_env,
        issuer_url=issuer_url,
        config=config,
        config_error=config_error,
    )


@app.route("/token")
def get_token():

    # reads ?env=test or ?env=prod
    env = request.args.get("env")

    if env is None:
        env = "test"

    try:
        access_token, expires_in = request_maskinporten_token(api_env=env)
        return jsonify({"access_token": access_token, "expires_in": expires_in})
    except Exception:
        app.logger.exception("Failed to request Maskinporten token")
        return jsonify({"error": "An internal error has occurred."}), 500


def main():
    debug_enabled = os.getenv("FLASK_DEBUG", "false").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )
    app.run(debug=debug_enabled, host="0.0.0.0")


if __name__ == "__main__":
    main()
