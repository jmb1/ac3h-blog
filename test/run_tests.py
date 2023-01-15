import sys
import os
import pytest

test_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(test_root))

print('cwd=%s' % os.getcwd())

retcode = pytest.main(["-x", "./test"])
