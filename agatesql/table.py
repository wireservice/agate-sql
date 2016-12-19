#!/usr/bin/env python

"""
This module contains the agatesql extensions to
:class:`Table <agate.table.Table>`.
"""

import decimal
import datetime
import six
import agate
from sqlalchemy import Column, MetaData, Table, create_engine
from sqlalchemy.engine import Connection
from sqlalchemy.types import BOOLEAN, DECIMAL, DATE, DATETIME, VARCHAR, Interval
from sqlalchemy.dialects.oracle import INTERVAL as ORACLE_INTERVAL
from sqlalchemy.dialects.postgresql import INTERVAL as POSTGRES_INTERVAL
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

def from_sql(cls, connection_or_string, table_name):
    """
    Create a new :class:`agate.Table` from a given SQL table. Types will be
    inferred from the database schema.

    Monkey patched as class method :meth:`Table.from_sql`.

    :param connection_or_string: An existing sqlalchemy connection or a
        connection string.
    :param table_name: The name of a table in the referenced database.
    """
    if isinstance(connection_or_string, Connection):
        connection = connection_or_string
    else:
        engine = create_engine(connection_or_string)
        connection = engine.connect()

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

def make_sql_column(column_name, column_type):
    """
    Creates a sqlalchemy column from agate column data.

    :param column_name: The name of the new column.
    :param column_type: The agate type of the column.
    """
    sql_column_type = None

    for agate_type, sql_type in SQL_TYPE_MAP.items():
        if isinstance(column_type, agate_type):
            sql_column_type = sql_type
            break

    if sql_column_type is None:
        raise ValueError('Unsupported column type: %s' % column_type)

    return Column(column_name, sql_column_type())

def to_sql(self, connection_or_string, table_name, overwrite=False):
    """
    Write this table to the given SQL database.

    Monkey patched as instance method :meth:`Table.to_sql`.

    :param connection_or_string:
        An existing sqlalchemy connection or a connection string.
    :param table_name:
        The name of the SQL table to create.
    :param overwrite:
        If ``True``, any existing table with the same name will be dropped
        and recreated.
    """
    if isinstance(connection_or_string, Connection):
        connection = connection_or_string
    else:
        engine = create_engine(connection_or_string)
        connection = engine.connect()

    dialect = connection.engine.dialect.name
    metadata = MetaData(connection)
    sql_table = Table(table_name, metadata)

    if dialect in INTERVAL_MAP.keys():
        SQL_TYPE_MAP[agate.TimeDelta] = INTERVAL_MAP[dialect]
    else:
        SQL_TYPE_MAP[agate.TimeDelta] = Interval

    for column_name, column_type in zip(self.column_names, self.column_types):
        sql_table.append_column(make_sql_column(column_name, column_type))

    if overwrite:
        sql_table.drop(checkfirst=True)

    sql_table.create()

    insert = sql_table.insert()
    connection.execute(insert, [dict(zip(self.column_names, row)) for row in self.rows])

agate.Table.from_sql = classmethod(from_sql)
agate.Table.to_sql = to_sql
