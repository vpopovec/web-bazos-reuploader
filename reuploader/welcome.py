from flask import Blueprint

from reuploader.helpers import *

bp = Blueprint('welcome', __name__)


@bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@bp.route("/contact", methods=["GET"])
def contact():
    return render_template("contact.html")
