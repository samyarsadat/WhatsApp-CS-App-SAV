#  WhatsApp messaging client project
#  Main application file
#  Written by Samyar Sadat Akhavi, 2023
#  
#  Project Information
#  Developer:        Samyar Sadat Akhavi
#  Start Date:       09/06/2023


# ------- Libraries, utils, and modules -------
import os
import bleach
import jinja2
import werkzeug
from dotenv import load_dotenv
from flask import abort, redirect, render_template, request, session, flash, url_for
from flask_security import auth_required, current_user, hash_password, Security, roles_required
from config import AppConfig, USER_SECRETS_ENV_FILE
from flask_babel import get_locale
from init import app, cache, db, log, debug_log, socketio
from modules.database import Agent, AnnouncementMessage, RedirectRule, database, PhoneNumber, user_datastore
from modules.admin import admin_pages
from modules.messaging import messaging
from modules.dev_panel import dev_pages
from modules.multiserver import multi_server
from utils.email import SecurityMailUtil
from utils.global_helpers import validate_e164_phone_num, get_cid_phone_num, get_phone_num_cid, get_display_name_cid
from utils.google_analytics import Analytics
from msg_dsp_text import UI_ELEMENTS_TEXT, FLASH_MESSAGES
from datetime import datetime, timedelta
from utils.forms import AdminNewRedirectRuleForm, AdminChangeDisplayNameForm


# ------- Global variables -------
SUPPORTED_LANGS = AppConfig.SUPPORTED_LANGS
RENDER_CACHE_TIMEOUT = AppConfig.RENDER_CACHE_TIMEOUT
PROGRAM_FIRST_REQ = True


# ------- Jinja env global objects -------
app.jinja_env.globals["get_locale"] = get_locale
app.jinja_env.globals["len"] = len
app.jinja_env.globals["get_cid_phone_num"] = get_cid_phone_num
app.jinja_env.globals["get_phone_num_cid"] = get_phone_num_cid
app.jinja_env.globals["Agent_db"] = Agent
app.jinja_env.globals["SUPPORTED_LANGS"] = SUPPORTED_LANGS
app.jinja_env.globals["ENABLE_ANALYTICS"] = AppConfig.ENABLE_ANALYTICS
app.jinja_env.globals["ANALYTICS_TAG_ID"] = AppConfig.ANALYTICS_TAG_ID
app.jinja_env.globals["RENDER_CACHE_TIMEOUT"] = RENDER_CACHE_TIMEOUT
app.jinja_env.globals["WEBSITE_DISPLAY_NAME"] = AppConfig.WEBSITE_DISPLAY_NAME
app.jinja_env.globals["WEBSITE_FOOTER_LOGO"] = AppConfig.WEBSITE_FOOTER_LOGO
app.jinja_env.globals["WEBSITE_NAV_LOGO"] = AppConfig.WEBSITE_NAV_LOGO
app.jinja_env.globals["WEBSITE_FAVICON"] = AppConfig.WEBSITE_FAVICON
app.jinja_env.globals["UI_ELEMENTS_TEXT"] = UI_ELEMENTS_TEXT
app.jinja_env.globals["MAX_FILE_UPLOAD_SIZE_BYTES"] = AppConfig.MAX_CONTENT_LENGTH
app.jinja_env.globals["HTTP_SCHEME"] = AppConfig.HTTP_SCHEME
app.jinja_env.globals["ALLOWED_FILE_EXTENSIONS"] = AppConfig.ALLOWED_FILE_EXTENSIONS
app.jinja_env.globals["MULTISERVER_SERVERS_LIST"] = AppConfig.MULTISERVER_SERVERS_LIST
app.jinja_env.globals["PROGRAM_VERSION"] = AppConfig.PROGRAM_VERSION


# ------- Blueprint registry -------
app.register_blueprint(admin_pages, url_prefix="/admin")
app.register_blueprint(dev_pages, url_prefix="/developer-console")
app.register_blueprint(database)
app.register_blueprint(messaging)
app.register_blueprint(multi_server)


# ------- Flask Security init -------
app.security = Security(app, user_datastore, mail_util_cls=SecurityMailUtil)


# ------- Locale selector -------
@app.route("/set-lang/<lang>", methods=["POST"])
def set_lang(lang):
    if lang in SUPPORTED_LANGS:
        debug_log.debug(f"[{request.remote_addr}] Changed language to [{lang}]")
        session["lang"] = lang
        return redirect(request.referrer)

    abort(500)


