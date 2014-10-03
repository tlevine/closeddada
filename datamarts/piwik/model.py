import sqlalchemy as s
from sqlalchemy.dialects.postgres import CIDR

import doeund as m

class PiwikVisitor(m.Fact):
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
