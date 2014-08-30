import os

import sqlalchemy as s
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from historian_reader.shell import historian

from warehouse.logger import logger

Base = declarative_base()

class Shell(Base):
    __tablename__ = 'shells'

    shell = s.Column(s.String(40), primary_key = True)
    shell_date = s.Column(s.DateTime(), nullable = False)

    def __repr__(self):
        return '<Shell(shell = "%s", shell_date = %s)>' % \
               (self.shell, self.shell_date)

class Command(Base):
    __tablename__ = 'commands'
    command_id = s.Column(s.Integer, primary_key = True)
    shell = s.Column(s.String(40), s.ForeignKey('shells.shell'), nullable=False)
    command_date = s.Column(s.DateTime, nullable = False)
    command = s.Column(s.String, nullable = False)
    def __repr__(self):
        return '<Command(shell = "%s", command_date = %s, command = """%s""")>' % \
               (self.shell, self.command_date, self.command)


drop_dim_shells = 'DROP VIEW IF EXISTS dim_shells;'
create_dim_shells = '''
CREATE VIEW dim_shells AS
SELECT
  shells.shell, shells.shell_date,
  max(commands.command_date) as 'final_command_date'
FROM commands
JOIN shells ON shells.shell = commands.shell
GROUP BY shells.shell;
'''

def session(cache_directory):
    database_file = os.path.join(cache_directory, 'shell-history.sqlite')
    engine = s.create_engine('sqlite:///' + database_file)
    Base.metadata.create_all(engine) 
    the_session = sessionmaker(bind=engine)()
    the_session.execute(drop_dim_shells)
    the_session.execute(create_dim_shells)
    return the_session

def update(session):
    HISTORY = os.path.join(os.path.expanduser('~'), 'history', 'shell')
    previous_shells = (row[0] for row in session.query(Shell.shell))
    for shell in historian(directory = HISTORY, skip = previous_shells):
        session.add(Shell(shell = shell['session'],
                          shell_date = shell['session_date']))
        session.add_all((Command(shell = shell['session'],
                                 command_date = command_date,
                                 command = command_string,
                ) for command_date, command_string in shell['commands']))
        session.commit()
        logger.info('Inserted commands from shell "%s"' % shell['session'])

def run(cache_directory):
    update(session(cache_directory))
