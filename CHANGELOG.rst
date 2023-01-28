0.5.9 - Jan 28, 2023
--------------------

* Disallow SQLAlchemy 2.

0.5.8 - September 15, 2021
--------------------------

* Fix tests for Linux packages.

0.5.7 - July 13, 2021
---------------------

* Add wheels distribution.

0.5.6 - March 4, 2021
---------------------

* Fix test that fails in specific environments.

0.5.5 - July 7, 2020
--------------------

* Set type to ``DATETIME`` for datetime (MS SQL).
* Drop support for Python 2.7 (EOL 2020-01-01), 3.4 (2019-03-18), 3.5 (2020-09-13).

0.5.4 - March 16, 2019
----------------------

* Add ``min_col_len`` and ``col_len_multiplier`` options to :meth:`.Table.to_sql` to control the length of text columns.
* agate-sql is now tested against Python 3.7.
* Drop support for Python 3.3 (end-of-life was September 29, 2017).

Dialect-specific:

* Add support for CrateDB.
* Set type to ``BIT`` for boolean (MS SQL).
* Eliminate SQLite warning about Decimal numbers.

0.5.3 - January 28, 2018
------------------------

* Add ``chunk_size`` option to :meth:`.Table.to_sql` to write rows in batches.
* Add ``unique_constraint`` option to :meth:`.Table.to_sql` to include in a UNIQUE constraint.

Dialect-specific:

* Specify precision and scale for ``DECIMAL`` (MS SQL, MySQL, Oracle).
* Set length of ``VARCHAR`` to ``1`` even if maximum length is ``0`` (MySQL).
* Set type to ``TEXT`` if maximum length is greater than 21,844 (MySQL).

0.5.2 - April 28, 2017
----------------------

* Add ``create_if_not_exists`` flag to :meth:`.Table.to_sql`.

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

* Add ``overwrite`` flag to :meth:`.Table.to_sql`.
* Removed Python 2.6 support.
* Updated agate dependency to version 1.1.0.
* Additional SQL types are now supported. (#4, #10)

0.2.0 - October 22, 2015
------------------------

* Add explicit patch function.

0.1.0 - September 22, 2015
--------------------------

* Initial version.
