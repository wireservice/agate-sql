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

Usage
=====

agate-sql uses agate's monkeypatching pattern to automatically add SQL support to all :class:`agate.Table <agate.table.Table>` instances.

.. code-block:: python

    import agate
    import agatesql

Once imported, you'll be able to use :meth:`.TableSQL.from_sql` and :meth:`.TableSQL.to_sql` as though they are members of :class:`agate.Table <agate.table.Table>`.

To import a table named :code:`doctors` from a local postgresql database named :code:`hospitals` you would run:

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
