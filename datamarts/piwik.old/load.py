import os
import itertools
import json
import datetime

import requests
from sqlalchemy import desc

from ..logger import logger
from .model import PiwikAction, PiwikVisit, PiwikVisitorLocation

def update(sessionmaker):
    key = 'PIWIK_API_TOKEN'
    if key not in os.environ:
        raise ValueError('You need to set the %s environment variable.' % key)

    session = sessionmaker()

    # The most recent date
    most_recent = session.query(PiwikVisit.serverDateTime)\
                         .order_by(desc(PiwikVisit.serverDateTime))\
                         .limit(1).scalar()
    if most_recent == None:
        date = oldest_visit(os.environ[key]).date()

    else:
        # Delete things from the most recent _datetime in case of partial dates.
        _datetime = datetime.datetime.combine(most_recent.date(), datetime.time())
        date = most_recent.date()

        session.query(PiwikAction)\
               .filter(PiwikAction.datetime >= _datetime).delete()
        session.query(PiwikVisit)\
               .filter(PiwikVisit.serverDateTime >= _datetime)\
               .delete()
        session.commit()
        prior_visits = set(row[0] for row in session.query(PiwikVisit.idVisit))

    while date <= datetime.date.today():
        logger.info('Loading visits for %s' % date.isoformat())
        session.add_all(visits(os.environ[key], date, prior_visits))
        session.commit()
        logger.info('Loaded visits for %s' % date.isoformat())
        date += datetime.timedelta(days = 1)

    session.add_all(visitor_locations(session))
    session.commit()
    logger.info('Determined Piwik visitor locations')

def visitor_locations(session):
    session.query(PiwikVisitorLocation).delete()
    session.flush()
    rows = session.query(PiwikVisit.visitIp, PiwikVisit.visitorId).distinct()
    for ip_address, visitor_id in rows:
        yield PiwikVisitorLocation(ip_address = ip_address,
                                   visitor_id = visitor_id)

def visits(token, date, prior_visits):
    for offset in itertools.count(0, 100):
        response = get_visits(date, offset, token = token)
        rawvisits = json.loads(response.text)
        for visit in map(reify_visit, rawvisits):
            if visit.idVisit not in prior_visits:
                yield visit
        if len(rawvisits) == 0:
            break

def oldest_visit(token):
    url = 'http://piwik.thomaslevine.com'
    params = {
        'module': 'API',
        'method': 'Live.getLastVisitsDetails',
        'idSite': '2',
        'period': 'range',
        'year': '2000,2020',
        'format': 'json',
        'token_auth': token,
        'filter_limit': 1,
        'filter_sort_order': 'asc',
        'showColumns': 'serverDate',
    }
    response = requests.get(url, params = params)
    rawdate = json.loads(response.text)[0]['serverDate']
    return datetime.datetime.strptime(rawdate, '%Y-%m-%d')

# I need to be able to refresh this so I can get a fresh version
# for the most recent date in case it was incomplete.
# @cache('~/.dadawarehouse/piwik-api-requests')
def get_visits(date, offset, token = None): 
    url = 'http://piwik.thomaslevine.com'
    params = {
        'module': 'API',
        'method': 'Live.getLastVisitsDetails',
        'idSite': '2',
        'period': 'day',
        'date': date.isoformat(),
        'format': 'json',
        'token_auth': token,
        'filter_limit': 100,
        'filter_offset': offset,
    }
    return requests.get(url, params = params)

def reify_visit(v):
    if v['resolution'].count('x') == 1:
        screen_width, screen_height = tuple(map(float, v['resolution'].split('x')))
    else:
        screen_width = screen_height = 0

    _serverDateTime = datetime.datetime.fromtimestamp(v['serverTimestamp'])
    visit = PiwikVisit(
        idVisit = int(v['idVisit']),

        serverDateTime = _serverDateTime,
        clientTime = datetime.time(*map(int, v['visitLocalTime'].split(':'))),

        n_actions = int(v['actions']),
        browserCode = v['browserCode'],
        browserFamily = v['browserFamily'],
        browserFamilyDescription = v['browserFamilyDescription'],
        browserName = v['browserName'],
        browserVersion = v['browserVersion'],

        city = v['city'],
        continent = v['continent'],
        continentCode = v['continentCode'],
        country = v['country'],
        countryCode = v['countryCode'],
        
        daysSinceFirstVisit = int(v['daysSinceFirstVisit']),
        daysSinceLastVisit = int(v['daysSinceLastVisit']),
        
        deviceType = v['deviceType'],
        events = int(v['events']),
        
        idSite = int(v['idSite']),
        firstActionDate = datetime.datetime.fromtimestamp(v['firstActionTimestamp']),
        lastActionDate = datetime.datetime.fromtimestamp(v['lastActionTimestamp']),
        
        location = v['location'],
        latitude = None if v['latitude'] == None else float(v['latitude']),
        longitude = None if v['longitude'] == None else float(v['longitude']),
        
        operatingSystem = v['operatingSystem'],
        operatingSystemCode = v['operatingSystemCode'],
        operatingSystemShortName = v['operatingSystemShortName'],
        
        provider = v['provider'],
        providerName = v['providerName'],
        providerUrl = v['providerUrl'],
        referrerKeyword = v['referrerKeyword'],
        referrerKeywordPosition = v['referrerKeywordPosition'],
        referrerName = v['referrerName'],
        referrerSearchEngineUrl = v['referrerSearchEngineUrl'],
        referrerType = v['referrerType'],
        referrerTypeName = v['referrerTypeName'],
        referrerUrl = v['referrerUrl'],
        region = v['region'],
        regionCode = v['regionCode'],
        
        screen_width = screen_width,
        screen_height = screen_height,
        screenType = v['screenType'],
        searches = int(v['searches']),
        visitCount = int(v['visitCount']),
        visitDuration = int(v['visitDuration']),
        visitIp = v['visitIp'],
        visitorId = v['visitorId'],
        visitorType = v['visitorType'],
    )
    for plugin in v['plugins'].split(', '):
        setattr(visit, 'plugin_' + plugin, True)
    visit.actions = list(actions(visit, v['actionDetails']))

    logger.debug('Assembled Piwik visit %s' % v['idVisit'])
    return visit

def actions(visit, actionDetails):
    for visit_action_id, action in enumerate(actionDetails):
        time = datetime.time(*map(int, action['serverTimePretty'].split(' ')[-1].split(':')))
        _datetime = datetime.datetime.combine(visit.serverDateTime.date(), time)
        yield PiwikAction(
            visit_id = visit.idVisit,
            visit_action_id = visit_action_id,

            page_id = int(action['pageId']),
            page_id_action = action['pageIdAction'],

            page_title = action['pageTitle'],
            action_type = action['type'],
            datetime = _datetime,
            url = action['url'],
        )
