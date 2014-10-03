from collections import defaultdict

from datamarts import PiwikVisit

def ip_address_visitor_id(session):
    ip_id = defaultdict(set)
    id_ip = defaultdict(set)
    query = session.query(PiwikVisit.visitIp, PiwikVisit.visitorId).distinct()
    for visitIp, visitorId in query:
        ip_id[visitIp].add(visitorId)
        ip_id[visitorId].add(visitIp)
    return ip_id, id_ip
