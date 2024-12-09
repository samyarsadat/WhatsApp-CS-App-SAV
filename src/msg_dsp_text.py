#  WhatsApp messaging client project
#  All displayed error/warning/success messages and UI element text
#  Written by Samyar Sadat Akhavi, 2023
#
#  Project Information
#  Developer:        Samyar Sadat Akhavi
#  Start Date:       09/06/2023


# ------- Libraries -------
from flask_babel import lazy_gettext
from config import AppConfig


# ------- UI Elements -------
class UI_ELEMENTS_TEXT:
    NAV_HOME = lazy_gettext("Mesajlar")
    NAV_ACC_CHANGE_PASS = lazy_gettext("Şifre Değiştir")
    NAV_ACC_CHANGE_USER = lazy_gettext("Kullanıcı Adı Değiştir")
    NAV_ACC_ADMIN = lazy_gettext("Yönetim")
    NAV_ACC_LOGOUT = lazy_gettext("Çıkış")
    NAV_ACC_LOGIN = lazy_gettext("Oturum Aç")
    NAV_BACK_TO_HOME = lazy_gettext("Eve geri dön")
    NAV_SERVER_SELECT = lazy_gettext("Sunucu Subdomain Seçimi")

    TITLE_HOME = lazy_gettext("Mesajlar")
    MEDIA_ATTACHMENT = lazy_gettext("Dosya Eklentisi")
    LOCATION_ATTACHMENT = lazy_gettext("Konum Eklentisi")

    FOOTER_COPYRIGHT = lazy_gettext("Copyright © 2023 Samyar Sadat Akhavi")
    FOOTER_PRIVACY_POLICY = lazy_gettext("Privacy Policy")

    MESSAGE_VIEW_SEARCH_PLACEHOLDER = lazy_gettext("Aramak için yazın...")
    MESSAGE_VIEW_COMPOSE_PLACEHOLDER = lazy_gettext("Bir mesaj yazın...")
    MAX_FILE_SIZE_EXCEEDED = lazy_gettext("Yüklediğiniz dosya çok büyük!\u005CnDosya boyut sınırı %(limit)sMB!", limit=(AppConfig.MAX_CONTENT_LENGTH / 1000 / 1000))

    ADMIN_MAIN_TITLE = lazy_gettext("Yönetim Paneli")
    ADMIN_NAV_LAUNCH = lazy_gettext("Menü")
    ADMIN_NAV_HEADING = lazy_gettext("Yönetim Menüsü")
    ADMIN_NAV_REDIRECTS = lazy_gettext("Yönlendirmeleri Yönet")
    ADMIN_REDIRECTS_DEL = lazy_gettext("Yönlendirmeler")
    ADMIN_NO_REDIRECTS = lazy_gettext("Herhangi bir yönlendirme kuralı bulunmamaktadır.")
    ADMIN_NAV_AGENTS = lazy_gettext("Temsilcileri Yönet")
    ADMIN_AGENTS_DEL = lazy_gettext("Temsilciler")
    ADMIN_NO_AGENTS = lazy_gettext("Herhangi bir tesmsilci bulunmamaktadır.")
    ADMIN_NAV_SYSTEM_SETTINGS = lazy_gettext("Sistem Ayarları")
    ADMIN_ADD_REDIRECT = lazy_gettext("Yönlendirme Ekle")
    ADMIN_REMOVE_ALL_REDIRECTS = lazy_gettext("Yönlendirmeleri Sil")
    ADMIN_RENAME_CUSTOMER = lazy_gettext("Değiştir")

    NO_MSGS_SELECT_HEADER_MSG = lazy_gettext("Hoş geldiniz, bir sohbet seçin.")

    HTTP_ERR_PAGES_ERROR = lazy_gettext("Hata")
    HTTP_ERR_PAGES_NAMES = {
        "404": lazy_gettext("Bulunamadı"),
        "405": lazy_gettext("İzin Verilmeyen Yöntem"),
        "500": lazy_gettext("Dahili Sunucu Hatası"),
    }
    HTTP_ERR_PAGES_DESCS = {
        "404": lazy_gettext("Tüm yeri ve zamanı aradık ama aradığınız sayfa yok!"),
        "405": lazy_gettext("Bu sayfa, gönderdiğiniz istek türünü desteklemiyor."),
        "500": lazy_gettext("Sunucularımızda bir şeyler ters gitti! Lütfen daha sonra tekrar deneyiniz."),
    }

    # TODO: Add elements from flask-security-related pages


