import os

from pydantic import ValidationError

try:
    from dotenv import load_dotenv
    from flask import Flask, jsonify, render_template, request
except ImportError as e:
    raise ImportError(
        "The pymaskinporten-web demo app needs the web extra: "
        "pip install pymaskinporten[web]"
    ) from e

from pymaskinporten.config import load_config
from pymaskinporten.request_token import ISSUER_URLS, request_maskinporten_token

# Configure application
app = Flask(__name__)

# Load environment variables from .env file if it exists
load_dotenv()


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = "0"
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
    except ValidationError as e:
        # str(e) shows the start and end of each rejected value; for a key pasted
        # without its PEM armor lines that is key material, so list fields only
        config_error = "; ".join(
            f"{'.'.join(map(str, err['loc']))}: {err['msg']}" for err in e.errors()
        )

    if request.method == "POST":
        selected_env = request.form.get("environment")
        issuer_url = ISSUER_URLS.get(selected_env or "test")

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
    env = request.args.get("env") or "test"
    if env not in ISSUER_URLS:
        return jsonify({"error": "env must be 'test' or 'prod'."}), 400

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
    # /token hands out real tokens without auth, so stay local unless told otherwise
    host = os.getenv("FLASK_RUN_HOST", "127.0.0.1")
    app.run(debug=debug_enabled, host=host)


if __name__ == "__main__":
    main()
