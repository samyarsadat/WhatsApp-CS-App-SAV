#  WhatsApp messaging client project
#  Admin management console module
#  Written by Samyar Sadat Akhavi, 2023
#  
#  Project Information
#  Developer:        Samyar Sadat Akhavi
#  Start Date:       09/06/2023


# ------- Libraries and utils -------
import bleach
from flask_security import auth_required, roles_required, hash_password
from flask import Blueprint, abort, render_template, redirect, url_for, request, flash
from config import AppConfig
from utils.forms import AdminNewRedirectRuleForm, AdminNewAgentForm
from msg_dsp_text import FLASH_MESSAGES
from utils.global_helpers import validate_e164_phone_num
from modules.database import PhoneNumber, RedirectRule, Agent
from init import db, debug_log, app
from datetime import datetime


# ------- Global variables -------
MANAGEMENT_PAGES_PREFIX = AppConfig.ADMIN_MANAGE_URL_PREFIX


# ------- Blueprint init -------
admin_pages = Blueprint("admin_pages", __name__, template_folder="../templates", static_folder="../static")


# ------- Page routes -------
@admin_pages.route("/")
def index():
    return redirect(url_for(".manage_redirects"))


@admin_pages.route(MANAGEMENT_PAGES_PREFIX + "/redirects", methods=["POST", "GET"])
@auth_required("session")
@roles_required("admin")
def manage_redirects():
    form = AdminNewRedirectRuleForm()
    agents = []
    phone_numbers = []
    
    for agent in Agent.query.all():
        agents.append((agent.id, agent.name))
        
    for number in PhoneNumber.query.all():
        if not Agent.query.filter_by(phone_number=number.number).first():
            phone_numbers.append((number.number, number.customer_id))
    
    form.redirect_to_agent.choices = agents
    form.redirect_phone_number.choices = phone_numbers
    
    if request.method == "POST" and form.validate_on_submit():
        if validate_e164_phone_num(form.redirect_phone_number.data):
            redirect_rule = RedirectRule(name=form.redirect_rule_name.data, phone_number=form.redirect_phone_number.data, agent_id=form.redirect_to_agent.data)
            redirect_rule_db = RedirectRule.query.filter_by(phone_number=redirect_rule.phone_number).filter_by(agent_id=redirect_rule.agent_id).first()
            redirect_rules = RedirectRule.query.filter_by(phone_number=redirect_rule.phone_number).all()
            agents_db = Agent.query.filter_by(phone_number=form.redirect_phone_number.data).first()
                
            if not redirect_rule_db:
                if redirect_rules:
                    if len(redirect_rules) >= AppConfig.MAX_AGENTS_PER_CUSTOMER:
                        flash(FLASH_MESSAGES.REDIRECT_RULE_AGENT_LIMIT_REACHED, "warning")
                        return redirect(url_for(".manage_redirects"))
                    
                if not agents_db:
                    db.session.add(redirect_rule)
                    db.session.commit()
                    debug_log.debug(f"Added new redirect rule: {[form.redirect_rule_name.data, form.redirect_phone_number.data, form.redirect_to_agent.data]}")
                    
                    flash(FLASH_MESSAGES.ADD_REDIRECT_RULE_SUCCESS, "success")
                    return redirect(url_for(".manage_redirects"))
                
                flash(FLASH_MESSAGES.REDIRECT_RULE_AGENT_UNABLE, "warning")
                return redirect(url_for(".manage_redirects"))
            
            flash(FLASH_MESSAGES.REDIRECT_RULE_ALREADY_EXIST, "warning")
            return redirect(url_for(".manage_redirects"))
        
        flash(FLASH_MESSAGES.INVALID_PHONE_NUMBER, "warning")
        return redirect(url_for(".manage_redirects"))
    
    rules = RedirectRule.query.all()
    return render_template("management/manage_redirects.html", form=form, rules=rules)


