# from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session

from helpers import *
from main import get_my_ads, send_authentication, send_sms_code, get_ad_links, download_ad, delete_ad
from upload_ad import upload_ad

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure session for backend
bazos_session = requests.Session()

# Initialize dirs
make_init_folders()

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


def reupload(resp):
    user_messages = []
    ad_links = get_ad_links(resp)
    load_session_cookies(bazos_session, session["tel_num"])

    ads_to_upload = []
    for ad_link in ad_links:
        downloaded = download_ad(bazos_session, ad_link)
        if not downloaded:
            user_messages.append(f"Couldn't download ad number {get_id_from_link(ad_link)}")
            continue

        success = delete_ad(bazos_session, ad_link, session)

        if success:
            ads_to_upload.append(get_id_from_link(ad_link))
        if not success:
            user_messages.append(f"Couldn't remove ad number {get_id_from_link(ad_link)}")

    for ad_id in ads_to_upload:
        resp, ad_title = upload_ad(bazos_session, session, ad_id)
        success = 'SUCCESSFUL' if 'Inzerát bol vložený' in resp else 'FAILED'
        user_messages.append({"success": success, "text": f"UPLOADING OF {ad_title} {success}"})

    save_session(bazos_session, session['tel_num'])
    return render_template("ads.html", messages=user_messages)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        pass  # RENDER ADS MESSAGES AFTER REUPLOADING

    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        tel_num = request.form.get("tel-num")
        # ad_psw = request.form.get("ad-psw")
        err = validate_user_input(email, tel_num)
        if err:
            return apology(f"{err}")
        email = email.strip()
        tel_num = tel_num.strip().replace(' ', '')
        session["email"] = email
        session["tel_num"] = tel_num
        # session["ad_psw"] = ad_psw
        
        bazos_session = requests.Session()
        """ SETTING BKOD COOKIE WORKS """
        load_session_cookies(bazos_session, tel_num)
        
        try:
            resp = get_my_ads(bazos_session)
            if not already_logged_in(resp):
                send_authentication(bazos_session, session)

                save_session(bazos_session, session['tel_num'])  # EXTRA
                return redirect("/sms-confirm")
            save_session(bazos_session, session["tel_num"])
            return reupload(resp)
        
        except Exception as e:
            return apology(f"{e}")

    
    return render_template("login.html")

@app.route("/sms-confirm", methods=["GET", "POST"])
def sms_confirm():
    if request.method == "POST":
        sms_code = request.form.get("sms-code")
        try:
            load_session_cookies(bazos_session, session['tel_num'])

            resp = send_sms_code(bazos_session, sms_code, session['tel_num'])

            save_session(bazos_session, session['tel_num'])
            return reupload(resp)

        except Exception as e:
            return apology(f"{e}")
        
    
    return render_template("smsconfirm.html")


@app.route("/contact", methods=["GET"])
def contact():
    return render_template("contact.html")
