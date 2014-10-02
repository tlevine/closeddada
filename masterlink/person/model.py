'''
Mappings between service-specific identifiers and
global person identifiers for different services

The global identifier is in the format that I use in
my mutt alias file, which is approximately one of these.

* ``[first name].[last name]``
* ``[first name].[middle name].[last name]``
* ``[nickname]``
* ``[first name].[last name].[context, like a city]``

I use the last of these if the others would be ambiguous
because different people have the same name.
'''
import sqlalchemy as s
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgres import CIDR

from doeund import Fact, Dimension, Column
from datamarts import (
    BranchableLog,
    FacebookMessage, FacebookChatStatusChange,
    FacebookDuration, FacebookNameChange,
    MuttAlias,
    NotmuchMessage, NotmuchAttachment,
    PiwikVisit, PiwikVisitorLocation,
    TwitterAction, TwitterNameHandle,
)

class Person(Fact):
    '''
    If you have an attribute of a person and want to know the other
    attributes of the person, filter based on the columns in this table.

    If you have the global identifier of a person and want to filter
    another cube based on this identifier (treating person as a dimension),
    you should not use the columns in this table. Instead, you should use
    the appropriate dimension column within that cube. The cube is a view
    that recursively applies joins to denormalize a fact table, and this
    dimesion is included in that denormalized view.
    '''
    id = Column(s.String, primary_key = True)

def PersonId(*args, **kwargs):
    return Column(s.String, s.ForeignKey(Person.id), *args, **kwargs)

class PersonEmailAddress(Fact):
    person_id = PersonId()
    email_address = Column(s.String, primary_key = True)

PersonEmailAddress.add_union(MuttAlias, (MuttAlias.email_address, Person.id))

NotmuchMessage.add_join([(NotmuchMessage.from_address, PersonEmailAddress.email_address)])
# NotmuchMessage.add_join([(NotmuchMessage.recipient_addresses, PersonEmailAddress.email_address)])

class PersonLocation(Fact):
    'Populate this from a CSV file.'
    ip_address = Column(CIDR, primary_key = True)
    person_id = PersonId(primary_key = True)
PersonLocation.add_union(PiwikVisitorLocation,
                         (PiwikVisitorLocation.ip_address, Person.id))

class PiwikVisitor(Dimension):
    id = Column(s.String, primary_key = True)
    person_id = PersonId(nullable = True)

PiwikVisit.add_join([(PiwikVisit.visitorId, PiwikVisitor.id)])
PiwikVisitorLocation.add_join(
    [(PiwikVisitorLocation.visitor_id, PiwikVisitor.id)])

class PersonTwitter(Fact):
    id = Column(s.String, primary_key = True)
    person_id = PersonId()

TwitterAction.add_join([(TwitterAction.user_handle, PersonTwitter.id)])

class PersonFacebook(Fact):
    id = Column(s.BigInteger, primary_key = True)
    person_id = PersonId()

FacebookMessage.add_join([(FacebookMessage.user_id, PersonFacebook.id)])
FacebookChatStatusChange.add_join([(FacebookChatStatusChange.user_id,
                                    PersonFacebook.id)])
FacebookDuration.add_join([(FacebookDuration.user_id, PersonFacebook.id)])
FacebookNameChange.add_join([(FacebookNameChange.user_id, PersonFacebook.id)])

# I need to union all of these
class PersonName(Fact):
    'Populate this from a CSV file.'
    name = Column(s.String, primary_key = True)
    person_id = PersonId(primary_key = True)

TwitterNameHandle.add_join([(TwitterNameHandle.user_handle, PersonTwitter.id)])
MuttAlias.add_join([(MuttAlias.pk, Person.id)])
FacebookNameChange.add_join([(FacebookNameChange.user_id, PersonFacebook.id)])
PersonName.add_union(TwitterNameHandle, (TwitterNameHandle.name, Person.id))
PersonName.add_union(MuttAlias, (MuttAlias.name, Person.id))
PersonName.add_union(FacebookNameChange, (FacebookNameChange.new_name, Person.id))
