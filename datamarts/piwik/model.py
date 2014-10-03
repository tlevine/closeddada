import sqlalchemy as s
from sqlalchemy.dialects.postgres import BYTEA, CIDR

import doeund as m

class PiwikVisit(m.Fact):
    idvisit = m.Column(s.Integer,
    #                  s.ForeignKey(PiwikVisit.idvisitor),
                       primary_key = True)
    idsite = m.Column(s.Integer)
    idvisitor = m.Column(BYTEA(8))
    visit_total_actions = m.Column(s.Integer)
    location_ip = m.Column(CIDR)
    location_country = m.Column(s.String, nullable = True)
    location_region = m.Column(s.String, nullable = True)
    location_city = m.Column(s.String, nullable = True)
    location_latitude = m.Column(s.Float, nullable = True)
    location_longitude = m.Column(s.Float, nullable = True)

class PiwikVisitor(m.Dimension):
    visitorId = m.Column(s.BINARY(8), primary_key = True)
    totalVisits = m.Column(s.Integer)
    totalVisitDuration = m.Column(s.Integer)
    totalActions = m.Column(s.Integer)
    totalPageViews = m.Column(s.Integer)
    firstVisitDate = m.Column(s.DateTime)
    lastVisitDate = m.Column(s.DateTime)
