#! /opt/local/bin/python

''' --------------------------------------------------------------------------------------------
Script: sql-proc.py -- Run an sql script within it's own context.
Author: Christopher Sean Hilton
  Date: 2016-05-02 12:00 EDT

Generate a sql connection to a database and run a script specified in the arguments.
-------------------------------------------------------------------------------------------- '''

import getpass, sys

import psycopg2 as db

def build_dsn(**kwargs):

    dsn = { }
    for dsn_param in ('database', 'host', 'user', 'password', ):
        try:
            val = kwargs.pop(dsn_param)
            dsn[dsn_param] = val
        except KeyError:
            pass

    return kwargs, dsn

def main(*args, **kwargs):

    ret_value = 75 ## Assume we can't even connect.
    
    ## Iterate through the keyword args searching for the DSN
    ## parameters inclusively. Save the ones you get into a new dict()
    ## for the call to connect.

    kwargs, dsn = build_dsn(**kwargs)

    conn_err = None
    connected = False
    try:
        gsdb = db.connect(**dsn)
        curs = gsdb.cursor()
        curs.execute("set client_min_messages = 'log'")
        connected = True

    except db.Error as conn_err:
        print "Error connecting to the database: (%s) - %s" % (conn_err.pgcode, conn_err.pgerror)

    if connected:
        ## If we get this far, assume the query fails.

        ret_value = 1
        query_err = None
        success = False
        try:
            query  = "SELECT %s" % (" ".join(args),)

            res = curs.execute(query)
            success = True
            ret_value = 0

        except db.Error as query_err:
            pass

        finally:
            if gsdb.notices:
                print "Notify: ".join(gsdb.notices)

            curs.close()
            gsdb.close()

        if not success:
            print "Error in query: (%s) - %s" % (query_err.pgcode, query_err.pgerror)

    return ret_value

if __name__ == '__main__':

    from getopt import getopt, GetoptError

    host = 'localhost'
    user = getpass.getuser()
    password = None
    database = None
    
    try:
        opts, args = getopt(sys.argv[1:], 'H:U:P:D:', ('host=',
                                                       'user=',
                                                       'password=',
                                                       'database='))
        for o, a in opts:
            if o in ('-H', "--host"):
                host = str(a)
            elif o in ('-U', "--user"):
                user = str(a)
            elif o in ('-P', "--password"):
                password = str(a)
            elif o in ('-D', "--database"):
                database = str(a)
                
        if database is None:
            database = user

        kwargs = locals().copy()

        sys.exit(main(*args, **kwargs))

    except GetoptError, e:
        print >> sys.stderr, "%s\n" % e
        
