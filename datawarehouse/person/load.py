import os
import csv
from collections import Counter

from sqlalchemy.ext.declarative import declarative_base

from datamarts.logger import logger
from datamarts import (
    BranchableLog,
    FacebookNameChange,
    MuttAlias,
    NotmuchMessage,
    PiwikVisit,
    TwitterAction,
)

from .model import Person, EmailAddress, Facebook, Twitter

file_mapping = [
    ('emailaddress.csv', EmailAddress),
    ('facebook.csv', Facebook),
    ('twitter.csv', Twitter),
    ('name.csv', None),
    ('ipaddress.csv', None),
    ('piwik.csv', None),
]

def load_person(session, directory):
    for filename, Class in file_mapping:
        logger.info('Importing %s' % filename)
        path = os.path.join(directory, filename)
        if os.path.exists(path):
            with open(path) as fp:
                rows = list(map(_strip, csv.DictReader(fp)))

            old_person_ids = set(row[0] for row in session.query(Person.id))
            new_person_ids = set(row['person_id'] for row in rows)
            session.add_all(Person(id = pid) for pid in \
                            (new_person_ids - old_person_ids))

            if Class != None and len(rows) > 0:
                for column_name in rows[0].keys():
                    values = list(duplicates(rows, column_name))
                    if len(values) > 0:
                        msg = 'The following values are duplicated in the "%s" column of "%s":\n\n%s\n'
                        logger.warning(msg % (column_name, path, '\n'.join(values)))

                session.query(Class).delete()
                records = (Class(**row) for row in rows)
                session.add_all(records)

            session.flush()

        else:
            with open(path, 'w') as fp:
                writer = csv.writer(fp)
                writer.writerow(Class.__table__.columns.keys())

    session.commit()

def duplicates(rows, column_name):
    counts = Counter(row[column_name] for row in rows)
    for value, count in counts.items():
        if count > 1:
            yield value

def _strip(dictionary):
    return {k.strip():v.strip() for k,v in dictionary.items()}
