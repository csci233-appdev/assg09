import os
import pytest
import sqlite3
from q01 import setup_student_info_database
from q01 import clear_student_info_database

def table_exists(dbfile, table):
    """Helper test function, checks if indicated table exists and returns
    true if it does and false if not"""
    # we will need a database connection to test with
    conn = sqlite3.connect(dbfile)
    cur = conn.cursor()

    # check that Majors table exists, for some reason the type="table" is case sensitive here
    # but count should be 1 if the table is in the sqlite_master 
    sql = '''SELECT COUNT(*) FROM sqlite_master WHERE type="table" and name=?'''
    cur.execute(sql, (table,))
    res = cur.fetchone()[0]
    conn.close()

    return res == 1

def column_exists(dbfile, table, column, type):
    """Helper function to check that a column exists in the given table, and that the column
    is of the indicated type.
    """
    # we will need a database connection to test with
    conn = sqlite3.connect(dbfile)
    cur = conn.cursor()

    # use pragma command on the table_info from sqlite to get a list of all columns
    sql = f'''PRAGMA table_info({table})'''
    cur.execute(sql)
    col_list = cur.fetchall()
    conn.close()

    # search for the asked for table
    for (_, column_name, column_type, _, _, _) in col_list:
        if column_name == column and column_type == type:
            return True
    # if we fail the search, the answer is false, the column does not correctly exist
    return False

def foreign_key_exists(dbfile, table, foreign_table, foreign_key):
    """Helper function to test if foreign key relationships have been correctly
    defined and exist in a table for a given column.
    """
    # we will need a database connection to test with
    conn = sqlite3.connect(dbfile)
    cur = conn.cursor()

    # first an extra check on this table, this will cause an exception if the
    # foreign key(s) constraints are violated
    sql = f'''PRAGMA foreign_key_check({table})'''
    cur.execute(sql)

    # use pragma command on the table_info from sqlite to get a list of all foreign key columns
    sql = f'''PRAGMA foreign_key_list({table})'''
    cur.execute(sql)
    col_list = cur.fetchall()
    conn.close()

    # search for the asked for foreign key to confirm it is defined
    for (_, _, column_foreign_table, column_foreign_key, _, _, _, _) in col_list:
        if column_foreign_table == foreign_table and column_foreign_key == foreign_key:
            return True

    # if we fail the search, the answer is false, the table does not have the needed
    # foreign key
    return False

def database_setup_correctly(dbfile):
    """Helper function that tests all expected tables, columns and foreign keys
    are present in the indicated database file.  This is a separate function so that
    the actual pytest tests can create and recreate and check database correctness
    multiple times
    """
    # was the asked for database file created
    assert os.path.exists(dbfile)

    # do the 3 tables exist that we expect
    assert table_exists(dbfile, 'Majors')
    assert not table_exists(dbfile, 'Major')
    assert table_exists(dbfile, 'Departments')
    assert not table_exists(dbfile, 'Department')
    assert table_exists(dbfile, 'Students')
    assert not table_exists(dbfile, 'Student')

    # check that the Majors table has expected columns
    assert column_exists(dbfile, 'Majors', 'MajorID', 'INTEGER')
    assert column_exists(dbfile, 'Majors', 'Name', 'TEXT')

    # check that the Departments table has expected columns
    assert column_exists(dbfile, 'Departments', 'DeptID', 'INTEGER')
    assert column_exists(dbfile, 'Departments', 'Name', 'TEXT')

    # check that the Students table has expected columns
    assert column_exists(dbfile, 'Students', 'StudentID', 'INTEGER')
    assert column_exists(dbfile, 'Students', 'Name', 'TEXT')
    assert column_exists(dbfile, 'Students', 'MajorID', 'INTEGER')
    assert column_exists(dbfile, 'Students', 'DeptID', 'INTEGER')

    # check that the Students table has expected foreign keys defined
    assert foreign_key_exists(dbfile, 'Students', 'Majors', 'MajorID')
    assert foreign_key_exists(dbfile, 'Students', 'Departments', 'DeptID')

    return True

def test_setup_student_info_database():
    # ensure no old test file exists before here, we need the database
    # file to be created and setup from scratch for this test
    dbfile = 'test/data/test.db'
    if os.path.exists(dbfile):
        os.remove(dbfile)

    # call setup function to create database
    setup_student_info_database(dbfile)

    # check that full database has been setup correctly
    assert database_setup_correctly(dbfile)

    # clean up after tests finish
    os.remove(dbfile)

def test_setup_is_idempotent():
    # ensure no old test file exists before here, we need the database
    # file to be created and setup from scratch for this test
    dbfile = 'test/data/test.db'
    if os.path.exists(dbfile):
        os.remove(dbfile)

    # call setup function to create database
    setup_student_info_database(dbfile)

    # second call should not cause any exceptions or problems when the
    # database exists
    setup_student_info_database(dbfile)

    # check that full database has been setup correctly
    assert database_setup_correctly(dbfile)

    # clean up after tests finish
    os.remove(dbfile)

def test_clear_student_info_database():
    # ensure no old test file exists before here, we need the database
    # file to be created and setup from scratch for this test
    dbfile = 'test/data/test.db'
    if os.path.exists(dbfile):
        os.remove(dbfile)

    # call setup function to create database
    setup_student_info_database(dbfile)

    # add some data to each table
    conn = sqlite3.connect(dbfile)
    cur = conn.cursor()

    sql = f'''INSERT INTO Majors (MajorID, Name)
                 VALUES          (1,       "B.S. Computer Science")'''
    cur.execute(sql)

    sql = f'''INSERT INTO Departments (DeptID, Name)
                 VALUES               (2,      "Computer Science and Information Systems")'''
    cur.execute(sql)

    sql = f'''INSERT INTO Students (StudentId, Name,          MajorID, DeptID)
                 VALUES            (1,         "Joe Student", 1,       2)'''
    cur.execute(sql)

    conn.commit()

    # check we have 1 row in each table fore we clear
    sql = f'''SELECT Name FROM Majors'''
    cur.execute(sql)
    rows = cur.fetchall()
    assert len(rows) == 1

    sql = f'''SELECT Name FROM Departments'''
    cur.execute(sql)
    rows = cur.fetchall()
    assert len(rows) == 1

    sql = f'''SELECT Name FROM Students'''
    cur.execute(sql)
    rows = cur.fetchall()
    assert len(rows) == 1

    # clear the database and check it is setup properly
    clear_student_info_database(dbfile)
    assert database_setup_correctly(dbfile)

    # test that tables are empty after being cleared
    sql = f'''SELECT Name FROM Majors'''
    cur.execute(sql)
    rows = cur.fetchall()
    assert len(rows) == 0

    sql = f'''SELECT Name FROM Departments'''
    cur.execute(sql)
    rows = cur.fetchall()
    assert len(rows) == 0

    sql = f'''SELECT Name FROM Students'''
    cur.execute(sql)
    rows = cur.fetchall()
    assert len(rows) == 0

    # clean up after tests finish
    conn.close()
    os.remove(dbfile)

