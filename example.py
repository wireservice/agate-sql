#!/usr/bin/env python

import agate
import agatesql

agatesql.patch()

table = agate.Table.from_sql('postgresql:///pa-sentencing', 'subset')

print(table.column_names)
print(table.column_types)
print(len(table.columns))
print(len(table.rows))

table.to_sql('postgresql:///pa-sentencing', 'foo')