class ADMIN_SYS_SETTINGS_FORM_TEXT:
    waapi_callback_user = lazy_gettext("WhatsApp API Callback Request Username")
    waapi_callback_pass = lazy_gettext("WhatsApp API Callback Request Password")
    waapi_send_phone_num = lazy_gettext("WhatsApp API 'Send From' Number")
    waapi_api_base_url = lazy_gettext("WhatsApp API Base URL")
    waapi_api_api_key = lazy_gettext("WhatsApp API Key")
    mailjet_api_key = lazy_gettext("Mailjet API Key")
    mailjet_api_secret = lazy_gettext("Mailjet API Secret")
    security_mail_email = lazy_gettext("Security Mail 'Send From' Email")
    security_mail_sender_name = lazy_gettext("Security Mail Sender Name")
    ga_tag_id = lazy_gettext("Google Analytics Tag ID")
    ga_property_id = lazy_gettext("Google Analytics Property ID")
    max_customers_per_day = lazy_gettext("Max. Customers Per Day")
    max_agents_per_customer = lazy_gettext("Max. Agents Per Customer")
    max_file_upload_size_mb = lazy_gettext("Max. File Upload Size (MB)")
    submit = lazy_gettext("Update Settings")


class ADMIN_NEW_REDIRECT_FORM_TEXT:
    redirect_to_agent = lazy_gettext("Yönlendirilecek Temsilci")
    redirect_phone_number = lazy_gettext("Yönlendirilecek Müşteri")
    redirect_rule_name = lazy_gettext("Yönlendirme Kural Adı")
    submit = lazy_gettext("Yeni Yönlendirme Kuralı Ekle")


class ADMIN_NEW_AGENT_FORM_TEXT:
    agent_password = lazy_gettext("Temsilci Şifresi")
    agent_email = lazy_gettext("Temsilci Email")
    agent_type = lazy_gettext("Temsilci Türü")
    agent_phone_number = lazy_gettext("Temsilci Telefon Numarası")
    agent_username = lazy_gettext("Temsilci Kullanıcı Adı")
    submit = lazy_gettext("Yeni Temsilci Oluştur")
    
    
class ADMIN_CHANGE_DISPLAY_NAME_FORM_TEXT:
    new_display_name = lazy_gettext("Yeni Müşteri Adı")
    customer = lazy_gettext("Müşteri")
    submit = lazy_gettext("Adı Değiştir")
    
class DEVELOPER_ADD_ANNOUNCEMENT_MESSAGE_FORM_TEXT:
    message = lazy_gettext("Message")
    level = lazy_gettext("Message Level")
    duration = lazy_gettext("Message Duration")
    submit = lazy_gettext("Add Message")


