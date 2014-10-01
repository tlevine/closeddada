from collections import defaultdict
import datetime
import re

import sqlalchemy as s

from datamarts import (
    NotmuchMessage, PiwikVisit, BranchableLog,
)
from datamarts.logger import logger

from .model import PiwikEmailOverlap

def ipaddress_email(sessionmaker):
    session = sessionmaker()

    query = session.query(s.func.date(BranchableLog.datetime),
                          BranchableLog.ip_address).distinct()\
        .union(session.query(s.func.date(PiwikVisit.serverDateTime),
                             PiwikVisit.visitIp).distinct())
    ip_address_days = identifier_sets(query)

    query = session.query(NotmuchMessage.datetime,
                          NotmuchMessage.from_address).distinct()
    email_address_days = identifier_sets(query)


def piwik_email(sessionmaker):
    session = sessionmaker()

    logger.info('Querying piwik')
    query = session.query(s.func.date(PiwikVisit.serverDateTime),
                          PiwikVisit.visitorId)\
                   .distinct()
    piwik_visitorid_days = identifier_sets(query)

    logger.info('Querying email')
    y2011 = datetime.datetime(2011,1,1)
    query = session.query(s.func.date(NotmuchMessage.datetime),
                          NotmuchMessage.from_address,
                          s.func.count())\
                   .filter(NotmuchMessage.datetime > y2011)\
                   .filter(NotmuchMessage.is_mailing_list == False)\
                   .group_by(s.func.date(NotmuchMessage.datetime),
                             NotmuchMessage.from_address)
    filtered_query = ((date, addr) for date, addr, count in query if count >= 2)
    email_address_days = identifier_sets(filtered_query)

    logger.info('Selected %d Piwik visitors' % len(piwik_visitorid_days))
    logger.info('Selected %d email addresses' % len(email_address_days))

    logger.info('Checking overlap')
    session.query(PiwikEmailOverlap).delete()
    session.flush()

    for record in pairwise_check(email_address_days,
                                 piwik_visitorid_days):
        session.add(record)
        session.commit()
    return
    session.add_all(pairwise_check(email_address_days,
                                   piwik_visitorid_days))
    session.commit()

def pairwise_check(email_address_days, piwik_visitorid_days):
    for email_address, email_dates in email_address_days.items():
        for piwik_visitorid, piwik_dates in piwik_visitorid_days.items():
            intersection = len(email_dates.intersection(piwik_dates))
            union = len(email_dates.union(piwik_dates))
            yield PiwikEmailOverlap(email_address = email_address,
                                    visitor_id = piwik_visitorid,
                                    intersecting_dates = intersection,
                                    unioned_dates = union)

ME = re.compile(r'.*(thomas\.?levine).*', flags = re.IGNORECASE)
LIST = re.compile(r'.*(?:list|googlegroups|facebook|announce|discuss|reply|meetup.com|voice.google|[gG]roup|yahoogroups|-[lL]@|freeculture.org|tkl081|tkl22|haskell.org|students@|scraperwiki.com).*', flags = re.IGNORECASE)
def identifier_sets(query):
    identifier_days = defaultdict(set)
    for date, identifier in query:
        identifier_days[identifier].add(date)
    for identifier in list(identifier_days.keys()):
        n = len(identifier_days[identifier])
        # When I was first developing this, on October 1, 2014,
        # the from_address responsible for the most messages of
        # all addresses other than mailing lists or my own was
        # "mlevine00@gmail.com", with 552 messages. And he doesn't
        # use this address anymore.
        if n <= 2 or n > 600 or re.match(LIST, identifier)\
            or re.match(ME, identifier) or identifier.lower().startswith('r-'):
            del(identifier_days[identifier])
    return identifier_days
