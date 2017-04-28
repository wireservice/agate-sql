0.5.2 - April 28, 2017
----------------------

* Add ``create_if_not_exists`` flag to :meth:`.TableSQL.to_sql`.

0.5.1 - February 27, 2017
-------------------------

* Add ``prefixes`` option to :func:`.to_sql` to add expressions following the INSERT keyword, like OR IGNORE or OR REPLACE.
* Use ``TIMESTAMP`` instead of ``DATETIME`` for DateTime columns.

0.5.0 - December 23, 2016
-------------------------

* ``VARCHAR`` columns are now generated with proper length constraints (unless explicilty disabled).
* Tables can now be created from query results using :func:`.from_sql_query`.
* Add support for running queries directly on tables with :func:`.sql_query`.
* When creating tables, ``NOT NULL`` constraints will be created by default.
* SQL create statements can now be generated without being executed with :func:`.to_sql_create_statement`

0.4.0 - December 19, 2016
-------------------------

* Modified ``example.py`` so it no longer depends on Postgres.
* It is no longer necessary to run :code:`agatesql.patch()` after importing agatesql.
* Upgrade required agate to ``1.5.0``.

0.3.0 - November 5, 2015
------------------------

* Add ``overwrite`` flag to :meth:`.TableSQL.to_sql`.
* Removed Python 2.6 support.
* Updated agate dependency to version 1.1.0.
* Additional SQL types are now supported. (#4, #10)

0.2.0 - October 22, 2015
------------------------

* Add explicit patch function.

0.1.0 - September 22, 2015
--------------------------

* Initial version.
