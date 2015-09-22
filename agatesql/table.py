#!/usr/bin/env python

import agate
from sqlalchemy import Column, MetaData, Table, create_engine
from sqlalchemy.engine import Connection
from sqlalchemy.types import *
from sqlalchemy.sql import select

SQL_TYPE_MAP = {
    agate.Boolean: BOOLEAN,
    agate.Number: DECIMAL,
    agate.Date: DATE,
    agate.DateTime: DATETIME,
    agate.Text: VARCHAR
}

class TableSQL(object):
    @classmethod
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
            sql_type = type(sql_column.type)

            if sql_type in [BIGINT, DECIMAL, FLOAT, INTEGER, NUMERIC, REAL, SMALLINT]:
                column_types.append(agate.Number())
            elif sql_type is BOOLEAN:
                column_types.append(agate.Boolean())
            elif sql_type in [CHAR, NCHAR, VARCHAR, NVARCHAR]:
                column_types.append(agate.Text())
            elif sql_type is DATE:
                column_types.append(agate.Date())
            elif sql_type is DATETIME:
                column_types.append(agate.DateTime())
            else:
                raise ValueError('Unsupported sqlalchemy column type: %s' % sql_type)

        s = select([sql_table])

        rows = connection.execute(s)

        return agate.Table(rows, zip(column_names, column_types))

    def _make_sql_column(self, column_name, column_type):
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

    def to_sql(self, connection_or_string, table_name):
        """
        Write this table to the given SQL database.

        Monkey patched as instance method :meth:`Table.to_sql`.

        :param connection_or_string: An existing sqlalchemy connection or a
            connection string.
        :param table_name: The name of the SQL table to create.
        """
        if isinstance(connection_or_string, Connection):
            connection = connection_or_string
        else:
            engine = create_engine(connection_or_string)
            connection = engine.connect()

        metadata = MetaData(connection)
        sql_table = Table(table_name, metadata)

        for column_name, column_type in zip(self.column_names, self.column_types):
            sql_table.append_column(self._make_sql_column(column_name, column_type))

        sql_table.create()

        insert = sql_table.insert()
        connection.execute(insert, [dict(zip(self.column_names, row)) for row in self.rows])
