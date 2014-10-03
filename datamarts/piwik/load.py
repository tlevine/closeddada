import os
import itertools
import json
import datetime

import requests
from sqlalchemy import desc

from ..logger import logger
from .model import (
    PiwikVisit,
    PiwikVisitor,
)
from .queries import (
    VISIT,
)

def update(sessionmaker):
    piwik_key = 'PIWIK_API_TOKEN'
    mysql_key = 'DADAWAREHOUSE_MYSQL_PASSWORD'
    for key in [piwik_key, mysql_key]:
        if key not in os.environ:
            msg = 'You need to set the %s environment variable.'
            raise ValueError(msg % key)

    url = 'mysql+pymysql://dadawarehouse:%s@piwik.thomaslevine.com/piwik'
    engine = s.create_engine(url % os.environ[mysql_key])
    token = os.environ[key]

    session = sessionmaker()
    prev_idvisit = session.query(PiwikVisit.idvisit).max().scalar()

    for i, row in enumerate(download(engine, prev_idvisit))):
        if i == 0:
            todo = []
        elif i % 100 == 0:
            session.add_all(todo)
            session.commit()
            todo = []
        else:
            todo.append(row)
    session.commit()

def download(engine, prev_idvisit):
    for (
        idvisit,
        idsite,
        idvisitor,
        visit_total_actions,
        location_ip_binary,
        location_country,
        location_region,
        location_city,
        location_latitude,
        location_longitude,
    ) in engine.execute(VISIT % prev_idvisit):
        location_ip = '.'.join(map(str,map(int,location_ip_binary)))
        yield PiwikVisit(
            idvisit =             idvisit,
            idsite =              idsite,
            idvisitor =           idvisitor,
            visit_total_actions = visit_total_actions,
            location_ip =         location_ip,
            location_country =    location_country,
            location_region =     location_region,
            location_city =       location_city,
            location_latitude =   location_latitude,
            location_longitude =  location_longitude,
        )
