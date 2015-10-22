===================
agate-sql |release|
===================

About
=====

.. include:: ../README

Install
=======

To install:

.. code-block:: bash

    pip install agatesql

For details on development or supported platforms see the `agate documentation <http://agate.readthedocs.org>`_.

.. warning::

    You'll need to have the correct `sqlalchemy drivers <http://docs.sqlalchemy.org/en/rel_1_0/dialects/index.html>`_ installed for whatever database you plan to access. For instance, in order to read/write tables in a Postgres database, you'll also need to ``pip install psycopg2``.

Usage
=====

agate-sql uses a monkey patching pattern to add SQL support to all :class:`agate.Table <agate.table.Table>` instances.

.. code-block:: python

    import agate
    import agatesql

    agatesql.patch()

Calling :meth:`patch` attaches all the methods of :meth:`TableSQL` to :class:`agate.Table <agate.table.Table>`. For example, to import a table named :code:`doctors` from a local postgresql database named :code:`hospitals` you will use :meth:`TableSQL.from_sql`:

.. code-block:: python

    new_table = agate.Table.from_sql('postgresql:///hospitals', 'doctors')

To save this table back to the database:

.. code-block:: python

    new_table.to_sql('postgresql:///hospitals', 'doctors')

The first argument to either function can be any valid `sqlalchemy connection string <http://docs.sqlalchemy.org/en/rel_1_0/core/engines.html>`_. The second argument must be a database name. (Arbitrary SQL queries are not supported.)

That's all there is to it.

===
API
===

.. autofunction:: agatesql.patch

.. autoclass:: agatesql.table.TableSQL
    :members:

Authors
=======

.. include:: ../AUTHORS

License
=======

.. include:: ../COPYING

Changelog
=========

.. include:: ../CHANGELOG

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