# ------- Error handlers -------
@app.errorhandler(werkzeug.exceptions.NotFound)
@cache.cached(timeout=RENDER_CACHE_TIMEOUT)
def error404(error):
    log.info(f"[{request.remote_addr}] Sent a [{request.method}] request to [{request.url}] that resulted in a [404 Error]")
    return render_template("http_error_master.html", error_code="404"), 404


@app.errorhandler(werkzeug.exceptions.InternalServerError)
@cache.cached(timeout=RENDER_CACHE_TIMEOUT)
def error500(error):
    log.error(f"[{request.remote_addr}] Sent a [{request.method}] request to [{request.url}] that resulted in a [500 Error]")
    return render_template("http_error_master.html", error_code="500"), 500


@app.errorhandler(werkzeug.exceptions.MethodNotAllowed)
@cache.cached(timeout=RENDER_CACHE_TIMEOUT)
def error405(error):
    log.info(f"[{request.remote_addr}] Sent a [{request.method}] request to [{request.url}] that resulted in a [405 Error]")
    return render_template("http_error_master.html", error_code="405"), 405


@app.errorhandler(jinja2.exceptions.TemplateNotFound)
@cache.cached(timeout=RENDER_CACHE_TIMEOUT)
def template_error(error):
    log.critical(f"[{request.remote_addr}] Sent a [{request.method}] request to [{request.url}] that resulted in a [500 Template Error]")
    return render_template("http_error_master.html", error_code="500"), 500


# ------- Before request -------
@app.before_request
def create_security():
    global PROGRAM_FIRST_REQ
    
    if PROGRAM_FIRST_REQ:
        datastore = app.security.datastore
        
        datastore.find_or_create_role("developer", description="Developer")
        datastore.find_or_create_role("admin", description="Administrator")
        datastore.find_or_create_role("agent", description="Agent")
        db.session.commit()

        with app.app_context():
            if not datastore.find_user(id=1):
                datastore.create_user(email=AppConfig.ADMIN_USER_DEFAULT_MAIL, password=hash_password(AppConfig.ADMIN_USER_DEFAULT_PASS), username=AppConfig.ADMIN_USER_DEFAULT_USER, confirmed_at=datetime.now())
                db.session.commit()
                
            if not datastore.find_user(id=2):
                datastore.create_user(email=AppConfig.DEV_USER_DEFAULT_MAIL, password=hash_password(AppConfig.DEV_USER_DEFAULT_PASS), username=AppConfig.DEV_USER_DEFAULT_USER, confirmed_at=datetime.now())
                db.session.commit()
        
        user = datastore.find_user(id=1)    
        if not user.has_role("admin"):
            datastore.add_role_to_user(user, "admin")
            datastore.add_role_to_user(user, "agent")
            db.session.commit()
            
        user = datastore.find_user(id=2)    
        if not user.has_role("developer"):
            datastore.add_role_to_user(user, "developer")
            datastore.add_role_to_user(user, "admin")
            datastore.add_role_to_user(user, "agent")
            db.session.commit()
            
        PROGRAM_FIRST_REQ = False
    

@app.before_request
def maintenance_mode():
    if (os.getenv("ENABLE_MAINTENANCE") == "True") and (not request.path.startswith("/account/")) and (not (current_user.is_authenticated and current_user.has_role("admin"))) and (not request.path.startswith("/static/")):
        abort(503)
    

@app.before_request
def remove_www():
    if "://www." in request.url.lower():
        log.info(f"[{request.remote_addr}] Sent a request with [www.]")

        request_url = request.url.lower()
        return redirect(request_url.replace("www.", ""))


@app.before_request
def log_request():
    debug_log.debug(f"[{request.remote_addr}] Sent a [{request.method}] request to [{request.url}]")
    log.info(f"[{request.remote_addr}] Sent a [{request.method}] request to [{request.url}]")
    

@app.before_request
def update_userset_settings():
    if not (request.path.startswith("/static/") or request.path.startswith("/api/")):
        debug_log.debug(f"Updated user settings from JSON file.")
        load_dotenv(USER_SECRETS_ENV_FILE, override=True)
        AppConfig.update_user_settings()
        
        