# ------- Flash Messages -------
class FLASH_MESSAGES:
    ADMIN_SYS_SETTINGS_UPDATE_SUCCESS = lazy_gettext("Sistem ayarları başarıyla güncellendi!")
    ADMIN_SYS_SETTINGS_UPDATE_FAIL = lazy_gettext("Sistem ayarları güncellenmeye çalışılırken bir hata oluştu.")

    RENAME_CUSTOMER_SUCCESS = lazy_gettext("Müşteri yeniden adlandırıldı.")
    RENAME_NAME_EXIST = lazy_gettext("Zaten bu adı kullanan bir müşteri var!")
    INVALID_PHONE_NUMBER = lazy_gettext("Geçersiz telefon numarası! Lütfen telefon numarasını şu şekilde biçimlendirin: +905XXXXXXXXX")
    ADD_REDIRECT_RULE_SUCCESS = lazy_gettext("Yönlendirme kuralı başarıyla eklendi.")
    REDIRECT_RULE_ALREADY_EXIST = lazy_gettext("Bu yönlendirme kuralı zaten var!")
    REDIRECT_RULE_AGENT_UNABLE = lazy_gettext("Bir temsilcinin telefon numarası yönlendirilemez!")
    REDIRECT_RULE_AGENT_LIMIT_REACHED = lazy_gettext("Müşteri başına yönlendirme sınırını ulaştınız. Bu müşteriye yeni yönlendirme eklenemez.")

    AGENT_ADD_SUCCESS = lazy_gettext("Yeni temsilci başarıyla eklendi.")
    AGENT_ALREADY_EXIST = lazy_gettext("Bu temsilci zaten var.")
    INVALID_EMAIL_PASS = lazy_gettext("Geçersiz e-posta adresi veya şifre.")


# ------- WhatsApp error responses -------
class WA_SYSTEM_RESPONSES:
    INVALID_RESPONSE_CUSTOMER_ID = lazy_gettext("_*Sistem:* Geçersiz müşteri numarası!_")
    CLIENT_NOT_BELONG = lazy_gettext("_*Sistem:* Bu müşteri size ait değildir._")
    MEDIA_UNSUPPORTED = lazy_gettext("_*Sistem:* Bu mesaj türü desteklenmiyor!_")
    AGENT_NO_CUSTOMERS = lazy_gettext("_*Sistem:* Size yönlendirilen herhangi bir müşteri yoktur._")
    ORIGIN_MESSAGE_RESEND_FAILED = lazy_gettext("_*Sistem:* Mesaj yönlendirmede bir hata oluştu. Lütfen az sonra tekrar deneyin._")
    
    
# ------- System announcement messages -------
class SYSTEM_ANNOUNCEMENT_MESSAGES:
    CUSTOMERS_PER_DAY_LIMIT_REACHED = lazy_gettext("Günde maximum müşteri sınırını ulaştınız. Lütfen sistem yöneticinize ulaşınız.")


