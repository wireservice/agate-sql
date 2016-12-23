#!/usr/bin/env python

"""
This module contains the agatesql extensions to
:class:`Table <agate.table.Table>`.
"""

import decimal
import datetime
import six
import agate
from sqlalchemy import Column, MetaData, Table, create_engine, dialects
from sqlalchemy.engine import Connection
from sqlalchemy.types import BOOLEAN, DECIMAL, DATE, DATETIME, VARCHAR, Interval
from sqlalchemy.dialects.oracle import INTERVAL as ORACLE_INTERVAL
from sqlalchemy.dialects.postgresql import INTERVAL as POSTGRES_INTERVAL
from sqlalchemy.schema import CreateTable
from sqlalchemy.sql import select

SQL_TYPE_MAP = {
    agate.Boolean: BOOLEAN,
    agate.Number: DECIMAL,
    agate.Date: DATE,
    agate.DateTime: DATETIME,
    agate.TimeDelta: None,  # See below
    agate.Text: VARCHAR
}

INTERVAL_MAP = {
    'postgresql': POSTGRES_INTERVAL,
    'oracle': ORACLE_INTERVAL
}

def get_connection(connection_or_string=None):
    """
    Gets a connection to a specific SQL alchemy backend. If an existing
    connection is provided, it will be passed through. If no connection
    string is provided, then in in-memory SQLite database will be created.
    """
    if connection_or_string is None:
        engine = create_engine('sqlite:///:memory:')
        connection = engine.connect()
    elif isinstance(connection_or_string, Connection):
        connection = connection_or_string
    else:
        engine = create_engine(connection_or_string)
        connection = engine.connect()

    return connection

def from_sql(cls, connection_or_string, table_name):
    """
    Create a new :class:`agate.Table` from a given SQL table. Types will be
    inferred from the database schema.

    Monkey patched as class method :meth:`Table.from_sql`.

    :param connection_or_string:
        An existing sqlalchemy connection or connection string.
    :param table_name:
        The name of a table in the referenced database.
    """
    connection = get_connection(connection_or_string)

    metadata = MetaData(connection)
    sql_table = Table(table_name, metadata, autoload=True, autoload_with=connection)

    column_names = []
    column_types = []

    for sql_column in sql_table.columns:
        column_names.append(sql_column.name)

        if type(sql_column.type) in INTERVAL_MAP.values():
            py_type = datetime.timedelta
        else:
            py_type = sql_column.type.python_type

        if py_type in [int, float, decimal.Decimal]:
            if py_type is float:
                sql_column.type.asdecimal = True
            column_types.append(agate.Number())
        elif py_type is bool:
            column_types.append(agate.Boolean())
        elif issubclass(py_type, six.string_types):
            column_types.append(agate.Text())
        elif py_type is datetime.date:
            column_types.append(agate.Date())
        elif py_type is datetime.datetime:
            column_types.append(agate.DateTime())
        elif py_type is datetime.timedelta:
            column_types.append(agate.TimeDelta())
        else:
            raise ValueError('Unsupported sqlalchemy column type: %s' % type(sql_column.type))

    s = select([sql_table])

    rows = connection.execute(s)

    return agate.Table(rows, column_names, column_types)

def from_sql_query(self, query):
    """
    Create an agate table from the results of a SQL query. Note that column
    data types will be inferred from the returned data, not the column types
    declared in SQL (if any). This is more flexible than :func:`.from_sql` but
    could result in unexpected typing issues.

    :param query:
        A SQL query to execute.
    """
    connection = get_connection()

    # Must escape '%'.
    # @see https://github.com/wireservice/csvkit/issues/440
    # @see https://bitbucket.org/zzzeek/sqlalchemy/commits/5bc1f17cb53248e7cea609693a3b2a9bb702545b
    rows = connection.execute(query.replace('%', '%%'))

    table = agate.Table(list(rows), column_names=rows._metadata.keys)

    return table

