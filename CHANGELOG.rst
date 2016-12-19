0.4.0
-----

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
