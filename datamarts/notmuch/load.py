from io import StringIO
import sys
import re
import datetime
from itertools import chain
import subprocess
from functools import partial
from concurrent.futures import ThreadPoolExecutor

from notmuch import Database, Query
from sqlalchemy import func

import doeund as m

from ..logger import logger
from .model import NotmuchMessage, NotmuchAttachment

def update(sessionmaker):
    '''
    Update the notmuch database.

    In order that updates are fast, this is how state is resumed.

    1. Get the date of the most recent email that has been imported.
    2. Get the message identifiers of all emails that have been imported.
    3. Search for emails that are no more than a week older than the
       most recent import. This buffer of a week should deal with issues
       of time zones and unsynchronized clocks.
    4. Process emails ascending chronological order.
    5. Skip an email if the message ID for the email has already been
       processed.
    '''
    if offlineimap_is_running():
        raise EnvironmentError('In case offlineimap runs "notmuch new", you should stop offlineimap while importing data from notmuch.')

    session = sessionmaker()
    most_recent = session.query(func.max(NotmuchMessage.datetime)).scalar()

    sql_query = session.query(NotmuchMessage.message_id)
    past_messages = set(row[0] for row in sql_query.distinct())

    start_date = (most_recent.date() - datetime.timedelta(weeks = 1))
    q = Query(Database(), 'date:%s..' % start_date)
    q.set_sort(Query.SORT.OLDEST_FIRST)
    for m in q.search_messages():
        message_id = m.get_message_id()
        if message_id in past_messages:
            logger.debug('Already imported %s' % message_id)
            continue
        past_messages.add(message_id)

        session.add(message(m))
        session.flush() # for foreign key constraints

        # I don't really need these, and it takes a long time.
    #   session.add_all(attachments(m))

        session.commit()
        logger.info('Added message "id:%s"' % m.get_message_id())

def offlineimap_is_running():
    pgrep = subprocess.Popen(['pgrep', 'offlineimap'], stdout = subprocess.PIPE)
    pgrep.wait()
    stdout, stderr = pgrep.communicate()
    return len(stdout) > 0
MAILING_LIST_HEADERS = [
    'List-Id', # Google Groups, Mailman
    'List-Unsubscribe', # LISTSERV, "cmail.dickblick", ConstantContact, Mailchimp
    'X-Campaign', # ConstantContact, Mailchimp
    'X-CiviMail-Bounce', # CiviCRM
]
def message(m): 
    filename = m.get_filename()
    subject = m.get_header('subject')

    from_name, from_address = addresses.parseString(m.get_header('from'))[0]
   #recipient_names, recipient_addresses = zip(*chain(*addresses.parseString(m.get_header(name)) for name in ['to','cc','bcc']))

    is_mailing_list = 'undisclosed-recipients' in m.get_header('to') or \
        any(m.get_header(header) != '' for header in MAILING_LIST_HEADERS)

    return NotmuchMessage(
        message_id = m.get_message_id(),
        datetime = datetime.datetime.fromtimestamp(m.get_date()),
        thread_id = m.get_thread_id(),
        filename = filename,
        subject = subject,
        from_name = from_name,
        from_address = from_address,
        recipient_names = recipient_names,
        recipient_addresses = recipient_names,
        is_mailing_list = is_mailing_list,
    )

def attachments(message):
    with open(message.get_filename(), 'rb') as fp:
        pyzm = pyzmail.PyzMessage.factory(fp)
    for part_number, part in enumerate(pyzm.mailparts):
        yield NotmuchAttachment(
            message_id = message.get_message_id(),
            part_number = part_number,
            content_type = part.type,
            name = part.filename,
        )
