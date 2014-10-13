#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''jss is a command-line tool for filtering JSON, like jq.

It's based on JSONSelect, a CSS-like language for selecting portions of a JSON
object.

Sample usage:

    # Extract every value whose key is 'foo', printing each on a line.
    jss .foo file.json

    # Remove all keys named 'coordinates' (JSON→JSON transformation)
    jss -v .coordinate file.json

    # Keep only keys named 'metadata' and their ancestors (JSON→JSON)
    jss -k .metadata file.json

    # Keey only keys named 'metadata' and their ancestors where something under
    # the value for 'metadata' contains 'needle':
    jss -k '.metadata:has(.needle)' file.json

For more examples and information, see https://github.com/danvk/jss/.
'''

import json
import os
import sys
import time
from collections import OrderedDict

import jsonselect

DEBUG = False

UNSPECIFIED = 0
KEEP = 1
DELETE = 2


def selector_to_ids(selector, obj, mode):
    def bail_on_match(obj, matches):
        return matches

    bail_fn = None
    if mode == DELETE:
        # There's no point in continuing a search below a node which will be
        # marked for deletion.
        bail_fn = bail_on_match

    matches = jsonselect.match(selector, obj, bailout_fn=bail_fn)
    return [id(node) for node in matches]


def filter_object(obj, marks, presumption=DELETE):
    '''Filter down obj based on marks, presuming keys should be kept/deleted.

    Args:
        obj: The object to be filtered. Filtering is done in-place.
        marks: An object mapping id(obj) --> {DELETE,KEEP}
               These values apply to the entire subtree, unless inverted.
        presumption: The default action to take on all keys.
    '''
    if isinstance(obj, list):
        keys = reversed(range(0, len(obj)))
    else:
        keys = obj.keys()

    for k in keys:
        v = obj[k]
        m = marks.get(id(v), UNSPECIFIED)
        if m == DELETE:
            del obj[k]  # an explicit deletion is irreversible.
        elif m == KEEP or presumption==KEEP:
            # keep descending, in case there are nodes we should delete.
            if isinstance(v, list) or isinstance(v, dict):
                filter_object(v, marks, presumption=KEEP)
        elif m == UNSPECIFIED:
            # ... and presumption == DELETE
            if isinstance(v, list) or isinstance(v, dict):
                filter_object(v, marks, presumption=DELETE)
                if len(v) == 0:
                    del obj[k]
            else:
                del obj[k]


def usage():
    print __doc__


class Timer(object):
    def __init__(self):
        '''Utility for logging timing info. Does nothing if DEBUG=False.'''
        self._start_time_ms_ = 1000 * time.time()
        self._last_time_ms_ = self._start_time_ms_
        self.log('Start')

    def log(self, statement):
        '''Write statement to stderr with timing info in DEBUG mode.'''
        global DEBUG
        time_ms = 1000 * time.time()
        if DEBUG:
            total_time_ms = time_ms - self._start_time_ms_
            lap_time_ms = time_ms - self._last_time_ms_
            sys.stderr.write('%6.f (%6.f ms) %s\n' % (
                total_time_ms, lap_time_ms, statement))
        self._last_time_ms_ = time_ms


def maybe_round(f):
    if round(f) == f:
        return '%d' % f
    else:
        return repr(f)


def apply_filter(objs, selector, mode):
    '''Apply selector to transform each object in objs.

    This operates in-place on objs. Empty objects are removed from the list.

    Args:
        mode: either KEEP (to keep selected items & their ancestors) or DELETE
              (to delete selected items and their children).
    '''
    indices_to_delete = []
    presumption = DELETE if mode == KEEP else KEEP
    for i, obj in enumerate(objs):
        timer.log('Applying selector: %s' % selector)
        marks = {k: mode for k in selector_to_ids(selector, obj, mode)}
        timer.log('done applying selector')
        timer.log('filtering object...')
        filter_object(obj, marks, presumption=presumption)
        timer.log('done filtering')
        if obj is None:
            indices_to_delete.append(i)

    for index in reversed(indices_to_delete):
        del objs[index]


def apply_selector(objs, selector):
    '''Returns a list of objects which match the selector in any of objs.'''
    out = []
    for obj in objs:
        timer.log('Applying selector: %s' % selector)
        out += list(jsonselect.match(selector, objs))
        timer.log('done applying selector')
    return out


timer = Timer()

def run(args):
    if len(args) == 0 or args[0] == '--help':
        usage()
        sys.exit(0)

    global DEBUG
    path = args.pop()  # TODO: allow stdin
    actions = args

    if actions and actions[0] == '--debug':
        DEBUG = True
        del actions[0]

    timer.log('Loading JSON...')
    objs = [json.load(open(path), object_pairs_hook=OrderedDict)]
    timer.log('done loading JSON')

    action_mode = None

    while actions:
        action = actions[0]
        del actions[0]
        mode = None
        if action == '-k':
            selector = actions[0]
            del actions[0]
            apply_filter(objs, selector, KEEP)
        elif action == '-v':
            selector = actions[0]
            del actions[0]
            apply_filter(objs, selector, DELETE)
        elif action == '.':
            continue
        else:
            objs = apply_selector(objs, action)

    def json_dump(o):
        return json.dumps(o, indent=2, separators=(',', ': '), ensure_ascii=False)

    # Note: it's unclear whether rounding these floats is a good idea, but it's
    # what jq does, so we do it too to simplify comparisons.
    save = json.encoder.FLOAT_REPR
    json.encoder.FLOAT_REPR = maybe_round
    r = '\n'.join([json_dump(o) for o in objs]) + '\n'
    json.encoder.FLOAT_REPR = save
    return r


def main():
    print run(sys.argv[1:]).encode('utf8'),
    timer.log('done printing')


if __name__ == '__main__':
    main()
