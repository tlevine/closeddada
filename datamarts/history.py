import subprocess
import os
import shlex

from historian_reader.shell import historian
import xapian

from .logger import logger

HISTORY = os.path.expanduser('~/.dadawarehouse/history')
CLOSEDDADA = os.path.expanduser('~/.closeddada')

db = xapian.WritableDatabase(os.path.join(CLOSEDDADA, 'history'),
                             xapian.DB_CREATE_OR_OPEN)
termgenerator = xapian.TermGenerator()
termgenerator.set_stemmer(xapian.Stem("en"))

def download():
    RSYNC = ['rsync', '--archive', '--sparse']
    subdirectories = ['history-nsa/', 'history-home/', 'history-laptop/']
    for subdirectory in subdirectories:
        remote = 'safe:' + os.path.join('rsync', subdirectory)
        logger.debug(' '.join(RSYNC + [remote, HISTORY]))
        rsync = subprocess.Popen(RSYNC + [remote, HISTORY])
        rsync.wait()

def update(sessionmaker):
    download()
    session = sessionmaker()
    shell_history = os.path.join(HISTORY, 'shell')
   #previous_shells = (row[0] for row in session.query(ShellSession.filename))
    for log in historian(directory = shell_history, skip = previous_shells):
        filename = log['session']
        datetime = log['session_date']
        for command_datetime, command_string in log['commands']:
            doc = xapian.Doc()
            termgenerator.set_document(doc)
            termgenerator.index_text(filename, 1, 'F')
            termgenerator.index_text(command_string)
            command_datetime, 
