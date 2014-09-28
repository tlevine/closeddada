from collections import defaultdict
from itertools import chain
import shutil
import os
import re
import datetime
import subprocess

import sqlalchemy

from ..logger import logger
from .model import FacebookChatStatusChange, FacebookMessage, \
                   FacebookDuration, FacebookNameChange

WAREHOUSE = os.path.expanduser('~/.dadawarehouse')
LOCAL_CHAT = os.path.join(WAREHOUSE, 'facebookchat')
REMOTE_CHAT = 'safe:rsync/ekg2-logs/xmpp:perluette@chat.facebook.com/*.db'
RSYNC = ['rsync', '--archive', '--sparse'] #, '--verbose']

def download():
    if not os.path.isdir(LOCAL_CHAT):
        os.mkdir(LOCAL_CHAT)
    rsync = subprocess.Popen(RSYNC + [REMOTE_CHAT, LOCAL_CHAT])
    rsync.wait()

UID = re.compile(r'xmpp:-([0-9]+)@chat.facebook.com')
def parse_uid(uid):
    try:
        return int(re.match(UID, uid).group(1))
    except:
        print(uid)
        raise

def status_changes(engine, filedate, session):
    sql = 'SELECT rowid, uid, nick, ts, status FROM log_status'
    for rowid, uid, nick, ts, status in engine.execute(sql):
        yield FacebookChatStatusChange(
            filedate = filedate,
            rowid = rowid,
            user_id = parse_uid(uid),
            datetime = datetime.datetime.fromtimestamp(ts),
            current_name = nick,
            status = status)

def messages(engine, filedate, session):
    sql = 'SELECT rowid, uid, nick, ts, body FROM log_msg'
    for rowid, uid, nick, ts, body in engine.execute(sql):
        yield FacebookMessage(
            filedate = filedate,
            rowid = rowid,
            user_id = parse_uid(uid),
            datetime = datetime.datetime.fromtimestamp(ts),
            current_name = nick,
            body = body)

def online_durations(engine, filedate, session):
    for row in engine.execute('SELECT DISTINCT uid FROM log_status;'):
        uid = row[0]
        duration = 0
        avail = False
        prev_ts = None
        for ts, status in engine.execute('SELECT ts, status FROM log_status WHERE uid = ? ORDER BY ts', uid):
            if status == 'avail' and not avail:
                avail = True
                prev_ts = ts
            elif status == 'avail' and avail:
                pass
            elif status == 'avail' and not avail:
                avail = True
                prev_ts = ts
            elif status == 'notavail' and not avail:
                pass
            elif status == 'notavail' and avail:
                duration += ts - prev_ts
                avail = False
                prev_ts = None
            elif status == 'notavail' and not avail:
                pass
            else:
                raise AssertionError('This else condition shouldn\'t happen.')

        yield FacebookDuration(
            date = filedate,
            user_id = parse_uid(uid),
            duration = duration
        )

def update(session, today = datetime.date.today()):
    first_pass(session, today)
    second_pass(session)

def first_pass(session, today):
    logger.info('Downloading Facebook logs')
    download()
    logger.info('Assessing the existing Facebook imports')
    could_import = set(os.listdir(LOCAL_CHAT))
    already_imported = set(row[0] for row in session.query(FacebookChatStatusChange.filedate).all())
    for filename in sorted(could_import, reverse = True):
        try:
            filedate = datetime.datetime.strptime(filename, '%Y-%m-%d.db').date()
            if filedate >= today:
                logger.info('Skipping %s because it is from today' % filename)
                # The file might not be complete.
                continue
            elif filedate in already_imported:
                logger.debug('Already imported %s' % filename)
                continue
            logger.debug('Importing %s' % filename)

            # Copy to RAM so it's faster.
            shutil.copy(os.path.join(LOCAL_CHAT, filename), '/tmp/fb.db')
            logger.debug('* Copied database to RAM')
            engine = sqlalchemy.create_engine('sqlite:////tmp/fb.db')

            # Add stuff
            session.add_all(status_changes(engine, filedate, session))
            logger.debug('* Added status changes')
            session.add_all(messages(engine, filedate, session))
            logger.debug('* Added messages')
            session.add_all(online_durations(engine, filedate, session))
            logger.debug('* Added durations')

            # Commit only at the end so that we don't have partial file data.
            session.commit()
            logger.info('Finished %s\n' % filename)

        except KeyboardInterrupt:
            break

def second_pass(session):
    '''
    Get name changes.

    This index should help. ::

        CREATE INDEX facebook_status_datetime
        ON ft_facebookchatstatuschange (datetime);

    Or maybe I can order by primary key?
    '''
    Class = FacebookChatStatusChange
  # Class = FacebookMessage

    q = session.query(Class.user_id,
                      Class.current_name,
                      Class.datetime)\
               .order_by(Class.filedate,
                         Class.rowid)

    session.add_all(name_changes(q))
    session.commit()
    
def name_changes(q):
    prev_name = {}
    for user, name, date in q:
        if user not in prev_name:
            # If this a new user, record it.
            # We don't know when the person first set this name,
            # so we mark that it is the first one we saw.
            yield FacebookNameChange(user_id = user,
                                     datetime = date,
                                     new_name = name,
                                     initial_name = True)
            prev_name[user] = name
            logger.info('User %s\'s initial name was on "%s"' % \
                        (user, name))

        elif name != prev_name[user]:
            # If this is the same user but a new name, record it.
            yield FacebookNameChange(user_id = user,
                                     datetime = date,
                                     new_name = name,
                                     initial_name = False)
            prev_name[user] = name
            logger.info('Detected a name change for %s on %s' % \
                        (user, date.isoformat()))
        # Otherwise, this is the same user with the same name
