#!/usr/bin/env python
# -*- coding: utf8 -*-

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import agate
import agatesql
from sqlalchemy import create_engine

agatesql.patch()

class TestSQL(unittest.TestCase):
    def setUp(self):
        self.rows = (
            (1, 'a'),
            (2, 'b'),
            (None, None)
        )

        self.number_type = agate.Number()
        self.text_type = agate.Text()

        self.column_names = ('one', 'two')
        self.column_types = (self.number_type, self.text_type)

        self.table = agate.Table(self.rows, zip(self.column_names, self.column_types))
        self.connection_string = 'sqlite:///:memory:'

    def test_sql(self):
        engine = create_engine(self.connection_string)
        connection = engine.connect()

        self.table.to_sql(connection, 'test')

        table = agate.Table.from_sql(connection, 'test')

        self.assertSequenceEqual(table.column_names, self.column_names)
        self.assertIsInstance(table.column_types[0], agate.Number)
        self.assertIsInstance(table.column_types[1], agate.Text)

        self.assertEqual(len(table.rows), len(self.table.rows))
        self.assertSequenceEqual(table.rows[0], self.table.rows[0])
