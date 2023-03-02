#!/usr/bin/env python3
from os.path import join as path_join
from fnmatch import fnmatch
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, FileType
from json import load as json_load, dumps as json_dumps, loads as json_loads
from itertools import chain
from sys import stdin as sys_stdin

import logging

LOG = logging.getLogger(__name__)

PROCESS_CHOICES = ["compact", "pretty", "debug", "keys"]
DEFAULT_INDENTATION = 2
DEFAULT_DEPTH = 5
DEFAULT_DICT_ELEMENTS = 4
DEFAULT_LIST_ELEMENTS = 2
DEFAULT_PATH = "*"

PYTHON_TYPES = False
TRUE_STR, FALSE_STR, NULL_STR = ("True", "False", "None") if PYTHON_TYPES else ("true", "false", "none")

TEST_NUM_ELEMENTS = 10


def _test_json():
    def k(k):
        return "k{}".format(k)

    return json_loads(
        json_dumps(
            {
                "listEmpty": [],
                "listInt": list(range(TEST_NUM_ELEMENTS)),
                "listFloat": [1.0 / (x + 1) for x in range(TEST_NUM_ELEMENTS)],
                "listStr": [str(x) for x in range(TEST_NUM_ELEMENTS)],
                "listBool": [x % 2 == 0 for x in range(TEST_NUM_ELEMENTS)],
                "listNull": [None for x in range(TEST_NUM_ELEMENTS)],
                "listDict": [{k(x): x} for x in range(TEST_NUM_ELEMENTS)],
                "listList": [list(range(10)) for x in range(TEST_NUM_ELEMENTS)],
                "listListListList": [[[[None]]]],
                "dictEmpty": {},
                "dictInt": {k(x): x for x in range(TEST_NUM_ELEMENTS)},
                "dictUnicode": {"k{}".format(x): "{}".format(x) for x in range(TEST_NUM_ELEMENTS)},
                "dictStr": {k(x): str(x) for x in range(TEST_NUM_ELEMENTS)},
                "dictDict": {k(x): {k(x): x} for x in range(TEST_NUM_ELEMENTS)},
                "dictDictDictDict": {"a": {"b": {"c": {"d": "e"}}}},
                "int": 1,
                "float": 1.0,
                "unicode": "hello",
                "str": "hello",
                "boolTrue": True,
                "boolFalse": False,
                "null": None,
            }
        )
    )


def json_debug(j, args):
    output = []

    def _output(*parts):
        output.append("".join(parts))

    def _indent(depth):
        return " " * (depth * args.indent)

    def _dict_test(items):
        return args.all or args.dict == 0 or len(items) <= (args.dict * 2)

    def _list_test(items):
        return args.all or args.list == 0 or len(items) <= (args.list * 2)

    def _depth_test(depth):
        return args.all or args.depth == 0 or depth < args.depth

    def _culled(j, path):
        def _path_hit(this_path, child):
            def _child_hit(_this_path, _child):
                if isinstance(_child, dict):
                    for k, v in _child.items():
                        _path = path_join(_this_path, k)
                        if fnmatch(_path, args.path) or _child_hit(_path, v):
                            return True
                elif isinstance(_child, list):
                    for n, v in enumerate(_child):
                        _path = path_join(_this_path, str(n))
                        if fnmatch(_path, args.path) or _child_hit(_path, v):
                            return True
                return False

            return not args.path or fnmatch(this_path, args.path) or _child_hit(this_path, child)

        if isinstance(j, dict):
            keys = sorted(j)
            if args.path or _dict_test(keys):
                for n, k in enumerate(keys):
                    this_path = path_join(path, k)
                    if _path_hit(this_path, j[k]):
                        yield n, k, j[k], this_path
            else:
                for n, k in chain(
                    enumerate(keys[: args.dict]), enumerate(keys[-args.dict :], start=len(keys) - args.dict)
                ):
                    yield n, k, j[k], path_join(path, k)
        elif isinstance(j, list):
            if args.path or _list_test(j):
                for n, v in enumerate(j):
                    this_path = path_join(path, str(n))
                    if _path_hit(this_path, v):
                        yield n, None, v, this_path
            else:
                for n, v in chain(enumerate(j[: args.list]), enumerate(j[-args.list :], start=len(j) - args.list)):
                    yield n, None, v, path_join(path, str(n))
        else:
            LOG.error("Unsupported type: %s", type(j))
            exit()

    def _item(j):
        if j is None:
            return NULL_STR
        elif isinstance(j, bool):
            return TRUE_STR if j else FALSE_STR
        elif isinstance(j, (float, int)):
            return "{}".format(j)
        else:
            return '"{}"'.format(j)

    def _info(path, count=0, value=None):
        if not args.paths and not args.counts:
            return ""

        if args.paths:
            key_str = path
        else:
            key_str = ""

        if args.counts:
            if value is None:
                count_str = ""
            elif count == len(value):
                count_str = "<{}>".format(count)
            else:
                count_str = "<{} of {}>".format(count, len(value))
        else:
            count_str = ""

        if not key_str and not count_str:
            return ""

        return " # {}{}".format(key_str, count_str)

    def _basic_list(j, path):
        basic = []
        previous_n = 0
        rendered = 0
        for n, _, v, _ in _culled(j, path):
            rendered += 1
            if n > 0 and n != previous_n + 1:
                basic.append("... ")
            previous_n = n
            basic.append(_item(v))
        _output(", ".join(basic))
        return rendered

    def _recurse(j, depth=0, path="/"):
        if isinstance(j, dict):
            if len(j) == 0:
                _output("{}", _info(path, 0, j))
                return
            elif not _depth_test(depth):
                _output("{ ... }", _info(path, 0, j))
                return
            else:
                _output("{\n")
        elif isinstance(j, list):
            if len(j) == 0:
                _output("[]", _info(path, 0, j))
                return
            elif not _depth_test(depth):
                _output("[ ... ]", _info(path, 0, j))
                return
            elif any(isinstance(x, (dict, list)) for x in j):
                _output("[\n")
            else:
                _output("[")
                rendered = _basic_list(j, path)
                _output("]", _info(path, rendered, j))
                return
        else:
            _output(_item(j))
            return

        depth += 1
        indent = _indent(depth)
        previous_n = 0
        rendered = 0
        for n, k, v, this_path in _culled(j, path):
            rendered += 1
            prefix = '{}"{}": '.format(indent, k) if k else indent

            # Is there a gap in the output, if so add a '...'
            if n > 0 and n != previous_n + 1:
                _output(indent, "...\n")
            previous_n = n

            if isinstance(v, dict):
                _output(prefix)
                _recurse(v, depth, this_path)
                _output("\n")
            elif isinstance(v, list):
                _output(prefix)
                _recurse(v, depth, this_path)
                _output("\n")
            else:
                _output(prefix, _item(v), _info(this_path), "\n")

        indent = _indent(depth - 1)
        if isinstance(j, dict):
            _output(indent, "}", _info(path, rendered, j))
        elif isinstance(j, list):
            _output(indent, "]", _info(path, rendered, j))

    _recurse(j)
    return output


