import re

from sqlalchemy.sql.schema import ForeignKeyConstraint, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import ARRAY

from doeund.templates import drop_view, create_view

def make_cubes(tables):
    fact_tables = filter(lambda table: table.name.startswith('ft_'), tables.values())
    n_unions = lambda table: len(list(union_strings(table)))
    for table in sorted(fact_tables, key = n_unions):
        yield from make_cube(table)

def make_cube(table):
    fact_table_base = re.sub(r'^ft_', '', table.name)
    yield drop_view.substitute(fact_table_base = fact_table_base)
    yield create_view.substitute(
        fact_table_base = fact_table_base,
        columns = list(columns_to_select(table)),
        joins = list(join_strings(table)),
        unions = list(union_strings(table)))

def aliased_column_name(column):
    alias = '%s_%s' % (re.sub(r'^(?:ft_|dim_)', '', column.table.name), column.name)
    return '"%s"."%s" AS "%s"' % (column.table.name, column.name, alias)

def unaliased_column_name(column):
    return '"%s"."%s"' % (column.table.name, column.name)

def columns_to_select(table):
    '''
    Come up with a list of columns to put in the select statement.
    '''
    do_not_select = set()
    for on_columns in joins(table):
        to_table = on_columns[0][1].table
        for from_column, to_column in on_columns:
            do_not_select.add((from_column.table.name, from_column.name))

    yield from _columns_one_table(do_not_select, False, table)
    for on_columns in joins(table):
        table = on_columns[0][1].table
        yield from _columns_one_table(do_not_select, True, table)

def _columns_one_table(do_not_select, aliased, table):
    for column in table.columns:
        f = aliased_column_name if aliased else unaliased_column_name
        if (column.table.name, column.name) not in do_not_select and not column.info['hide']:
            yield f(column)

def _unpruned_joins(table):
    '''
    List the joins from this table.

    This automatically detects joins that are encoded as
    foreign keys. If you have joins that are not encoded as
    foreign keys, use the add_join class method.

    If the same target table is specified twice, this includes both
    join specifications, which could lead to an error.
    '''
    for on_columns in table.info.get('joins', []):
        yield on_columns
        to_table = on_columns[0][1].table
        yield from _unpruned_joins(to_table)

    for constraint in table.constraints:
        if isinstance(constraint, ForeignKeyConstraint):
            from_columns = [col for col in constraint.columns]
            to_columns = [fk.column for fk in constraint.elements]
            yield list(zip(from_columns, to_columns))

            to_table = to_columns[0].table
            if len(set(to_column.table.name for to_column in to_columns)) != 1:
                raise AssertionError('This shouldn\'t happen.')
            yield from _unpruned_joins(to_table)

def joins(table):
    joined_tables = set()
    for join in _unpruned_joins(table):
        for from_column, to_column in join:
            if to_column.table.name in joined_tables:
                break
        else:
            joined_tables.add(to_column.table.name)
            yield join

def join_strings(table):
    for on_columns in joins(table):
        to_table = on_columns[0][1].table

        yield (to_table, [(
            unaliased_column_name(from_column),
            unaliased_column_name(to_column),
        ) for from_column, to_column in on_columns])


def union_strings(table):
    for other_table, columns in table.info.get('unions', []):
        select_strings = tuple(map(unaliased_column_name, columns))
        yield select_strings, other_table.name, join_strings(other_table)
