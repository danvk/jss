from nose.tools import *

import glob
import json
import os
import sys

import jss


def load_commented_json(path):
    lines = open(path).read().split('\n')
    return json.loads('\n'.join(
        [line for line in lines if not line.startswith('#')]))


def test_all():
    specs = glob.glob('tests/data/*.spec')
    for idx, spec in enumerate(specs):
        sys.stderr.write('%2d %s\n' % (idx, spec))
        args = load_commented_json(spec)
        expected = open(spec.replace('.spec', '.out.json')).read().decode('utf8')
        actual = jss.run(args)

        if expected != actual:
            open('/tmp/expected.json', 'w').write(expected.encode('utf8'))
            open('/tmp/actual.json', 'w').write(actual.encode('utf8'))

        eq_(expected, actual)
