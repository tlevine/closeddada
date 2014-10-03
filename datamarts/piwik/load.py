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

def get
    engine = s.create_engine('mysql+pymysql://piwik.thomaslevine.com/piwik')
