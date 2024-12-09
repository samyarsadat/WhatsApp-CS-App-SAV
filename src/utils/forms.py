#  WhatsApp messaging client project
#  WTForms form models file
#  Written by Samyar Sadat Akhavi, 2023
#  
#  Project Information
#  Developer:        Samyar Sadat Akhavi
#  Start Date:       09/06/2023


# ------- Libraries and utils -------
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TelField, PasswordField, EmailField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, Optional
from flask_security.forms import username_validator
from config import AppConfig
from msg_dsp_text import ADMIN_CHANGE_DISPLAY_NAME_FORM_TEXT, ADMIN_SYS_SETTINGS_FORM_TEXT, ADMIN_NEW_AGENT_FORM_TEXT, ADMIN_NEW_REDIRECT_FORM_TEXT, DEVELOPER_ADD_ANNOUNCEMENT_MESSAGE_FORM_TEXT


# ------- WTForms classes -------
# ---- Admin system settings form ----
class AdminSysSettingsForm(FlaskForm):
    waapi_callback_user = StringField(ADMIN_SYS_SETTINGS_FORM_TEXT.waapi_callback_user)
    waapi_callback_pass = PasswordField(ADMIN_SYS_SETTINGS_FORM_TEXT.waapi_callback_pass)
    waapi_send_phone_num = TelField(ADMIN_SYS_SETTINGS_FORM_TEXT.waapi_send_phone_num)
    waapi_api_base_url = StringField(ADMIN_SYS_SETTINGS_FORM_TEXT.waapi_api_base_url)
    waapi_api_api_key = StringField(ADMIN_SYS_SETTINGS_FORM_TEXT.waapi_api_api_key)
    mailjet_api_key = StringField(ADMIN_SYS_SETTINGS_FORM_TEXT.mailjet_api_key)
    mailjet_api_secret = StringField(ADMIN_SYS_SETTINGS_FORM_TEXT.mailjet_api_secret)
    security_mail_email = EmailField(ADMIN_SYS_SETTINGS_FORM_TEXT.security_mail_email)
    security_mail_sender_name = StringField(ADMIN_SYS_SETTINGS_FORM_TEXT.security_mail_sender_name)
    ga_tag_id = StringField(ADMIN_SYS_SETTINGS_FORM_TEXT.ga_tag_id)
    ga_property_id = StringField(ADMIN_SYS_SETTINGS_FORM_TEXT.ga_property_id)
    max_customers_per_day = IntegerField(ADMIN_SYS_SETTINGS_FORM_TEXT.max_customers_per_day)
    max_agents_per_customer = IntegerField(ADMIN_SYS_SETTINGS_FORM_TEXT.max_agents_per_customer)
    max_file_upload_size_mb = IntegerField(ADMIN_SYS_SETTINGS_FORM_TEXT.max_file_upload_size_mb)
    submit = SubmitField(ADMIN_SYS_SETTINGS_FORM_TEXT.submit)
    
    @classmethod
    def new(cls) -> "AdminSysSettingsForm":
        form = cls()
        AppConfig.update_user_settings()
        
        form.waapi_callback_user.default = AppConfig.WAAPI_REQUEST_BASIC_AUTH_USER
        form.waapi_send_phone_num.default = AppConfig.WAAPI_WHATSAPP_FROM_NUMBER
        form.waapi_api_base_url.default = AppConfig.WAAPI_BASE_URL
        form.waapi_api_api_key.default = AppConfig.WAAPI_API_KEY
        form.mailjet_api_key.default = AppConfig.MAILJET_API_KEY
        form.mailjet_api_secret.default = AppConfig.MAILJET_API_SECRET
        form.security_mail_email.default = AppConfig.SECURITY_EMAIL_SENDER
        form.security_mail_sender_name.default = AppConfig.SECURITY_EMAIL_SENDER_NAME
        form.ga_tag_id.default = AppConfig.ANALYTICS_TAG_ID
        form.ga_property_id.default = AppConfig.ANALYTICS_PROPERTY_ID
        form.max_customers_per_day.default = AppConfig.MAX_CUSTOMERS_PER_DAY
        form.max_agents_per_customer.default = AppConfig.MAX_AGENTS_PER_CUSTOMER
        form.max_file_upload_size_mb.default = AppConfig.MAX_CONTENT_LENGTH / 1000 / 1000
        form.process()
        
        return form
    
    
# ---- Admin new redirect rule form ----
class AdminNewRedirectRuleForm(FlaskForm):
    redirect_rule_name = StringField(ADMIN_NEW_REDIRECT_FORM_TEXT.redirect_rule_name, validators=[DataRequired()])
    redirect_phone_number = SelectField(ADMIN_NEW_REDIRECT_FORM_TEXT.redirect_phone_number, validators=[DataRequired()])
    redirect_to_agent = SelectField(ADMIN_NEW_REDIRECT_FORM_TEXT.redirect_to_agent, validators=[DataRequired()])
    submit = SubmitField(ADMIN_NEW_REDIRECT_FORM_TEXT.submit)
    
    
# ---- Admin new agent form ----
class AdminNewAgentForm(FlaskForm):
    agent_username = StringField(ADMIN_NEW_AGENT_FORM_TEXT.agent_username, validators=[DataRequired(), username_validator])
    agent_phone_number = TelField(ADMIN_NEW_AGENT_FORM_TEXT.agent_phone_number)
    agent_type = SelectField(ADMIN_NEW_AGENT_FORM_TEXT.agent_type, validators=[DataRequired()], choices=AppConfig.ADD_AGENT_FORM_TYPE_OPTS)
    agent_email = EmailField(ADMIN_NEW_AGENT_FORM_TEXT.agent_email, validators=[Optional(), Email()])
    agent_password = PasswordField(ADMIN_NEW_AGENT_FORM_TEXT.agent_password)
    submit = SubmitField(ADMIN_NEW_AGENT_FORM_TEXT.submit)
    

# ---- Admin change display name form ----
class AdminChangeDisplayNameForm(FlaskForm):
    new_display_name = StringField(ADMIN_CHANGE_DISPLAY_NAME_FORM_TEXT.new_display_name, validators=[DataRequired()])
    customer = SelectField(ADMIN_CHANGE_DISPLAY_NAME_FORM_TEXT.customer, validators=[DataRequired()])
    submit = SubmitField(ADMIN_CHANGE_DISPLAY_NAME_FORM_TEXT.submit)
    
    
# ---- Developer add announcement message form ----
class DeveloperAddAnnouncementMessageForm(FlaskForm):
    message = StringField(DEVELOPER_ADD_ANNOUNCEMENT_MESSAGE_FORM_TEXT.message, validators=[DataRequired()])
    level = SelectField(DEVELOPER_ADD_ANNOUNCEMENT_MESSAGE_FORM_TEXT.level, validators=[DataRequired()], choices=AppConfig.ADD_ANNOUNCEMENT_MESSAGE_FORM_LEVEL_OPTS)
    duration = SelectField(DEVELOPER_ADD_ANNOUNCEMENT_MESSAGE_FORM_TEXT.duration, validators=[DataRequired()], choices=AppConfig.ADD_ANNOUNCEMENT_MESSAGE_FORM_DURATION_OPTS)
    submit = SubmitField(DEVELOPER_ADD_ANNOUNCEMENT_MESSAGE_FORM_TEXT.submit)