#  WhatsApp messaging client project
#  Developer console module
#  Written by Samyar Sadat Akhavi, 2023
#  
#  Project Information
#  Developer:        Samyar Sadat Akhavi
#  Start Date:       09/06/2023


# ------- Libraries and utils -------
import bleach
from flask import Blueprint, flash, redirect, request, abort
from modules.database import Agent, AnnouncementMessage, PhoneNumber, User, Role, Message, RedirectRule
from init import db, app
from msg_dsp_text import FLASH_MESSAGES
from utils.forms import AdminSysSettingsForm, DeveloperAddAnnouncementMessageForm
from utils.user_config import SecretVarsFile, UserConfigFile
from flask_security import hash_password, current_user
from flask_admin import BaseView, expose, AdminIndexView, Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin
from config import WORKING_DIR
from datetime import datetime


# ------- Blueprint init -------
dev_pages = Blueprint("dev_pages", __name__, template_folder="../templates", static_folder="../static")


# ------- Flask-Admin custom base views -------
def access_allowed():
    return (current_user.is_active and
            current_user.is_authenticated and
            current_user.has_role("developer"))


class MyBaseView(BaseView):
    def is_accessible(self):
        return access_allowed()
        
        
class MyModelView(ModelView):
    can_view_details = True
    create_modal = True
    edit_modal = True
    can_export = True
    can_set_page_size = True
    page_size = 50
    
    def is_accessible(self):
        return access_allowed()
        
        
class MyIndexView(AdminIndexView):
    def is_accessible(self):
        return access_allowed()
    
    @expose("/", methods=["POST", "GET"])
    def index(self):
        return self.render("admin/index.html")
        

class MyFileAdmin(FileAdmin):
    editable_extensions = ("py", "txt", "json", "env", "html", "css", "jinja", "po", "cfg", "pot")
    
    def is_accessible(self):
        return access_allowed()
    
    
# ------- Flask-Admin init -------
admin = Admin(app, name="Developer", index_view=MyIndexView(name="Home", url="/developer-console", endpoint="developer-console"), template_mode="bootstrap4", url="/developer-console")


# ------- Flask-Admin views -------
class SysSettingsView(MyBaseView):
    @expose("/", methods=["POST", "GET"])
    def index(self):
        form = AdminSysSettingsForm.new()
        config_file_form_map = {
            "ANALYTICS_PROPERTY_ID": "ga_property_id",
            "ANALYTICS_TAG_ID": "ga_tag_id",
            "SECURITY_EMAIL_SENDER": "security_mail_email",
            "SECURITY_EMAIL_SENDER_NAME": "security_mail_sender_name",
            "WAAPI_REQUEST_BASIC_AUTH_PASS_HASH": "waapi_callback_pass",
            "WAAPI_REQUEST_BASIC_AUTH_USER": "waapi_callback_user",
            "WAAPI_WHATSAPP_FROM_NUMBER": "waapi_send_phone_num",
            "WAAPI_REQUEST_PASSWORD": "waapi_callback_pass",
            "WAAPI_BASE_URL": "waapi_api_base_url",
            "WAAPI_API_KEY": "waapi_api_api_key",
            "MAILJET_API_KEY": "mailjet_api_key",
            "MAILJET_API_SECRET": "mailjet_api_secret",
            "MAX_CUSTOMERS_PER_DAY": "max_customers_per_day",
            "MAX_AGENTS_PER_CUSTOMER": "max_agents_per_customer",
            "MAX_FILE_UPLOAD_SIZE_MB": "max_file_upload_size_mb"
        }

        if request.method == "POST" and form.is_submitted():
            try:
                config_file = UserConfigFile.read()
                secrets_file = SecretVarsFile.read()
                
                for config in config_file.__dict__:
                    form_mapped = config_file_form_map.get(config)
                    
                    if form_mapped:
                        form_field = getattr(form, form_mapped).raw_data[0]
                    
                        if form_field:
                            if config == "WAAPI_REQUEST_BASIC_AUTH_PASS_HASH":
                                form_field = hash_password(form_field)
                                
                            elif (config == "MAX_CUSTOMERS_PER_DAY" or config == "MAX_AGENTS_PER_CUSTOMER" or config == "MAX_FILE_UPLOAD_SIZE_MB"):
                                form_field = int(form_field)
                            
                            setattr(config_file, config, form_field)
                        
                for config in secrets_file.__dict__:
                    form_mapped = config_file_form_map.get(config)
                    
                    if form_mapped:
                        form_field = getattr(form, form_mapped).raw_data[0]
                    
                        if form_field:
                            setattr(secrets_file, config, form_field)
                
                if not (config_file.write() and secrets_file.write()):
                    raise Exception
                
                flash(FLASH_MESSAGES.ADMIN_SYS_SETTINGS_UPDATE_SUCCESS, "success")
                return redirect(self.get_url("sys-settings.index"))
                
            except Exception:
                flash(FLASH_MESSAGES.ADMIN_SYS_SETTINGS_UPDATE_FAIL, "danger")
                return redirect(self.get_url("sys-settings.index"))

        return self.render("admin/system_settings.html", form=form)
    
    
class AnnouncementMessagesView(MyBaseView):
    @expose("/", methods=["POST", "GET"])
    def index(self):
        form = DeveloperAddAnnouncementMessageForm()
        
        if request.method == "POST" and form.validate_on_submit():
            to_db = AnnouncementMessage(message=form.message.data, level=form.level.data, duration=form.duration.data, start_time=datetime.now())
            db.session.add(to_db)
            db.session.commit()
            flash("Successfully added announcement message!", "success")
        
        current_messages = AnnouncementMessage.query.all()
        return self.render("admin/announce_msgs.html", form=form, current_messages=current_messages)
    
    @expose("/delete_announcement_message/<id>")
    def delete_announcement_message(self, id):
        message = AnnouncementMessage.query.get(bleach.clean(id))
        
        if message:
            db.session.delete(message)
            db.session.commit()
            flash("Successfully deleted announcement message!", "success")
            return redirect(self.get_url("announce-msgs.index"))
        
        abort(404)
    
    
# ------- View registry -------
admin.add_view(SysSettingsView(name="System Config", endpoint="sys-settings"))
admin.add_view(AnnouncementMessagesView(name="Announce. Msgs", endpoint="announce-msgs"))
admin.add_view(MyModelView(Message, db.session, category="Database"))
admin.add_view(MyModelView(RedirectRule, db.session, category="Database"))
admin.add_view(MyModelView(Agent, db.session, category="Database"))
admin.add_view(MyModelView(PhoneNumber, db.session, category="Database"))
admin.add_view(MyModelView(User, db.session, category="User Database"))
admin.add_view(MyModelView(Role, db.session, category="User Database"))
admin.add_view(MyFileAdmin(WORKING_DIR, endpoint="/manage-files/", name="Files"))
