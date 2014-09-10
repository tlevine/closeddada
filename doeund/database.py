from collections import namedtuple
from enum import Enum

from sqlalchemy import Column as _Column
from sqlalchemy.ext.declarative import \
    declarative_base as _declarative_base, declared_attr

Base = _declarative_base()

class Column(_Column):
    '''
    Column in a table with some model metadata

    This is a normal SQLAlchemy column with two special keyword arguments.

    label: pretty label for the field
    aggregations: list of aggregation functions
    '''
    def __init__(self, *args, **kwargs):
        _kwargs = dict(kwargs) # copy it rather than mutating it
        info = _kwargs.pop('info', {})
        if 'label' in _kwargs:
            info['label'] = _kwargs.pop('label')
        if 'aggregations' in _kwargs:
            info['aggregations'] = _kwargs.pop('aggregations')
        _Column.__init__(self, *args, info = info, **_kwargs)

class DadaBase(Base):
    __abstract__ = True

    @classmethod
    def _relationships(Class):
        for r in Class.__mapper__.relationships:
            yield r.key + '_id', r.key, r.argument

    @classmethod
    def _uniques(Class):
        for c in Class.__mapper__.columns:
            if c.unique:
                yield c.name 


class Fact(DadaBase):
    '''
    A fact table
    '''
    __abstract__ = True

    @declared_attr
    def __tablename__(Class):
        return 'fact_' + Class.__name__.lower()

class Dimension(Base):
    '''
    A dimension table

    Each dimension table should have only one dimension;
    the different columns within that table are treated
    as a hierarchy of levels within that dimension.
    '''
    __abstract__ = True

    @declared_attr
    def __tablename__(Class):
        return 'dim_' + Class.__name__.lower()

    @classmethod
    def new(Class, pk):
        '''
        Create a new instance of this dimension. Create defaults and merge
        relationships, but don't merge the new instance itself.
        '''
        msg = 'Please implement the %(c)s.new method.'
        raise NotImplementedError(msg % {'c': Class})

    def merge(self, session):
        raise NotImplementedError(
            'Please implement a %(c)s.merge method that calls one of'
            '%(c)s._merge_label and %(c)s._merge_pk and that calls'
            '%(c)s._merge_references if it is appropriate.' % \
            {'c': self.__class__})

    def _merge_pk(self, session):
        return session.merge(self)

    def _merge_label(self, session):
        Class = self.__class__
        filters = [(getattr(Class, column_name), getattr(self, column_name)) \
                   for column_name in column_names]

        query = session.query(Class)

        for unique_column, value in filters:
            if unique_column == None:
                raise ValueError('The table doesn\'t have a %s column.' % column_name)
            elif value == None:
                raise ValueError('The instance doesn\'t have a %s attribute.' % column_name)
            else:
                query = query.filter(unique_column == value)

        record = query.first()
        if record == None:
            _kwargs = dict(kwargs)
            for unique_column, value in filters:
                _kwargs[unique_column.name] = value
            record = Class(**_kwargs)
            session.add(record)
            # session.commit() ?
        return record

    def _merge_references(self, session, *references):
        '''
        references is a list of string names of relationship properties
        '''
        for reference in references:
            reference_instance = getattr(self, reference, None)
            if reference_instance == None:
                raise ValueError('The reference is None (not defined). This isn\'t allowed.')
        setattr(self, reference, reference_instance.merge(session))
        return session.merge(self)
