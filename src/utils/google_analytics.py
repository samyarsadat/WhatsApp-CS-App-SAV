#  WhatsApp messaging client project
#  Google Analytics Data API utility
#  Written by Samyar Sadat Akhavi, 2023
#  Original version by Samyar Sadat Akhavi, 2020
#  
#  Project Information
#  Developer:        Samyar Sadat Akhavi
#  Start Date:       09/06/2023


# ------- Libraries and utils -------
from google.api_core.exceptions import ServiceUnavailable, ResourceExhausted
from google.analytics.data_v1beta.types import DateRange, Metric, RunReportRequest, RunReportResponse
from config import AppConfig
from init import ga, debug_log, log


# ---- Global variables ----
PROPERTY_ID = AppConfig.ANALYTICS_PROPERTY_ID


# -=-=-= Functions =-=-=-

# ---- Run report with checks ----
def run_report_with_checks(request: RunReportRequest) -> RunReportResponse:
    if AppConfig.ENABLE_ANALYTICS == False:
        debug_log.debug(f"Analytics requested however 'Analytics' is disabled.")
        return RunReportResponse()
    
    try:
        return ga.run_report(request)

    except ServiceUnavailable:
        log.critical("Requested analytics data from the Google Analytics Data API however the API responded with [503 Service Unavailable]")
        debug_log.debug("Requested analytics data from the Google Analytics Data API however the API responded with [503 Service Unavailable]")
        return RunReportResponse()
    
    except ResourceExhausted:
        log.critical("Requested analytics data from the Google Analytics Data API however the API responded with [429 Resource Exhausted]")
        debug_log.debug("Requested analytics data from the Google Analytics Data API however the API responded with [429 Resource Exhausted]")
        return RunReportResponse()
    
    except Exception:
        log.critical("Requested analytics data from the Google Analytics Data API however the API responded with exception:", exc_info=1)
        debug_log.debug("Requested analytics data from the Google Analytics Data API however the API responded with exception:", exc_info=1)
        return RunReportResponse()


# ---- Get basic analytics data from the API ----
def get_basic_data(start_date: str, end_date: str, metric: str) -> RunReportResponse:
    request = RunReportRequest(
        property = f"properties/{PROPERTY_ID}",
        metrics = [Metric(name=metric)],
        date_ranges = [DateRange(start_date=start_date, end_date=end_date)],
    )
    
    debug_log.debug(f"Basic analytics query for metric [{metric}] with date range [{start_date}, {end_date}]")
    return run_report_with_checks(request)
    

# ---- Parse usable data from raw basic API response ----
def parse_basic_response(response: RunReportResponse) -> str:
    if response.rows:
        return str(response.rows[0].metric_values[0].value)
    
    return "NO DATA"


class Analytics():
    # ---- Total page views ----
    def total_pageviews() -> str:
        response = get_basic_data("2022-05-01", "today", "screenPageviews")
        return parse_basic_response(response)


    # ---- Total page views (Past 30 days) ----
    def pageviews_this_month() -> str:
        response = get_basic_data("30daysAgo", "today", "screenPageviews")
        return parse_basic_response(response)
    

    # ---- Total page views (Today) ----
    def pageviews_today() -> str:
        response = get_basic_data("today", "today", "screenPageviews")
        return parse_basic_response(response)


    # ---- Total unique user count ----
    def total_users() -> str:
        response = get_basic_data("2022-05-01", "today", "totalUsers")
        return parse_basic_response(response)


    # ---- Number of new users (Today) ----
    def new_users_today() -> str:
        response = get_basic_data("today", "today", "newUsers")
        return parse_basic_response(response)


    # ---- Number of active users (Today) ----
    def active_users_today() -> str:
        response = get_basic_data("today", "today", "activeUsers")
        return parse_basic_response(response)
    
    
    # ---- Custom basic API query ----
    def custom_basic_query(start_date: str, end_date: str, metric: str) -> str:
        response = get_basic_data(start_date, end_date, metric)
        return parse_basic_response(response)
    
    
    # ---- Fully custom API query ----
    def custom_query(request: RunReportRequest) -> RunReportResponse:
        debug_log.debug(f"Fully custom analytics query for metrics [{request.metrics}] with date ranges [{request.date_ranges}]")
        return run_report_with_checks(request)