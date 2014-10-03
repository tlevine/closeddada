import sqlalchemy as s
from sqlalchemy.dialects.postgres import CIDR

import doeund as m

class PiwikVisit(
        select idvisit, idsite, idvisitor, visit_total_actions, location_ip, location_country, location_region, location_city, location_latitude, location_longitude from piwik_log_visit limit 1;

class PiwikVisitor(m.Dimension):
    visitorId = m.Column(s.String, primary_key = True)
    totalVisits = m.Column(s.Integer)
    totalVisitDuration = m.Column(s.Integer)
    totalActions = m.Column(s.Integer)
    totalPageViews = m.Column(s.Integer)
    firstVisitDate = m.Column(s.DateTime)
    lastVisitDate = m.Column(s.DateTime)

class PiwikVisitorLocation(m.Fact):
    ip_address = m.Column(CIDR, primary_key = True)
    visitor_id = m.Column(s.String, primary_key = True)
