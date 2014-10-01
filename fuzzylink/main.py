from sqlalchemy.orm import sessionmaker

from .web_email.load import ipaddress_email, piwik_email
from .web_email.model import PiwikEmailOverlap

def load(engine):
    sm = sessionmaker(bind=engine)
    piwik_email(sm)