"""# ------- UI Elements -------
class ADMIN_SYS_SETTINGS_FORM_TEXT():
    waapi_callback_user = lazy_gettext("waapi Callback Request Username")
    waapi_callback_pass = lazy_gettext("waapi Callback Request Password")
    waapi_get_media_user = lazy_gettext("waapi Media Username")
    waapi_get_media_pass = lazy_gettext("waapi Media Password")
    waapi_send_phone_num = lazy_gettext("waapi 'Send From' Number")
    waapi_api_auth_token = lazy_gettext("waapi API Auth Token")
    waapi_api_account_sid = lazy_gettext("waapi API Account SID")
    mailjet_api_key = lazy_gettext("Mailjet API Key")
    mailjet_api_secret = lazy_gettext("Mailjet API Secret")
    security_mail_email = lazy_gettext("Security Mail 'Send From' Email")
    security_mail_sender_name = lazy_gettext("Security Mail Sender Name")
    ga_tag_id = lazy_gettext("Google Analytics Tag ID")
    ga_property_id = lazy_gettext("Google Analytics Property ID")
    submit = lazy_gettext("Update Settings")
    
    
class ADMIN_NEW_REDIRECT_FORM_TEXT():
    redirect_to_agent = lazy_gettext("Redirect To Agent")
    redirect_phone_number = lazy_gettext("Phone Number To Redirect")
    redirect_rule_name = lazy_gettext("Redirect Rule Name")
    submit = lazy_gettext("Add New Redirect Rule")
    
    
class ADMIN_NEW_AGENT_FORM_TEXT():
    agent_password = lazy_gettext("Agent Password")
    agent_email = lazy_gettext("Agent Email")
    agent_type = lazy_gettext("Agent Type")
    agent_phone_number = lazy_gettext("Agent Phone Number")
    agent_username = lazy_gettext("Agent Username")
    submit = lazy_gettext("Create New Agent")


class UI_ELEMENTS_TEXT():
    NAV_HOME = lazy_gettext("Messages")
    NAV_ACC_CHANGE_PASS = lazy_gettext("Change Password")
    NAV_ACC_CHANGE_USER = lazy_gettext("Change Username")
    NAV_ACC_ADMIN = lazy_gettext("Admin")
    NAV_ACC_LOGOUT = lazy_gettext("Logout")
    NAV_ACC_LOGIN = lazy_gettext("Login")
    NAV_BACK_TO_HOME = lazy_gettext("Back to Home")
    
    TITLE_HOME = lazy_gettext("Messages")
    
    FOOTER_COPYRIGHT = lazy_gettext("Copyright © 2023 Samyar Sadat Akhavi")
    FOOTER_PRIVACY_POLICY = lazy_gettext("Privacy Policy")
    
    MESSAGE_VIEW_SEARCH_PLACEHOLDER = lazy_gettext("Type to search...")
    MESSAGE_VIEW_COMPOSE_PLACEHOLDER = lazy_gettext("Write a message...")
    
    ADMIN_MAIN_TITLE = lazy_gettext("Admin Console")
    ADMIN_NAV_LAUNCH = lazy_gettext("Menu")
    ADMIN_NAV_HEADING = lazy_gettext("Admin Menu")
    ADMIN_NAV_REDIRECTS = lazy_gettext("Manage Redirects")
    ADMIN_NAV_AGENTS = lazy_gettext("Manage Agents")
    ADMIN_NAV_SYSTEM_SETTINGS = lazy_gettext("System Settings")
    
    NO_MSGS_SELECT_HEADER_MSG = lazy_gettext("Welcome, select a chat.")
    
    HTTP_ERR_PAGES_ERROR = lazy_gettext("Error")
    HTTP_ERR_PAGES_NAMES = {
        "404": lazy_gettext("Not Found"),
        "405": lazy_gettext("Method Not Allowed"),
        "500": lazy_gettext("Internal Server Error")}
    HTTP_ERR_PAGES_DESCS = {
        "404": lazy_gettext("We searched all of space and time but the page that you are looking for does not exist!"),
        "405": lazy_gettext("This page does not support the type of request that you sent."),
        "500": lazy_gettext("Something went wrong with our servers! Please try again later.")}

    # TODO: Add elements from flask-security-related pages
    
    
# ------- Flash Messages -------
class FLASH_MESSAGES():
    ADMIN_SYS_SETTINGS_UPDATE_SUCCESS = lazy_gettext("Successfully updated system settings!")
    ADMIN_SYS_SETTINGS_UPDATE_FAIL = lazy_gettext("An error occurred whilst attempting to update system settings.")
    
    INVALID_PHONE_NUMBER = lazy_gettext("Invalid phone number! Please format the phone number as follows: +905XXXXXXXXX")
    ADD_REDIRECT_RULE_SUCCESS = lazy_gettext("Added redirect rule successfuly.")
    REDIRECT_RULE_ALREADY_EXIST = lazy_gettext("This redirect rule already exists!")
    
    AGENT_ADD_SUCCESS = lazy_gettext("New agent added successfuly.")
    AGENT_ALREADY_EXIST = lazy_gettext("This agent already exists.")
    INVALID_EMAIL_PASS = lazy_gettext("Invalid email address or password.")
    
    
# ------- WhatsApp error responses -------
class WA_ERROR_RESPONSES():
    INVALID_RESPONSE_PHONE_NUM = lazy_gettext("Invalid phone number!")
    CLIENT_NOT_BELONG = lazy_gettext("This client does not belong to you.")"""
