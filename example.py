#!/usr/bin/env python

import agate

import agatesql

table = agate.Table.from_sql('sqlite:///example.db', 'test')

print(table.column_names)
print(table.column_types)
print(len(table.columns))
print(len(table.rows))

table.to_sql('sqlite:///example.db', 'test', overwrite=True)
