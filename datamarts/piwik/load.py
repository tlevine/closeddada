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
    token = os.environ[key]

    visitorId = get_first_visitorId(token):
    while visitorId:
        response = get_visitor(visitorId, token)
        session.add(reify_visitor(response))
        sessin

def get_first_visitorId(token):
    first_response = get_visitor(None, token)
    second_visitorId = json.loads(response.text)['nextVisitorId']
    second_response = get_visitor(second_visitorId, token)
    first_visitorId = json.loads(response.text)['previousVisitorId']
    return first_visitorId

def get_visitor(visitorId, token): 
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

def reify_visitor(response):
    raw = json.loads(response.text)
    return PiwikVisitor(
        visitorId = visitorId,
        totalVisits = raw['totalVisits'],
        totalVisitDuration = raw['totalVisitDuration'],
        totalActions = raw['totalActions'],
        totalPageViews = raw['totalPageViews'],
        firstVisitDate = raw['firstVisit']['date'],
        lastVisitDate = raw['lastVisit']['date'],
    )
