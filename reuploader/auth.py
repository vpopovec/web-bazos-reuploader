import traceback

from flask import (
    Blueprint, flash, redirect, request, session, url_for
)

from reuploader.helpers import *
from flask import current_app
from reuploader.main import get_my_ads, send_authentication, send_sms_code
from reuploader.ads import reupload
from reuploader.db import get_db

bp = Blueprint('auth', __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email").strip()
        tel_num = request.form.get("tel-num").strip().replace(' ', '')

        err = validate_user_input(email, tel_num)
        if err:
            return apology(f"{err}")

        session["email"] = email
        session["tel_num"] = tel_num

        b_session = current_app.config['B_SESSION']
        load_session_cookies(b_session, tel_num)

        try:
            ads_resp = get_my_ads(b_session)
            if not already_logged_in(ads_resp):
                send_authentication(b_session, session)

                # save_session(b_session, session['tel_num'])  # EXTRA
                return redirect("/sms-confirm")
            save_session(b_session, session["tel_num"])

            reupload(ads_resp)
            return redirect(url_for('ads.result'))

        except Exception as e:
            traceback.print_exc()
            return apology(f"{e=} {traceback.print_exc()}")

    return render_template("login.html")


@bp.route("/sms-confirm", methods=["GET", "POST"])
def sms_confirm():
    if request.method == "POST":
        # TODO: Implement code length checking (helpers)
        sms_code = request.form.get("sms-code")
        try:
            b_session = current_app.config["B_SESSION"]
            resp = send_sms_code(b_session, sms_code, session['tel_num'])
            # save user to DB
            save_user_to_db()

            save_session(b_session, session['tel_num'])
            reupload(resp)
            return redirect(url_for('ads.result'))

        except Exception as e:
            traceback.print_exc()
            return apology(f"{e}")

    return render_template("smsconfirm.html")


def save_user_to_db():
    db = get_db()
    try:
        db.execute(
            "INSERT INTO user (email, tel_num) VALUES (?, ?)",
            (session['email'], session['tel_num'])
        )
        db.commit()
    except db.IntegrityError:
        error = f"User under {session['tel_num']} number is already registered"

    user = db.execute(
        'SELECT * FROM user WHERE tel_num = ?', (session['tel_num'],)
    ).fetchone()
    session['user_id'] = user['id']
