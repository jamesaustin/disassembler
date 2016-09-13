#!/usr/bin/env python

from os.path import join as path_join
from fnmatch import fnmatch
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from json import load as json_load, dumps as json_dumps

import logging
LOG = logging.getLogger(__name__)

DEFAULT_INDENTATION = 2
DEFAULT_DEPTH = 5
DEFAULT_DICT_ELEMENTS = 4
DEFAULT_LIST_ELEMENTS = 2
DEFAULT_PATH = '*'

PYTHON_TYPES = False
TRUE_STR, FALSE_STR, NULL_STR = ('True', 'False', 'None') if PYTHON_TYPES else ('true', 'false', 'none')

TEST_JSON = {
    'list': [],
    'listInt': list(range(100)),
    'listFloat': [1.0 / (x + 1) for x in range(100)],
    'listStr': [str(x) for x in range(100)],
    'listBool': [x % 2 == 0 for x in range(100)],
    'listNull': [None for x in range(100)],
    'listDict': [{str(x): x} for x in range(100)],
    'listList': [list(range(10)) for x in range(100)],
    'listListListList': [[[[None]]]],
    'dict': {},
    'dictStr': {str(x): x for x in range(100)},
    'dictDict': {str(x): {str(x): x} for x in range(100)},
    'dictDictDictDict': {'a': {'b': {'c': {'d': 'e'}}}},
    'int': 1,
    'float': 1.0,
    'str': 'hello',
    'boolTrue': True,
    'boolFalse': False,
    'null': None
}

def json_debug(j, args):
    output = []
    def _output(*parts):
        output.append(''.join(parts))
    def _null(_):
        pass

    def _path_hit(this_path, child):
        def _child_hit(_this_path, _child):
            if isinstance(_child, dict):
                for k, v, in _child.iteritems():
                    _path = path_join(_this_path, k)
                    if fnmatch(_path, args.path) or _child_hit(_path, v):
                        return True
            elif isinstance(_child, list):
                for n, v in enumerate(_child):
                    _path = path_join(_this_path, str(n))
                    if fnmatch(_path, args.path) or _child_hit(_path, v):
                        return True
            return False
        return fnmatch(this_path, args.path) or _child_hit(this_path, child)

    def _dict_test(items):
        return args.all or args.dict == 0 or len(items) <= (args.dict * 2)
    def _list_test(items):
        return args.all or args.list == 0 or len(items) <= (args.list * 2)
    def _depth_test(depth):
        return args.all or args.depth == 0 or depth <= args.depth

    def _culled(j):
        if isinstance(j, dict):
            keys = sorted(j.keys())
            if _dict_test(keys):
                for n, k in enumerate(keys):
                    yield n, k, j[k]
            else:
                n = 0
                for k in keys[:args.dict]:
                    yield n, k, j[k]
                    n += 1
                n = len(keys) - args.dict
                for k in keys[-args.dict:]:
                    yield n, k, j[k]
                    n += 1
        elif isinstance(j, list):
            if _list_test(j):
                for n, v in enumerate(j):
                    yield n, None, v
            else:
                n = 0
                for v in j[:args.list]:
                    yield n, None, v
                    n += 1
                n = len(j) - args.list
                for v in j[-args.list:]:
                    yield n, None, v
                    n += 1
        else:
            LOG.error('Unsupported type: %s', type(j))
            exit()

    def _item(j):
        if j is None:
            return NULL_STR
        elif isinstance(j, bool):
            return TRUE_STR if j else FALSE_STR
        elif isinstance(j, (float, int)):
            return '{}'.format(j)
        elif isinstance(j, (str, unicode)):
            return '"{}"'.format(j)
        else:
            LOG.error('Unsupported type: %s', type(j))
            exit()

    def _info(path, count=0, value=None, key=None):
        if not args.paths and not args.counts:
            return ''

        if args.paths:
            key_str = '{}'.format(path)
        elif key:
            key_str = '"{}"'.format(key)
        else:
            key_str = ''

        if args.counts:
            if not value:
                count_str = ''
            elif count == len(value):
                count_str = '<{}>'.format(count)
            else:
                count_str = '<{} of {}>'.format(count, len(value))
        else:
            count_str = ''

        if not key_str and not count_str:
            return ''

        return ' # {}{}'.format(key_str, count_str)

    def _basic_list(j):
        basic = []
        comma, no_comma_at = ', ', len(j) - 1
        previous_n = 0
        for n, _, v in _culled(j):
            if n > 0 and n != previous_n + 1:
                basic.append('... ')
            previous_n = n
            comma = '' if n == no_comma_at else comma
            basic.append('{}{}'.format(_item(v), comma))
        return ''.join(basic)

    def _recurse(j, current_depth=0, path=None):
        indent = ' ' * (current_depth * args.indent)
        current_depth += 1
        comma, no_comma_at = ',', len(j) - 1
        previous_n = 0
        c = 0
        for n, k, v in _culled(j):
            c += 1
            prefix = indent
            if not path:
                this_path = '/'
            elif k:
                prefix = '{}"{}": '.format(indent, k)
                this_path = path_join(path, k)
            else:
                this_path = path_join(path, str(n))
            comma = '' if n == no_comma_at else comma
            render_fn = _output if _path_hit(this_path, v) else _null
            if n > 0 and n != previous_n + 1:
                render_fn(indent, '...')
            previous_n = n
            if isinstance(v, dict):
                if not _depth_test(current_depth):
                    render_fn(prefix, '{ ... }', comma, _info(this_path, 0, v))
                elif len(v) == 0:
                    render_fn(prefix, '{}', comma, _info(this_path, 0, v, k))
                else:
                    render_fn(prefix, '{')
                    count = _recurse(v, current_depth, this_path)
                    render_fn(indent, '}', comma, _info(this_path, count, v, k))
            elif isinstance(v, list):
                if not _depth_test(current_depth):
                    render_fn(prefix, '[ ... ]', comma, _info(this_path, 0, v))
                elif any(isinstance(x, (dict, list)) for x in v):
                    render_fn(prefix, '[')
                    count = _recurse(v, current_depth, this_path)
                    render_fn(indent, ']', comma, _info(this_path, count, v, k))
                else:
                    render_fn(prefix, '[', _basic_list(v), ']', comma, _info(this_path))
            else:
                render_fn(prefix, _item(v), comma, _info(this_path))
        return c

    if isinstance(j, (dict, list)):
        _recurse([j])
    else:
        _output(_item(j))

    return output

