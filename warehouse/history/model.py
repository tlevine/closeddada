import sqlalchemy as s
from sqlalchemy.orm import relationship

import warehouse.model as m

class ShellSession(m.Dimension):
    pk = m.PkColumn()
    date_id = m.DateColumn()
    time_id = m.TimeColumn()
    filename = m.LabelColumn()
    commands = relationship('Command')

class Command(m.Fact):
    pk = m.PkColumn()
    shellsession_id = m.FkColumn(ShellSession.pk)
    date_id = m.DateColumn()
    time_id = m.TimeColumn()
    command = m.Column(s.String)
