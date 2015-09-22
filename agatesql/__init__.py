#!/usr/bin/env python

import agate
from agatesql.table import TableSQL

# Monkeypatch!
agate.Table.monkeypatch(TableSQL)
