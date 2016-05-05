= sql-proc.py 

Many times when I work for database clients they have standards and
procedures for running periodic processes. People tend to use the
languages that they know so in an environment that uses Oracle or
PostgreSQL, where there's a high degree of SQL talent, procedural
stuff that I might write in python, ruby, or ksh gets written in the
procedural language on the database. Since these guys tend to be very
very savvy with their database, they also eschew syslog and write
their logs into a table on the database. At first blush, this sounds
bad but it's actually a good thing. A shop shouldn't try to have a
shallow knowledge across a broad group of tools. They are better
served by having a deep knowledge across a small toolset. Nonetheless,
sometimes the toolset comes up short. PL/PGSQL in PostgreSQL is an
example here. If a function raises an exception the transaction is
started is totally rolled back and there's no easy way to undo that
and preserve the exception. Furthermore, any new transaction that you
start, say to log the failure in the first place will also be rolled
back. Sigh. The function of this code is to fire one SQL statement,
really a stored procedure call, capture any exception that happens and
respond appropriately. Being written in python it can then open a new
cursor in which to log the exception. It can also return an
appropriate exit code to the shell for proper decision making.