@app.before_request
def clear_announcement_messages():
    msgs = AnnouncementMessage.query.all()
    
    for msg in msgs:
        if msg.duration != "inf":
            msg_dur_mx = msg.duration.split("-")[1]
            msg_dur_num = int(msg.duration.split("-")[0])
            tdelta = None
            
            if msg_dur_mx == "mt":
                tdelta = msg.start_time + timedelta(minutes=msg_dur_num)
            
            elif msg_dur_mx == "hr":
                tdelta = msg.start_time + timedelta(hours=msg_dur_num)
                
            elif msg_dur_mx == "wk":
                tdelta = msg.start_time + timedelta(weeks=msg_dur_num)
            
            if tdelta and tdelta <= datetime.now():
                debug_log.debug(f"Clearing announcement message as [{msg.duration}] duration is over. [{msg.id}: {msg.message}]")
                db.session.delete(msg)
            
    db.session.commit()


# ------- Page routes -------
@app.route("/")
@auth_required("session")
def index():
    user_id = current_user.id 
    agent = db.session.query(Agent).filter_by(type="fs_user").filter_by(fs_user_id=user_id).first()
    redirect_rules = []
    
    if agent:
        redirect_rules = db.session.query(RedirectRule).filter_by(agent_id=agent.id).all()
    
    phone_nums = []
        
    if current_user.has_role("admin"):
        phones = PhoneNumber.query.all()
        
        for num in phones:
            phone_nums.append(num.number)
            
    else:
        for rule in redirect_rules:
            phone_nums.append(rule.phone_number)
                
    announcement_messages = AnnouncementMessage.query.all()
    return render_template("index.html", phone_number="NO_CHAT_PAGE", phone_nums=phone_nums, customer_id="NO_CHAT_PAGE", announcement_messages=announcement_messages)


@app.route("/msgs/<customer_id>", methods=["POST", "GET"])
@auth_required("session")
def index_msgs(customer_id):
    phone_number = get_phone_num_cid(bleach.clean(customer_id))
    
    form = AdminNewRedirectRuleForm()
    form2 = AdminChangeDisplayNameForm()
    agents = []
    phone_numbers = []
    
    for agent in Agent.query.all():
        agents.append((agent.id, agent.name))
            
    for number in PhoneNumber.query.all():
        if not Agent.query.filter_by(phone_number=number.number).first():    
            phone_numbers.append((number.number, number.customer_id))
    
    form.redirect_to_agent.choices = agents
    form.redirect_phone_number.choices = phone_numbers
    form2.customer.choices = phone_numbers
    
    form_return = redirect(url_for(".index_msgs", customer_id=customer_id))
    
    if request.method == "POST" and form2.validate_on_submit():
        if current_user.has_role("admin"):
            if validate_e164_phone_num(form2.customer.data):
                customer = PhoneNumber.query.filter_by(number=form2.customer.data).first()
                customer_new = PhoneNumber.query.filter_by(display_name=form2.new_display_name.data.lower()).first()
                
                if customer:
                    if not customer_new:
                        customer.display_name = form2.new_display_name.data.lower()
                        db.session.commit()
                        
                        flash(FLASH_MESSAGES.RENAME_CUSTOMER_SUCCESS, "success")
                        return form_return
                    
                    flash(FLASH_MESSAGES.RENAME_NAME_EXIST, "warning")
                    return form_return
                
                flash(FLASH_MESSAGES.INVALID_PHONE_NUMBER, "warning")
                return form_return
            
            flash(FLASH_MESSAGES.INVALID_PHONE_NUMBER, "warning")
            return form_return
        
        abort(401)
    
    if request.method == "POST" and form.validate_on_submit():
        if current_user.has_role("admin"):
            if validate_e164_phone_num(form.redirect_phone_number.data):
                redirect_rule = RedirectRule(name=form.redirect_rule_name.data, phone_number=form.redirect_phone_number.data, agent_id=form.redirect_to_agent.data)
                redirect_rule_db = RedirectRule.query.filter_by(phone_number=redirect_rule.phone_number).filter_by(agent_id=redirect_rule.agent_id).first()
                redirect_rules = RedirectRule.query.filter_by(phone_number=redirect_rule.phone_number).all()
                agents_db = Agent.query.filter_by(phone_number=form.redirect_phone_number.data).first()
                
                if not redirect_rule_db:
                    if redirect_rules:
                        if len(redirect_rules) >= AppConfig.MAX_AGENTS_PER_CUSTOMER:
                            flash(FLASH_MESSAGES.REDIRECT_RULE_AGENT_LIMIT_REACHED, "warning")
                            return form_return
                            
                    if not agents_db:
                        db.session.add(redirect_rule)
                        db.session.commit()
                        debug_log.debug(f"Added new redirect rule: {[form.redirect_rule_name.data, form.redirect_phone_number.data, form.redirect_to_agent.data]}")
                        
                        flash(FLASH_MESSAGES.ADD_REDIRECT_RULE_SUCCESS, "success")
                        return form_return
                    
                    flash(FLASH_MESSAGES.REDIRECT_RULE_AGENT_UNABLE, "warning")
                    return form_return
                
                flash(FLASH_MESSAGES.REDIRECT_RULE_ALREADY_EXIST, "warning")
                return form_return
            
            flash(FLASH_MESSAGES.INVALID_PHONE_NUMBER, "warning")
            return form_return
        
        abort(401)
    
    if phone_number:
        user_id = current_user.id 
        agent = db.session.query(Agent).filter_by(type="fs_user").filter_by(fs_user_id=user_id).first()
        redirect_rules = []
    
        if agent:
            redirect_rules = db.session.query(RedirectRule).filter_by(agent_id=agent.id).all()
        
        rule_avail = False
        phone_nums = []
        
        if current_user.has_role("admin"):
            phones = PhoneNumber.query.all()
            
            for num in phones:
                phone_nums.append(num.number)
        
        for rule in redirect_rules:
            if agent and rule.agent_id == agent.id:
                if not current_user.has_role("admin"):
                    phone_nums.append(rule.phone_number)
                    
                rule_avail = True
                
        if rule_avail or current_user.has_role("admin"):
            pn_database = PhoneNumber.query.filter_by(number=phone_number).first()
            
            if pn_database:
                pn_database.unread_msgs = 0
                db.session.commit()
                
            form.redirect_phone_number.default = phone_number
            form.process()
            
            form2.customer.default = phone_number
            form2.process()
            
            redirect_rules = RedirectRule.query.filter_by(phone_number=phone_number).all()
            announcement_messages = AnnouncementMessage.query.all()
            return render_template("index.html", phone_number=phone_number, phone_nums=phone_nums, form=form, form2=form2, customer_id=customer_id, redirect_rules=redirect_rules, display_name=get_display_name_cid(customer_id), announcement_messages=announcement_messages)
    
    debug_log.debug(f"[{request.remote_addr}] Attempted to open chat page for a number that is not in their redirects list. [{phone_number}]")
    abort(404)
    
    
