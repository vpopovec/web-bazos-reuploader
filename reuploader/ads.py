from reuploader.helpers import *
from flask import (
    Blueprint, current_app, render_template, session, redirect, url_for
)
from reuploader.main import get_ad_links, download_ad, delete_ad
from reuploader.upload_ad import upload_ad, ADS_DIR
from reuploader.db import get_db

bp = Blueprint('ads', __name__)


@bp.route('/result', methods=["GET", "POST"])
def result():
    try:
        user_id = session['user_id']
    except KeyError:
        return redirect(url_for('auth.login'))

    messages = get_db().execute('SELECT * FROM result WHERE user_id = ?', (user_id,)).fetchall()

    # cet = timezone('Europe/Bratislava')
    messages = [{'success': msg['success'], 'text': msg['message'],
                 'dt': msg['uploaded'].strftime("%d.%m.%Y %H:%M")} for msg in messages]

    return render_template("ads.html", messages=messages)


def reupload(resp):
    result_messages = []
    ad_links = get_ad_links(resp)
    b_session = current_app.config["B_SESSION"]

    ads_to_upload = []
    for ad_link in ad_links:
        ad_fpath = os.path.join(ROOT_DIR, ADS_DIR, get_id_from_link(ad_link))
        downloaded = download_ad(b_session, ad_link, ad_fpath)
        if not downloaded:
            result_messages.append({"success": 0, "text": f"Couldn't download ad number {get_id_from_link(ad_link)}"})
            continue

        success = delete_ad(b_session, ad_link)

        if success:
            ads_to_upload.append(get_id_from_link(ad_link))
        if not success:
            result_messages.append({"success": 0, "text": f"Couldn't remove ad number {get_id_from_link(ad_link)}"})

    for ad_id in ads_to_upload:
        ad_path = os.path.join(ROOT_DIR, ADS_DIR, ad_id)  # Maybe os.path.join() ?
        resp, ad_title = upload_ad(b_session, session, ad_path)
        success = 1 if 'Inzerát bol vložený' in resp else 0
        SUCCESS_MSG = {0: "FAILED", 1: "SUCCESSFUL"}
        result_messages.append({"success": success, "text": f"Uploading of {ad_title} {SUCCESS_MSG[success]}"})

    save_session(b_session, session['tel_num'])
    save_results_to_db(result_messages)
    return result_messages


def save_results_to_db(messages):
    db = get_db()
    try:
        user_id = session['user_id']
    except KeyError:
        user_id = db.execute(
            "SELECT id FROM user WHERE tel_num = ?", (session['tel_num'],)
        ).fetchone()['id']
        session['user_id'] = user_id

    for m in messages:
        db.execute(
            "INSERT INTO result (user_id, success, message) VALUES (?, ?, ?)",
            (user_id, m['success'], m['text'])
        )

    db.commit()
