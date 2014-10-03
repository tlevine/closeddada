from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class 
        select idvisit, idsite, idvisitor, visit_total_actions, location_ip, location_country, location_region, location_city, location_latitude, location_longitude from piwik_log_visit limit 1;