@app.route("/msgs/all_read/<customer_id>")
@auth_required("session")
def index_msgs_set_read(customer_id):
    phone_number = get_phone_num_cid(bleach.clean(customer_id))
    
    if phone_number:
        user_id = current_user.id 
        agent = db.session.query(Agent).filter_by(type="fs_user").filter_by(fs_user_id=user_id).first()
        redirect_rules = []
    
        if agent:
            redirect_rules = db.session.query(RedirectRule).filter_by(agent_id=agent.id).all()
        
        rule_avail = False
        
        for rule in redirect_rules:
            if agent and rule.agent_id == agent.id:
                rule_avail = True
                
        if rule_avail or current_user.has_role("admin"):
            pn_database = PhoneNumber.query.filter_by(number=phone_number).first()
            
            if pn_database:
                pn_database.unread_msgs = 0
                db.session.commit()
            
            return "OK", 200
    
    debug_log.debug(f"[{request.remote_addr}] Attempted to set read status for a chat page that is not in their redirects list. [{phone_number}]")
    abort(404)
    
    
@app.route("/msgs/delete_redirects/<customer_id>")
@auth_required("session")
@roles_required("admin")
def delete_all_redirects_customer(customer_id):
    phone_number = get_phone_num_cid(bleach.clean(customer_id))
    customer = PhoneNumber.query.filter_by(number=phone_number)
    
    if customer:
        redirect_rules = RedirectRule.query.filter_by(phone_number=phone_number).all()
        
        for rule in redirect_rules:
            db.session.delete(rule)

        db.session.commit()
        
        debug_log.debug(f"Successfully deleted all redirect rules for: [{customer_id}]")
        return redirect(url_for(".index_msgs", customer_id=customer_id))
    
    abort(404)


# ------- Running the app -------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        
    socketio.run(app)

# ---- For production ----
def create_app():
    with app.app_context():
        db.create_all()
        
    return app