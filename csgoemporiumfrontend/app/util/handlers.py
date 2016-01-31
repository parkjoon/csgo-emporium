import json, logging

from flask import request, g, redirect
from psycopg2 import OperationalError

from emporium import app
from database import Cursor

from helpers.user import get_user_info

from util.sessions import Session
from util.errors import ResponseException, GenericError
from util.responses import APIResponse

log = logging.getLogger(__name__)

@app.context_processor
def app_context_processor():
    return {
        "user": get_user_info(g.user)
    }

@app.template_filter("jsonify")
def jsonify_filter(x):
    return json.dumps(x)

@app.before_request
def app_before_request():
    if '/static/' in request.path:
        return

    # Load session if it exists
    g.session = Session()
    if g.session.new():
        g.session["ip"] = request.remote_addr
    elif g.session["ip"] != request.remote_addr:
        g.session.end()
        return redirect("/")

    g.user = None
    g.group = "normal"

    # Set a user for testing
    if app.config.get("TESTING"):
        if 'FAKE_USER' in request.headers:
            log.debug("TESTING: Faking user %s", request.headers.get("FAKE_USER"))
            g.user = int(request.headers.get("FAKE_USER"))
            g.group = "normal"
        if 'FAKE_GROUP' in request.headers:
            log.debug("TESTING: Faking group %s", request.headers.get("FAKE_GROUP"))
            g.group = request.headers.get("FAKE_GROUP")
    else:
        # Set uid
        g.user = g.session.get("u")
        g.group = g.session.get("g")

    # Setup DB transaction
    g.cursor = Cursor()

@app.after_request
def app_after_request(response):
    if '/static/' in request.path:
        return response

    # Update the session if applicable
    if g.user:
        g.session["g"] = g.group
        g.session["u"] = g.user

        # Save session if it changed
        g.session.save(response)
    else:
        g.session.end()

    g.cursor.close()
    return response

@app.errorhandler(ResponseException)
def app_response_error(err):
    return err.to_response()