def keys_debug(j, args):
    output = []

    def _recurse(j, depth=0, path="/"):
        # TODO add support for "dict" + "list"?
        # TODO add support for "path"
        if args.all or args.depth == 0 or depth < args.depth:
            depth += 1
            if isinstance(j, dict):
                keys = sorted(j)
                for k in keys:
                    this_path = path_join(path, k)
                    output.append(this_path)
                    _recurse(j[k], depth, this_path)
            elif isinstance(j, list):
                for n, v in enumerate(j):
                    _recurse(v, depth, path_join(path, str(n)))

    _recurse(j)
    return output


def parse_args():
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("input", nargs="*", type=FileType("r"), default=[sys_stdin], help="JSON files to process")
    parser.add_argument("--style", choices=PROCESS_CHOICES, default="debug", help="Style of JSON output")
    group = parser.add_argument_group("what to output?")
    group.add_argument("--all", action="store_true", help="Output everything")
    group.add_argument("--indent", type=int, default=DEFAULT_INDENTATION, help="Print indentation")
    group.add_argument("--depth", type=int, default=DEFAULT_DEPTH, help="Depth to recurse")
    group.add_argument("--dict", type=int, default=DEFAULT_DICT_ELEMENTS, help="Num dict entries to display")
    group.add_argument("--list", type=int, default=DEFAULT_LIST_ELEMENTS, help="Num list entries to display")
    group.add_argument("--paths", action="store_true", help="Output item paths")
    group.add_argument("--counts", action="store_true", help="Output item counts")
    group.add_argument("--path", type=str, help="File pattern selection of elements to display")
    group = parser.add_argument_group("debugging options")
    group.add_argument("--verbose", "-v", action="store_true")
    group.add_argument("--debug", action="store_true")
    group.add_argument("--test", action="store_true", help="Test the tool against a built-in unit test")
    args = parser.parse_args()

    if args.debug:
        level = logging.DEBUG
    elif args.verbose:
        level = logging.INFO
    else:
        level = logging.WARNING
    logging.basicConfig(format="%(message)s", level=level)
    LOG.debug("# %s", args)

    return args


def main():
    args = parse_args()

    def _process(j):
        if args.style == "compact":
            print(json_dumps(j, sort_keys=True, separators=(",", ":")))
        elif args.style == "pretty":
            print(json_dumps(j, sort_keys=True, indent=args.indent, separators=(",", ": ")))
        elif args.style == "keys":
            print("\n".join(keys_debug(j, args)))
        elif args.style == "debug":
            print("".join(json_debug(j, args)))

    if args.test:
        _process(_test_json())
        return

    for f in args.input:
        j = json_load(f)
        _process(j)


if __name__ == "__main__":
    main()
