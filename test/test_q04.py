import pytest
import subprocess
import os

def test_departments_crud_application():
    dbfile = 'test/data/student_info.db'
    if os.path.exists(dbfile):
        os.remove(dbfile)

    # we rerun the Majors and Departments CRUD tests here to create
    # a database with a known major and department in it
    command = ['python3', 'test/test-question.py', 'majors_crud.py']
    result = subprocess.run(command)
    assert result.returncode == 0
    
    command = ['python3', 'test/test-question.py', 'departments_crud.py']
    result = subprocess.run(command)
    assert result.returncode == 0

    assert os.path.exists(dbfile)

    # now run the Students CRUD application tests
    command = ['python3', 'test/test-question.py', 'students_crud.py']
    result = subprocess.run(command)
    assert result.returncode == 0

    # clean up after tests
    os.remove(dbfile)