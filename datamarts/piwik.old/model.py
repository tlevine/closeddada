import sqlalchemy as s
from sqlalchemy.dialects.postgres import CIDR

import doeund as m

class PiwikAction(m.Fact):
    visit_id = m.Column(s.Integer,
                        s.ForeignKey('ft_piwikvisit.idVisit'),
                        primary_key = True)
    visit_action_id = m.Column(s.Integer, primary_key = True)

    page_id = m.Column(s.Integer)
    page_id_action = m.Column(s.Integer, nullable = True)

    page_title = m.Column(s.String, nullable = True)
    datetime = m.Column(s.DateTime)
    action_type = m.Column(s.String)
    url = m.Column(s.String, nullable = True)

class PiwikVisit(m.Fact):
    idVisit = m.Column(s.Integer, primary_key = True)
    actions = s.orm.relationship(PiwikAction)

    serverDateTime = m.Column(s.DateTime)
    clientTime = m.Column(s.Time)

    n_actions = m.Column(s.Integer)
    browserCode = m.Column(s.String)
    browserFamily = m.Column(s.String)
    browserFamilyDescription = m.Column(s.String)
    browserName = m.Column(s.String)
    browserVersion = m.Column(s.String)

    daysSinceFirstVisit = m.Column(s.Integer)
    daysSinceLastVisit = m.Column(s.Integer)

    deviceType = m.Column(s.String)
    events = m.Column(s.Integer)

    idSite = m.Column(s.Integer)
    firstActionDate = m.Column(s.DateTime)
    lastActionDate = m.Column(s.DateTime)

    city = m.Column(s.String, nullable = True)
    continent = m.Column(s.String)
    continentCode = m.Column(s.String)
    country = m.Column(s.String)
    countryCode = m.Column(s.String)
    location = m.Column(s.String)
    region = m.Column(s.String, nullable = True)
    regionCode = m.Column(s.String, nullable = True)
    latitude = m.Column(s.Float, nullable = True)
    longitude = m.Column(s.Float, nullable = True)

    operatingSystem = m.Column(s.String)
    operatingSystemCode = m.Column(s.String)
    operatingSystemShortName = m.Column(s.String)

    plugin_pdf = m.Column(s.Boolean, default = False)
    plugin_flash = m.Column(s.Boolean, default = False)
    plugin_java = m.Column(s.Boolean, default = False)
    plugin_director = m.Column(s.Boolean, default = False)
    plugin_quicktime = m.Column(s.Boolean, default = False)
    plugin_realplayer = m.Column(s.Boolean, default = False)
    plugin_windowsmedia = m.Column(s.Boolean, default = False)
    plugin_gears = m.Column(s.Boolean, default = False)
    plugin_silverlight = m.Column(s.Boolean, default = False)
    plugin_cookie = m.Column(s.Boolean, default = False)

    provider = m.Column(s.String)
    providerName = m.Column(s.String)
    providerUrl = m.Column(s.String)
    referrerKeyword = m.Column(s.String, nullable = True)
    referrerKeywordPosition = m.Column(s.Integer, nullable = True)
    referrerName = m.Column(s.String, nullable = True)
    referrerSearchEngineUrl = m.Column(s.String, nullable = True)
    referrerType = m.Column(s.String, nullable = True)
    referrerTypeName = m.Column(s.String)
    referrerUrl = m.Column(s.String, nullable = True)

    screen_width = m.Column(s.Float)
    screen_height = m.Column(s.Float)
    screenType = m.Column(s.String)
    searches = m.Column(s.Integer)
    visitCount = m.Column(s.Integer)
    visitDuration = m.Column(s.Integer)
    visitIp = m.Column(CIDR)
    visitorId = m.Column(s.String)
    visitorType = m.Column(s.String)

class PiwikVisitorLocation(m.Fact):
    ip_address = m.Column(CIDR, primary_key = True)
    visitor_id = m.Column(s.String, primary_key = True)
