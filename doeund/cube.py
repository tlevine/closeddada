'''
Group the fact table's columns into two categories

References
    Foreign keys that reference dimensions
Measures
    Not foreign keys, which are each dimensions themselves

(The primary key will fall into one of these categories.)

Group each dimension's columns into three categories.

Primary keys
    Primary keys on this table
Foreign keys
    References to another dimension table
Levels
    Everything else

Treat the levels as components of the dimension.


Slicing and dicing

* point_cut
* set_cut
* range_cut

Drill up, drill down
http://pythonhosted.org/cubes/recipes/drilldown_tree.html

Roll up
http://pythonhosted.org/cubes/slicing_and_dicing.html#aggregate

What's pivot for???

'''
from collections import OrderedDict
import re
import itertools
from functools import partial

from sqlalchemy import and_, or_
from .inference import dim_levels, fact_measures, joins

class Dimension:
    def __init__(self, query, hierarchy):
        self._query = query
        self.hierarchy = hierarchy

    def levels(self, *path):
        query = self._query
        if len(path) == 0:
            columns = self.hierarchy
        else:
            columns, _ = zip(*zip(self.hierarchy, path))
        for record in query.group_by(*columns):
            yield tuple(*(getattr(record, column.name) for column in columns))

class Cube:
    def __init__(self, session, fact_table):
        '''
        fact_table: a Fact class
        '''
        self._args = (session, fact_table)

        # A dictionary of string keys and list-of-Column-object values,
        # traversing recursively into the full snowflake of dimensions
        dimensions = fact_measures(fact_table)
        self.responses = list(dimensions.keys())

        # Flatten the table, and record dimensions
        self._query = session.query(fact_table)
        tables = [fact_table]
        while len(tables) > 0:
            for from_column, to_column in joins(tables.pop()):
                to_table = to_column.table

                self._query = self._query.join(to_table, from_column == to_column)

                dim_name = re.sub(r'^dim_', '', to_table.name)
                dimensions[dim_name] = dim_levels(to_table)

                tables.append(to_table)
        self.dimensions = OrderedDict((key,
            Dimension(self._query, hierarchy))\
            for key, hierarchy in dimensions.items())

    def __repr__(self):
        return '<Cube for table "%s">' % self._args[1]

    def dice(self, dimension, *paths):
        def match_path(dimension, path):
            # An AND-joined query to match the full path
            return and_(*(level == value for level, value in \
                          zip(dimension, path)))

        # An OR-joined query to match any of the paths
        filter_criteria = or_(*map(partial(match_path, dimension), paths))

        # Apply the criteria
        return self._query.filter(filter_criteria)

    def roll_up(self, dimensions, *aggregations):
        '''
        Like this ::

            .rollup({'date': 2, # year, month
                     'time': None, # as many levels as there are
                    }, doeund.rollups.count('pk'))
        '''
        subcube_hierarchies = OrderedDict()
        for key, n in dimensions.items():
            if n:
                sub_hierarchy = self.dimensions[key].hierarchy[:n]
            else:
                sub_hierarchy = self.dimensions[key].hierarchy
            subcube_hierarchies[key] = sub_hierarchy

        groupings = itertools.chain(*subcube_hierarchies.values())
        query = self._query.group_by(*groupings)

        subcube = Cube(*self._args)
        subcube.dimensions = OrderedDict((key,
            Dimension(query, hierarchy))\
            for key, hierarchy in subcube_hierarchies.items())
        return subcube
