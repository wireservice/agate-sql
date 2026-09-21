===================
agate-sql |release|
===================

.. include:: ../README.rst

Install
=======

To install:

.. code-block:: bash

    pip install agate-sql

For details on development or supported platforms see the `agate documentation <https://agate.readthedocs.org>`_.

.. warning::

    You'll need to have the correct `SQLAlchemy drivers <https://docs.sqlalchemy.org/en/20/dialects/index.html>`_ installed for whatever database you plan to access. For instance, in order to read/write tables in a PostgreSQL database, you'll also need to ``pip install psycopg2``.

    agate-sql supports all `included dialects <https://docs.sqlalchemy.org/en/20/dialects/index.html#included-dialects>`__. It is known to work with these `external dialects <https://docs.sqlalchemy.org/en/20/dialects/index.html#external-dialects>`__: CrateDB, Ingres.

Usage
=====

agate-sql uses a monkey patching pattern to add SQL support to all :class:`agate.Table <agate.table.Table>` instances.

.. code-block:: python

    import agate
    import agatesql

Importing :mod:`.agatesql` attaches new methods to :class:`agate.Table <agate.table.Table>`. For example, to import a table named :code:`doctors` from a local PostgreSQL database named :code:`hospitals` you will use :meth:`.from_sql`:

.. code-block:: python

    new_table = agate.Table.from_sql('postgresql:///hospitals', 'doctors')

To save this table back to the database:

.. code-block:: python

    new_table.to_sql('postgresql:///hospitals', 'doctors')

The first argument to either function can be any valid `sqlalchemy connection string <https://docs.sqlalchemy.org/en/rel_1_0/core/engines.html>`_. The second argument must be a database name. (Arbitrary SQL queries are not supported.)

That's all there is to it.

Transactions
------------

When passed a connection string, :meth:`.to_sql` commits its writes on success
and rolls them back on error, then closes its connection. When passed an existing
SQLAlchemy connection, it leaves transaction management and connection cleanup
to the caller. For example, to commit multiple writes together:

.. code-block:: python

    from sqlalchemy import create_engine

    engine = create_engine('postgresql:///hospitals')
    with engine.begin() as connection:
        doctors.to_sql(connection, 'doctors')
        departments.to_sql(connection, 'departments')

Database-specific restrictions on transactional DDL still apply when creating
or replacing tables.

===
API
===

.. autofunction:: agatesql.table.from_sql

.. autofunction:: agatesql.table.from_sql_query

.. autofunction:: agatesql.table.to_sql

.. autofunction:: agatesql.table.to_sql_create_statement

.. autofunction:: agatesql.table.sql_query

Authors
=======

.. include:: ../AUTHORS.rst

Changelog
=========

.. include:: ../CHANGELOG.rst

License
=======

.. include:: ../COPYING

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