@admin_pages.route(MANAGEMENT_PAGES_PREFIX + "/agents", methods=["POST", "GET"])
@auth_required("session")
@roles_required("admin")
def manage_agents():
    form = AdminNewAgentForm()
    
    if request.method == "POST" and form.validate_on_submit():
        if form.agent_type.data == "phone":
            if form.agent_phone_number.data:
                if validate_e164_phone_num(form.agent_phone_number.data):
                    agent = Agent(name=form.agent_username.data, type=form.agent_type.data, phone_number=form.agent_phone_number.data, fs_user_id=None)
                    agent_db = Agent.query.filter_by(phone_number=form.agent_phone_number.data).first()
                    
                    if not agent_db:
                        db.session.add(agent)
                        db.session.commit()
                        
                        debug_log.debug(f"Added new agent: {[form.agent_type.data, form.agent_username.data, form.agent_phone_number.data]}")
                        
                        flash(FLASH_MESSAGES.AGENT_ADD_SUCCESS, "success")
                        return redirect(url_for(".manage_agents"))
                    
                    flash(FLASH_MESSAGES.AGENT_ALREADY_EXIST, "warning")
                    return redirect(url_for(".manage_agents"))
                        
            flash(FLASH_MESSAGES.INVALID_PHONE_NUMBER, "warning")
            return redirect(url_for(".manage_agents"))
            
        elif form.agent_type.data == "fs_user":
            if form.agent_email.data and form.agent_password.data: 
                datastore = app.security.datastore
                agent = Agent(name=form.agent_username.data, type=form.agent_type.data, phone_number=None, fs_user_id=None)
                agent_db = Agent.query.filter_by(name=form.agent_username.data).first()
                user_db = datastore.find_user(email=form.agent_email.data)
                user_db_name = datastore.find_user(username=form.agent_username.data)
                    
                if (not agent_db) and (not user_db) and (not user_db_name):
                    with app.app_context():
                        user = datastore.create_user(email=form.agent_email.data, password=hash_password(form.agent_password.data), username=form.agent_username.data, confirmed_at=datetime.now())
                        db.session.commit()
                        
                        user = datastore.find_user(email=form.agent_email.data)
                        agent.fs_user_id = user.id
                        
                        datastore.add_role_to_user(user, "agent")
                        db.session.add(agent)
                        db.session.commit()
                        
                        debug_log.debug(f"Added new agent: {[form.agent_type.data, form.agent_username.data, form.agent_email.data]}")
                        
                        flash(FLASH_MESSAGES.AGENT_ADD_SUCCESS, "success")
                        return redirect(url_for(".manage_agents"))
                        
                flash(FLASH_MESSAGES.AGENT_ALREADY_EXIST, "warning")
                return redirect(url_for(".manage_agents"))
        
            flash(FLASH_MESSAGES.INVALID_EMAIL_PASS, "warning")
            return redirect(url_for(".manage_agents"))
    
    agents = Agent.query.all()
    return render_template("management/manage_agents.html", form=form, agents=agents)


@admin_pages.route("/delete_agent/<id>")
@auth_required("session")
@roles_required("admin")
def delete_agent(id):
    id = bleach.clean(id)
    agent = Agent.query.get(id)
    
    if agent:
        redirect_rules = RedirectRule.query.filter_by(agent_id=agent.id).all()
        
        for rule in redirect_rules:
            db.session.delete(rule)
        
        if agent.type == "fs_user":
            user = app.security.datastore.find_user(id=agent.fs_user_id)
            
            if user:
                app.security.datastore.delete_user(user)
            
        db.session.delete(agent)
        db.session.commit()
        
        debug_log.debug(f"Successfully deleted agent and agent rules: [{id}]")
        return redirect(url_for(".manage_agents"))
    
    abort(404)
                
        
@admin_pages.route("/delete_rule/<id>")
@auth_required("session")
@roles_required("admin")
def delete_redirect_rule(id):
    id = bleach.clean(id)
    rule = RedirectRule.query.get(id)
    
    if rule:
        db.session.delete(rule)
        db.session.commit()
        
        debug_log.debug(f"Successfully deleted redirect rule: [{id}]")
        return redirect(url_for(".manage_redirects"))

    abort(404)