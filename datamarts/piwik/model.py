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

# Rather than importing the visitor profile thing from Piwik,
# I'm just linking to it.
'''
CREATE OR REPLACE FUNCTION visitor_profile(BYTEA)
RETURNS TEXT AS $$
BEGIN
    RETURN 'http://piwik.thomaslevine.com/index.php?date=2000-01-01,2020-01-01&module=Widgetize&action=iframe&widget=1&idSite=2&period=range&moduleToWidgetize=Live&actionToWidgetize=getVisitorProfilePopup&visitorId=' || encode($1, 'hex');
END;
$$ LANGUAGE plpgsql;
'''
