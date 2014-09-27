import sqlalchemy as s
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY

import doeund as m

class NotmuchMessage(m.Fact):
    message_id = m.Column(s.String, primary_key = True)
    datetime = m.Column(s.DateTime)
    thread_id = m.Column(s.String)
    filename = m.Column(s.String)
    subject = m.Column(s.String)
    from_name = m.Column(s.String, nullable = True)
    from_address = m.Column(s.String)
    recipient_names = m.Column(ARRAY(s.String))
    recipient_addresses = m.Column(ARRAY(s.String, dimensions = 1))

class NotmuchAttachment(m.Fact):
    message_id = m.Column(s.String,
                          s.ForeignKey(NotmuchMessage.message_id),
                          primary_key = True)
    message = relationship(NotmuchMessage)
    part_number = m.Column(s.Integer, primary_key = True)
    content_type = m.Column(s.String, nullable = True)
    name = m.Column(s.String, nullable = True)
