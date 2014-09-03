import os
import datetime

from ..logger import logger
import warehouse.model as m
from .model import (CalendarFilename, CalendarDescription, CalendarFile,
                    CalendarEventDescription, CalendarEvent)

CALENDARS = [os.path.join(os.path.expanduser('~/.pal'), rest) for rest in [\
    'secrets-nsa/secret-calendar.txt',
    'p/activities.txt',
    'p/to-do.txt',
    'p/sleeping.txt',
    'p/travel.txt',
    'p/postponed.txt',
]]
    
def update(session, calendars = CALENDARS):
    session.query(CalendarFile).delete()
    session.query(CalendarEvent).delete()

    for filename in calendars:
        with open(filename) as fp:
            labels, normals = parse(fp)
        for label in labels:
            m.add_label(session, label)
        session.add_all(normals)
        session.commit()
        logger.info('Inserted events from calendar %s' % filename)

def parse(fp, filename = None):
    'Read a pal calendar file.'
    labels = []
    normals = []

    # Parse the filename.
    if filename == None:
        try:
            filename = fp.name
        except NameError:
            raise ValueError('You must specify a filename.')
    filename_record = CalendarFilename(filename = filename)
    labels.append(filename_record)

    calendar = None
    for line in fp:
        line = line.rstrip()
        if line.startswith('#'):
            pass
        elif calendar == None:
            calendar_code, _, calendar_description = line.partition(' ')
            description_record = CalendarDescription(description = calendar_description)
            labels.append(description_record)
            normals.append(CalendarFile(pk = calendar_code,
                filename = filename_record, description = description_record))

        else:
            for date, description in entry(line):
                event_description = CalendarEventDescription(eventdescription = description)
                labels.append(event_description)
                normals.appendCalendarEvent(calendar = calendar_record,
                    date = date, description = event_description)
    return labels, normals

def entry(line):
    'Read a pal calendar entry'
    datespec, _, description = line.partition(' ')
    for date in dates(datespec):
        yield date, description

def read_date(datestring):
    try:
        date = datetime.datetime.strptime(datestring, '%Y%m%d')
    except ValueError:
        return None
    else:
        return date.date()

def dates(datespec:str):
    single_date = read_date(datespec)
    if single_date != None:
        yield single_date
    elif datespec.count(':') == 2:
        subset, start, end = datespec.split(':')
        if subset == 'DAILY':
            today = read_date(start)
            end = read_date(end)
            while today <= end:
                yield today
                today += datetime.timedelta(days = 1)
    else:
        logger.warn('Unsupported date specification: "%s"' % datespec)