def parse_args():
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('input', nargs='*', type=str, help='JSON files to process')
    parser.add_argument('--style', choices=['compact', 'pretty', 'debug'], default='debug', help='Style of JSON output')
    group = parser.add_argument_group('what to output?')
    group.add_argument('--all', action='store_true', help='Output everything')
    group.add_argument('--indent', type=int, default=DEFAULT_INDENTATION, help='Print indentation')
    group.add_argument('--depth', type=int, default=DEFAULT_DEPTH, help='Depth to recurse')
    group.add_argument('--dict', type=int, default=DEFAULT_DICT_ELEMENTS, help='Num dict entries to display')
    group.add_argument('--list', type=int, default=DEFAULT_LIST_ELEMENTS, help='Num list entries to display')
    group.add_argument('--paths', action='store_true', help='Output item paths')
    group.add_argument('--counts', action='store_true', help='Output item counts')
    group.add_argument('--path', type=str, default=DEFAULT_PATH, help='File pattern selection of elements to display')
    group = parser.add_argument_group('debugging options')
    group.add_argument('--verbose', '-v', action='store_true')
    group.add_argument('--debug', action='store_true')
    group.add_argument('--test', action='store_true', help='Test the tool against a built-in unit test')
    args = parser.parse_args()

    if args.debug:
        level = logging.DEBUG
    elif args.verbose:
        level = logging.INFO
    else:
        level = logging.WARNING
    logging.basicConfig(format='%(message)s', level=level)
    LOG.debug('# %s', str(args))

    return args

def main():
    args = parse_args()

    def _process(j):
        if args.style == 'compact':
            print(json_dumps(j, sort_keys=True, separators=(',', ':')))
        elif args.style == 'pretty':
            print(json_dumps(j, sort_keys=True, indent=args.indent, separators=(',', ': ')))
        else:
            print('\n'.join(json_debug(j, args)))

    if args.test:
        _process(TEST_JSON)
        return

    for i in args.input:
        with open(i) as f:
            j = json_load(f)
            _process(j)

if __name__ == '__main__':
    main()
