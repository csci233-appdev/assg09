import pytest
import subprocess
import os

def test_departments_crud_application():
    dbfile = 'test/data/student_info.db'
    if os.path.exists(dbfile):
        os.remove(dbfile)

    command = ['python3', 'test/test-question.py', 'departments_crud.py']
    result = subprocess.run(command)
    assert result.returncode == 0

    assert os.path.exists(dbfile)

    # clean up after tests
    os.remove(dbfile)