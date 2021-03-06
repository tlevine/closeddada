import os
import itertools
import json
import datetime

import requests
from sqlalchemy import func, create_engine

from ..logger import logger
from .model import (
    PiwikVisit,
    PiwikVisitor,
)
from .queries import (
    VISIT,
    LINK_VISIT_ACTION,
)

def update(sessionmaker):
    piwik_key = 'PIWIK_API_TOKEN'
    mysql_key = 'DADAWAREHOUSE_MYSQL_PASSWORD'
    for key in [piwik_key, mysql_key]:
        if key not in os.environ:
            msg = 'You need to set the %s environment variable.'
            raise ValueError(msg % key)

    url = 'mysql+pymysql://dadawarehouse:%s@piwik.thomaslevine.com/piwik'
    engine = create_engine(url % os.environ[mysql_key])
    token = os.environ[key]

    session = sessionmaker()
    prev_idvisit = session.query(func.max(PiwikVisit.idvisit)).scalar()

    for i, row in enumerate(visits(engine, prev_idvisit)):
        if i == 0:
            todo = []
        elif i % 100 == 0:
            session.add_all(todo)
            session.commit()
            todo = []
        else:
            todo.append(row)
    session.commit()

def link_visit_actions(engine, count_link_visit_action):
    if count_link_visit_action == None:
        count_link_visit_action = 0
    query = engine.execute(LINK_VISIT_ACTION % count_link_visit_action)
    for idvisit, idvisitor, idaction_url in query:
        yield PiwikAction(idvisit = idvisit,
                          idvisitor = idvisitor,
                          idaction_url = idaction_url)

def visits(engine, prev_idvisit):
    if prev_idvisit == None:
        prev_idvisit = -1
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
        if location_ip.count('.') != 3:
            logger.error('Problem converting the IP address %s' % location_ip_binary)
            continue

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
