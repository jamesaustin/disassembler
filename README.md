# disassembler
Simple stupid tool to help with disassembling JSON assets.

Testing with Python 2.7.12 on Mac OS X 10.11.6.

# Usage
```
usage: disassembler.py [-h] [--style {compact,pretty,debug,keys}] [--all] [--indent INDENT]
                       [--depth DEPTH] [--dict DICT] [--list LIST] [--paths] [--counts]
                       [--path PATH] [--verbose] [--debug] [--test]
                       [input [input ...]]

positional arguments:
  input                 JSON files to process (default: None)

optional arguments:
  -h, --help            show this help message and exit
  --style {compact,pretty,debug,keys}
                        Style of JSON output (default: debug)

what to output?:
  --all                 Output everything (default: False)
  --indent INDENT       Print indentation (default: 2)
  --depth DEPTH         Depth to recurse (default: 5)
  --dict DICT           Num dict entries to display (default: 4)
  --list LIST           Num list entries to display (default: 2)
  --paths               Output item paths (default: False)
  --counts              Output item counts (default: False)
  --path PATH           File pattern selection of elements to display (default: None)

debugging options:
  --verbose, -v
  --debug
  --test                Test the tool against a built-in unit test (default: False)
```

# Contributor list
[@james_austin](http://twitter.com/james_austin)