def make_sql_column(column_name, column, sql_type_kwargs=None, sql_column_kwargs=None):
    """
    Creates a sqlalchemy column from agate column data.

    :param column_name:
        The name of the column.
    :param column:
        The agate column.
    :param sql_column_kwargs:
        Additional kwargs to passed through to the Column constructor, such as
        ``nullable``.
    """
    sql_column_type = None

    for agate_type, sql_type in SQL_TYPE_MAP.items():
        if isinstance(column.data_type, agate_type):
            sql_column_type = sql_type
            break

    if sql_column_type is None:
        raise ValueError('Unsupported column type: %s' % column_type)

    sql_type_kwargs = sql_type_kwargs or {}
    sql_column_kwargs = sql_column_kwargs or {}

    return Column(column_name, sql_column_type(**sql_type_kwargs), **sql_column_kwargs)

def make_sql_table(table, table_name, dialect=None, db_schema=None, constraints=True, connection=None):
    """
    Generates a SQL alchemy table from an agate table.
    """
    metadata = MetaData(connection)
    sql_table = Table(table_name, metadata, schema=db_schema)

    if dialect in INTERVAL_MAP.keys():
        SQL_TYPE_MAP[agate.TimeDelta] = INTERVAL_MAP[dialect]
    else:
        SQL_TYPE_MAP[agate.TimeDelta] = Interval

    for column_name, column in table.columns.items():
        sql_type_kwargs = {}
        sql_column_kwargs = {}

        if constraints:
            if isinstance(column.data_type, agate.Text):
                sql_type_kwargs['length'] = table.aggregate(agate.MaxLength(column_name))

            sql_column_kwargs['nullable'] = table.aggregate(agate.HasNulls(column_name))

        sql_table.append_column(make_sql_column(column_name, column, sql_type_kwargs, sql_column_kwargs))

    return sql_table

def to_sql(self, connection_or_string, table_name, overwrite=False, create=True, insert=True, db_schema=None, constraints=True):
    """
    Write this table to the given SQL database.

    Monkey patched as instance method :meth:`Table.to_sql`.

    :param connection_or_string:
        An existing sqlalchemy connection or a connection string.
    :param table_name:
        The name of the SQL table to create.
    :param overwrite:
        Drop any existing table with the same name before creating.
    :param create:
        Create the table.
    :param insert:
        Insert table data.
    :param db_schema:
        Create table in the specified database schema.
    :param constraints
        Generate constraints such as ``nullable`` for table columns.
    """
    connection = get_connection(connection_or_string)

    dialect = connection.engine.dialect.name
    sql_table = make_sql_table(self, table_name, dialect=dialect, db_schema=db_schema, constraints=constraints, connection=connection)

    if create:
        if overwrite:
            sql_table.drop(checkfirst=True)

        sql_table.create()

    if insert:
        insert = sql_table.insert()
        connection.execute(insert, [dict(zip(self.column_names, row)) for row in self.rows])

    return sql_table

def to_sql_create_statement(self, table_name, dialect=None, db_schema=None, constraints=True):
    """
    Generates a CREATE TABLE statement for this SQL table, but does not execute
    it.

    :param table_name:
        The name of the SQL table to create.
    :param dialect:
        The dialect of SQL to use for the table statement.
    :param db_schema:
        Create table in the specified database schema.
    :param constraints
        Generate constraints such as ``nullable`` for table columns.
    """
    sql_table = make_sql_table(self, table_name, dialect=dialect, db_schema=db_schema, constraints=constraints)

    if dialect:
        sql_dialect = dialects.registry.load(dialect)()
    else:
        sql_dialect = None

    return six.text_type(CreateTable(sql_table).compile(dialect=sql_dialect)).strip() + ';'

def sql_query(self, query, table_name='agate'):
    """
    Convert this agate table into an intermediate, in-memory sqlite table,
    run a query against it, and then return the results as a new agate table.

    Multiple queries may be separated with semicolons.

    :param query:
        One SQL query, or multiple queries to be run consecutively separated
        with semicolons.
    :param table_name:
        The name to use for the table in the queries, defaults to ``agate``.
    """
    connection = get_connection()

    # Execute the specified SQL queries
    queries = query.split(';')
    rows = None

    sql_table = self.to_sql(connection, table_name)

    for q in queries:
        if q:
            rows = connection.execute(q)

    table = agate.Table(list(rows), column_names=rows._metadata.keys)

    return table

agate.Table.from_sql = classmethod(from_sql)
agate.Table.from_sql_query = classmethod(from_sql_query)
agate.Table.to_sql = to_sql
agate.Table.to_sql_create_statement = to_sql_create_statement
agate.Table.sql_query = sql_query
