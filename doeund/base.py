from sqlalchemy.ext.declarative import \
    declarative_base as _declarative_base, declared_attr

Base = _declarative_base()

class DadaBase(Base):
    __abstract__ = True

    @classmethod
    def add_join(from_class, on_columns):
        from_table = from_class.__table__
        
        if 'joins' not in from_table.info:
            from_table.info['joins'] = []

        from_table.info['joins'].append([(
            from_column.table.columns[from_column.name],
            to_column.table.columns[to_column.name],
        ) for from_column, to_column in on_columns])

class Fact(DadaBase):
    __abstract__ = True

    @declared_attr
    def __tablename__(Class):
        return 'ft_' + Class.__name__.lower()

    @classmethod
    def add_union(Class, OtherClass, columns):
        '''
        A query to this fact's cube view will include all of the
        fact table columns plus the selected columns from the union.
        '''
        if 'unions' not in Class.__table__.info:
            Class.__table__.info['unions'] = []
        Class.__table__.info['unions'].append((OtherClass.__table__, columns))

class Dimension(DadaBase):
    __abstract__ = True

    @declared_attr
    def __tablename__(Class):
        return 'dim_' + Class.__name__.lower()
