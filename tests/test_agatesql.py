#!/usr/bin/env python
# -*- coding: utf8 -*-

from decimal import Decimal

import agate
import agatesql  # noqa
from sqlalchemy import create_engine


class TestSQL(agate.AgateTestCase):
    def setUp(self):
        self.rows = (
            (1.123, 'a', True, '11/4/2015', '11/4/2015 12:22 PM'),
            # See issue #18
            # (2, u'👍', False, '11/5/2015', '11/4/2015 12:45 PM'),
            (2, u'c', False, '11/5/2015', '11/4/2015 12:45 PM'),
            (None, 'b', None, None, None)
        )

        self.column_names = [
            'number', 'text', 'boolean', 'date', 'datetime'
        ]

        self.column_types = [
            agate.Number(), agate.Text(), agate.Boolean(),
            agate.Date(), agate.DateTime()
        ]

        self.table = agate.Table(self.rows, self.column_names, self.column_types)
        self.connection_string = 'sqlite:///:memory:'

    def test_back_and_forth(self):
        engine = create_engine(self.connection_string)
        connection = engine.connect()

        self.table.to_sql(connection, 'test')

        table = agate.Table.from_sql(connection, 'test')

        self.assertSequenceEqual(table.column_names, self.column_names)
        self.assertIsInstance(table.column_types[0], agate.Number)
        self.assertIsInstance(table.column_types[1], agate.Text)
        self.assertIsInstance(table.column_types[2], agate.Boolean)
        self.assertIsInstance(table.column_types[3], agate.Date)
        self.assertIsInstance(table.column_types[4], agate.DateTime)

        self.assertEqual(len(table.rows), len(self.table.rows))
        self.assertSequenceEqual(table.rows[0], self.table.rows[0])

    def test_create_if_not_exists(self):
        column_names = ['id', 'name']
        column_types = [agate.Number(), agate.Text()]
        rows1 = (
            (1, 'Jake'),
            (2, 'Howard'),
        )
        rows2 = (
            (3, 'Liz'),
            (4, 'Tim'),
        )

        table1 = agate.Table(rows1, column_names, column_types)
        table2 = agate.Table(rows2, column_names, column_types)

        engine = create_engine(self.connection_string)
        connection = engine.connect()

        # Write two agate tables into the same SQL table
        table1.to_sql(connection, 'create_if_not_exists_test', create=True, create_if_not_exists=True, insert=True)
        table2.to_sql(connection, 'create_if_not_exists_test', create=True, create_if_not_exists=True, insert=True)

    def test_to_sql_create_statement(self):
        statement = self.table.to_sql_create_statement('test_table')

        self.assertIn('CREATE TABLE test_table', statement)
        self.assertIn('number DECIMAL,', statement)
        self.assertIn('text VARCHAR(1) NOT NULL,', statement)
        self.assertIn('boolean BOOLEAN,', statement)
        self.assertIn('date DATE,', statement)
        self.assertIn('datetime TIMESTAMP', statement)

    def test_to_sql_create_statement_no_constraints(self):
        statement = self.table.to_sql_create_statement('test_table', constraints=False)

        self.assertIn('CREATE TABLE test_table', statement)
        self.assertIn('number DECIMAL,', statement)
        self.assertIn('text VARCHAR,', statement)
        self.assertIn('boolean BOOLEAN,', statement)
        self.assertIn('date DATE,', statement)
        self.assertIn('datetime TIMESTAMP', statement)

    def test_to_sql_create_statement_with_schema(self):
        statement = self.table.to_sql_create_statement('test_table', db_schema='test_schema', dialect='mysql')

        self.assertIn('CREATE TABLE test_schema.test_table', statement)
        self.assertIn('number DECIMAL(38, 3),', statement)
        self.assertIn('text VARCHAR(1) NOT NULL,', statement)
        self.assertIn('boolean BOOL,', statement)
        self.assertIn('date DATE,', statement)
        self.assertIn('datetime TIMESTAMP', statement)

    def test_to_sql_create_statement_with_dialects(self):
        for dialect in ['mysql', 'postgresql', 'sqlite']:
            self.table.to_sql_create_statement('test_table', dialect=dialect)

    def test_to_sql_create_statement_zero_width(self):
        rows = (
            (1, ''),
            (2, ''),
        )
        column_names = ['id', 'name']
        column_types = [agate.Number(), agate.Text()]

        table = agate.Table(rows, column_names, column_types)

        statement = table.to_sql_create_statement('test_table', db_schema='test_schema', dialect='mysql')

        self.assertIn('CREATE TABLE test_schema.test_table', statement)
        self.assertIn('id DECIMAL(38, 0) NOT NULL,', statement)
        self.assertIn('name VARCHAR(1)', statement)

    def test_sql_query_simple(self):
        results = self.table.sql_query('select * from agate')

        self.assertColumnNames(results, self.table.column_names)
        self.assertRows(results, self.table.rows)

    def test_sql_query_limit(self):
        results = self.table.sql_query('select * from agate limit 2')

        self.assertColumnNames(results, self.table.column_names)
        self.assertRows(results, self.table.rows[:2])

    def test_sql_query_select(self):
        results = self.table.sql_query('select number, boolean from agate')

        self.assertColumnNames(results, ['number', 'boolean'])
        self.assertColumnTypes(results, [agate.Number, agate.Boolean])
        self.assertRows(results, [
            [Decimal('1.123'), True],
            [2, False],
            [None, None]
        ])

    def test_sql_query_aggregate(self):
        results = self.table.sql_query('select sum(number) as total from agate')

        self.assertColumnNames(results, ['total'])
        self.assertColumnTypes(results, [agate.Number])
        self.assertRows(results, [[Decimal('3.123')]])

    def test_chunksize(self):
        column_names = ['number']
        column_types = [agate.Number()]

        n = 9999
        rows = []
        ref_total = 0
        for k in range(n):
            rows.append((k,))
            ref_total += k

        engine = create_engine(self.connection_string)
        connection = engine.connect()

        try:
            for chunksize in [11, 100, 9, 231]:
                # insert data with chunksize
                table = agate.Table(rows, column_names, column_types)
                table.to_sql(connection, 'test_chunksize', overwrite=True, chunksize=chunksize)

                table = agate.Table.from_sql(connection, 'test_chunksize')
                total = 0
                for r in table.rows:
                    total += int(r[0])
                self.assertEqual(len(table.rows), len(rows), "Number of rows")
                self.assertEqual(ref_total, total, "Sum of all values")
        finally:
            connection.close()
            engine.dispose()

