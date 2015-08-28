#!/usr/bin/env python
import sys
import os

paths = sys.path[:]
my_location = os.path.split(os.path.dirname(__file__))[0]
lib_path = sorted([(x, len(os.path.commonprefix([x, my_location]))) for x in paths], cmp=lambda x,y: cmp(x[1],y[1]))[-1][0]
sys.path.insert(1,lib_path)

import nose
import biokbase.data_api.tests.test_suite_basic

nose.core.run(module=biokbase.data_api.tests.test_suite_basic)