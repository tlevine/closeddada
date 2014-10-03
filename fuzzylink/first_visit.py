import datetime

from doeund import PiwikVisit, NotmuchMessage

def first_visit(session):
    hour, end = hour_range(session)
    while hour <= end:
        hour += datetime.timedelta(hours = 1)

def hour_range(session):
    a = session.query(PiwikVisit.serverDateTime).min().scalar()
    b = session.query(NotmuchMessage.datetime).min().scalar()
    start = max(a, b)
    beginning = datetime.datetime(d.year, d.month, d.day, d.hour)

    a = session.query(PiwikVisit.serverDateTime).max().scalar()
    b = session.query(NotmuchMessage.datetime).max().scalar()
    start = min(a, b)
    end = datetime.datetime(d.year, d.month, d.day, d.hour)

    return beginning, end
