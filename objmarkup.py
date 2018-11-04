#!/usr/bin/env python3 -O
"""
A class to process object hierarchy data easier and more clearly.
"""

import os
import re
import ssl
import sys
import json
import urllib
import urllib.error
import urllib.request
import argparse
import collections


class ObjMarkup:
    """
    A class to process object hierarchy data easier and more clearly
    """
    # The default separation character between fields.
    # Can be changed to get markup such as:
    #         'company.employees[0]division.location.name'
    #   or:   'company/employees[0]division/location/name'
    def_sep = '.'

    @classmethod
    def is_dict(cls, obj):
        """
        Determine if an object is a dict (mapping) type.
        :param obj: the object to check
        :return: True if the object is a dict type container.
        """
        return isinstance(obj, collections.Mapping) and not isinstance(obj, str)

    @classmethod
    def is_list(cls, obj):
        """
        Determine if an object is a list/array type.
        :param obj: the object to check
        :return: True if the object is a list/array type container.
        """
        return isinstance(obj, collections.Collection)\
            and not isinstance(obj, collections.Mapping)\
            and not isinstance(obj, str)

    @classmethod
    def is_scalar(cls, obj):
        """
        Determine if an object is a simple scalar value (not a container)
        :param obj: the object to check
        :return: True if the object is a scalar value.
        """
        return not (cls.is_dict(obj) or cls.is_list(obj))

    @classmethod
    def contains_containers(cls, data):
        """
        Check all entries in a container and determine if any of
        them are containers themselves.

        :param data: a container to be checked
        :return: returns None if no entries are containers,
                 otherwise returns the first container found.
        """
        if not data or not isinstance(data, collections.Collection) or isinstance(data, str):
            # The data is not a container (or it is but it is empty) and
            # therefore cannot contain any containers
            return None

        if isinstance(data, collections.Mapping):
            for value in data.values():
                if isinstance(value, collections.Collection) and not isinstance(value, str):
                    return value
        else:
            for entry in data:
                if isinstance(entry, collections.Collection) and not isinstance(entry, str):
                    return entry  # this entry is a container (not a child node)
        return None

    @classmethod
    def get_json_data(cls, api_url):
        """
        Retrieve the json data returned from the specified REST url

        :param api_url: the url to retrieve the data from
        :return: the json data as a dictionary
        """
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        # ssl._create_default_https_context = ssl._create_unverified_context
        with urllib.request.urlopen(api_url, context=ssl_context) as url:
            http_info = url.info()
            raw_data = url.read().decode(http_info.get_content_charset())
            json_data = json.loads(raw_data)
            return json_data

    def __call__(self, markup):
        return self.parse(markup)

    def __init__(self, obj):
        """
        Initialize this instance.
        """
        self.sep = ObjMarkup.def_sep
        self.obj = obj
        self.path = ''
        self.fields = []

    def parse(self, path):
        """
        Get a reference to an element in the object using our markup grammar.
        """
        pattern = r'([^\[][a-zA-Z_]+[a-zA-z0-9_]?)?(\[([^\]]+)\])'
        expr_pat = r'([\(\)\%0-9\+\\\*\-\. ]*)'
        begin_colon_end_ndx_pat = r'\[' + expr_pat + r':' + expr_pat + r'\]'

        content = self.obj
        indexes = path.split(self.sep)
        for index in indexes:
            search_result = re.search(pattern, index, re.M)
            if not search_result:
                content = content[index]
                continue
            while search_result:
                label = search_result.group(1)
                ndx_str = search_result.group(2)
                index_val = search_result.group(3)
                if ':' not in ndx_str:
                    if self.is_dict(content):
                        content = content[label][int(index_val)]
                    elif self.is_list(content):
                        content = content[int(index_val)]
                    if label is None and ndx_str is not None:
                        index = index.replace(ndx_str, '', 1)
                    elif label is not None and ndx_str is None:
                        index = index.replace(label, '', 1)
                    elif label is not None and ndx_str is not None:
                        index = index.replace(label + ndx_str, '', 1)
                    search_result = re.search(pattern, index, re.M)
                    continue
                ndx_with_colon = re.search(begin_colon_end_ndx_pat, ndx_str, re.M)
                # if not ndx_with_colon:
                #     raise ValueError('object markup: invalid index: "{}"'.format(ndx_str))
                lhs = ndx_with_colon.group(1)
                rhs = ndx_with_colon.group(2)
                lhs = None if lhs == '' else lhs
                rhs = None if rhs == '' else rhs
                begin = int(lhs) if lhs else 0
                end = int(rhs) if rhs else len(content[label])
                if self.is_dict(content):
                    # print('lhs = "{}" (type({})), rhs = "{}" (type({}))'.format(
                    #    lhs, type(lhs), rhs, type(rhs)))
                    # exit(0)
                    content = content[label][begin:end]
                    index = index.replace(label + ndx_str, '', 1)
                    search_result = re.search(pattern, index, re.M)
                    if index:
                        new_content = []
                        for item in content:
                            new_content.append({index: item[index]})
                        index = ''
                        content = new_content
                    continue
                elif self.is_list(content):
                    # print('content = "{}" (type({}))'.format(content, type(content)))
                    # print('label = "{}" (type({}))'.format(label, type(label)))
                    # print('begin = "{}" (type({})), end = "{}" (type({}))'.format(
                    #     begin, type(begin), end, type(end)))
                    # exit(0)
                    # content = content[label]
                    content = content[begin:end]
                    index = index.replace(label + ndx_str, '', 1)
                    search_result = re.search(pattern, index, re.M)
                    continue
            if index:
                content = content[index]
        return content

    def _gen_fields(self, obj):
        """
        Generate the list of valid markup fields for the object passed in
        """
        if self.is_dict(obj):
            orig_path = self.path
            for key, value in obj.items():
                self.path = orig_path
                if self.path:
                    self.path += self.sep
                self.path += key
                self._gen_fields(value)
            self.path = orig_path
        elif self.is_list(obj):
            index = 0
            orig_path = self.path
            all_items_are_scalar = bool(self.contains_containers(obj))
            for item in obj:
                self.path = orig_path
                if all_items_are_scalar:
                    self.path += '[{}]'.format(len(obj))
                    self._gen_fields(item)
                    break
                self.path += '[{}]'.format(index)
                index += 1
                self._gen_fields(item)
            self.path = orig_path
        else:
            if self.path:
                self.path = self.path.replace('].', ']')
                self.fields.append(self.path)

    def get_fields(self, obj=None):
        """
        Get a list of valid markup fields for our object
        """
        self.path = ''
        self.fields = []
        if obj is None:
            obj = self.obj
        self._gen_fields(obj)
        return self.fields


class JsonMarkup(ObjMarkup):
    """
    Markup adapter with useful functions for processing JSON data
    """
    def __init__(self, obj):
        super().__init__(obj)
        self.csv_path = ''
        self.csv_fields = []

    def gen_csv(self, obj):
        """
        Generate the list of valid markup fields and values for the object passed in
        """
        if self.is_dict(obj):
            orig_path = self.csv_path
            for key, value in obj.items():
                self.csv_path = orig_path
                if self.csv_path:
                    self.csv_path += self.sep
                self.csv_path += key
                self.gen_csv(value)
            self.csv_path = orig_path
        elif self.is_list(obj):
            index = 0
            orig_path = self.csv_path
            # all_items_are_scalar = bool(self.contains_containers(obj))
            for item in obj:
                self.csv_path = orig_path
                # if all_items_are_scalar:
                #     self.path += '[{}]'.format(len(obj))
                #     self.gen_csv(item)
                #     break
                # else:
                self.csv_path += '[{}]'.format(index)
                index += 1
                self.gen_csv(item)
            self.csv_path = orig_path
        else:
            if self.csv_path:
                self.csv_path = self.csv_path.replace('].', ']')
                self.csv_fields.append(self.csv_path)

    def _get_csv_headings_parser(self, obj):
        parser = JsonMarkup(None)
        if self.is_dict(obj):
            for item in obj.items():
                parser = JsonMarkup(item)
                break
        elif self.is_list(obj):
            parser = JsonMarkup(obj[0])
        if not self.is_dict(parser.obj) and not self.is_list(parser.obj):
            parser = JsonMarkup(obj)
        parser.gen_csv(parser.obj)
        hdr_fields = parser.csv_fields
        if hdr_fields and hdr_fields[0] and hdr_fields[0][0] == '[':
            parser = JsonMarkup(obj)
            parser.gen_csv(parser.obj)
        return parser

    def get_csv(self, obj=None):
        """
        Generate a comma separated value table from the object
        """
        self.csv_path = ''
        self.csv_fields = []
        if obj is None:
            obj = self.obj
        self.gen_csv(obj)
        hdr_fields = self.get_fields(obj)
        fields = self.csv_fields

        head_parser = self._get_csv_headings_parser(obj)
        hdr_fields = head_parser.csv_fields

        max_head = max([len(s) for s in hdr_fields]) + 2
        rows = []
        cols = []
        for field in fields:
            value = self.parse(field)
            if isinstance(value, str):
                cols.append(value)
            else:
                cols.append(str(value))
        max_col = max([len(s) for s in cols]) + 2
        fmt1 = '{{:>{}s}}'.format(max(max_head, max_col))

        # Write the column headings line
        quoted_fields = ', '.join([fmt1.format('"{}"'.format(field)) for field in hdr_fields])
        rows.append(quoted_fields)

        # Write the rows of data
        column_index = 0
        cols = []
        for field in fields:
            value = self.parse(field)
            if isinstance(value, str):
                cols.append(value)
            else:
                cols.append(str(value))
            column_index += 1
            if column_index % len(hdr_fields) == 0:
                quoted_cols = ', '.join([fmt1.format('"{}"'.format(col)) for col in cols])
                rows.append(quoted_cols)
                cols = []
                column_index = 0

        return rows


def create_args_parser():
    """
    Create the argparse ArgumentParser for this program

    :param: none
    :return: the argparse.ArgumentParser object
    """
    description = 'Parse an object applying a simplified markup grammar to access data elements, '\
        'optionally display the schema of the object\'s structure as markup strings, '\
        'display all values in the object, or output the object\'s contents as a table of '\
        'comma separated values.'
    epilog = 'Example use: objmarkup.py --log log/objmarkup.log --output output.txt '\
        '--filein sample.json --schema'

    # Standard options for cli interface
    parser = argparse.ArgumentParser(description=description, epilog=epilog,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-l', '--log', type=argparse.FileType('a'), default='/dev/null',
                        help='the file where the log data should be written')
    parser.add_argument('-o', '--output', default=sys.stdout, type=argparse.FileType('a'),
                        help='the file where the output should be written')
    parser.add_argument('-f', '--filein', default=sys.stdin, type=argparse.FileType('r'),
                        help='the file where the input should be read from')

    parser.add_argument('-u', '--url', type=str,
                        help='use the specified url to retrieve json as the input')

    parser.add_argument('-m', '--markup', type=str,
                        help='use the element at the specified markup path to begin '
                        'the processing')

    # Optional user supplied values
    parser.add_argument('-s', '--separator',
                        help='the separation character to use between fields', default='.',
                        type=str)

    parser.add_argument('-b', '--basepaths',
                        help='output the valid markup paths (the schema) for the structure of the '
                        'object. Elements that are array (list) elements are indicated with a '
                        'bracket pair around the total number list items available in the '
                        'current objects contents e.g. \'company.employees[2]\'.',
                        default=False, action='store_true')

    parser.add_argument('-v', '--values',
                        help='output ALL valid markup paths for the structure of the '
                        'object along with their current value.  All legal values for array '
                        'indexes are fully ranged and displayed.  This also makes a handy '
                        'tool to view a list of the various markup strings used to reach a '
                        'certain value in the json.',
                        default=False, action='store_true')

    parser.add_argument('-c', '--csv',
                        help='the filename to output the object to as a comma separated value '
                        'table.  The first line will be the headings for the column names. '
                        'By default these names are the markup string that is the path to the '
                        'column data.',
                        default=False, action='store_true')

    parser.add_argument('-j', '--json',
                        help='output using JSON format',
                        default=False, action='store_true')
    return parser


def check_args_files(args):
    """
    Check the file(s) from the cli. Issue a message and exit
    the program if they are unavailable.

    :param args: the arguments namespace returned from argparse
    :return: nothing
    """
    if not args.filein:
        msg = 'markup: error opening input file'
        print(msg)
        args.log.write(msg + '\n')
        args.log.close()
        exit(-1)

    if not args.output:
        msg = 'markup: error opening output file'
        print(msg)
        args.filein.close()
        args.log.write(msg + '\n')
        args.log.close()
        exit(-2)


def process_args_basepaths(args, obj):
    """
    Handle the basepaths option from the cli.

    :param args: the arguments namespace returned from argparse
    :param obj: the object to process
    :return: nothing
    """
    parser = ObjMarkup(obj)
    if args.markup:
        parser.obj = parser(args.markup)
    fields = parser.get_fields()
    for field in fields:
        args.output.write(field + '\n')
    args.log.write('markup: generated base paths\n')


def process_args_values(args, obj):
    """
    Handle the values option from the cli.

    :param args: the arguments namespace returned from argparse
    :param obj: the object to process
    :return: nothing
    """
    parser = JsonMarkup(obj)
    if args.markup:
        obj = parser.obj = parser(args.markup)
    parser.gen_csv(obj)
    fields = parser.csv_fields
    max_heading = max([len(s) for s in fields])
    max_value = 0
    for field in fields:
        value = parser(field)
        max_value = max(max_value, len(str(value)))

    fmt1 = '{:' + str(max_heading) + 's}'
    fmt2 = '{:<' + str(max_value) + 's}'
    fmt = fmt1 + ' = ' + fmt2 + '\n'

    for field in fields:
        value = parser(field)
        msg = fmt.format(field, str(value))
        args.output.write(msg)
    args.log.write('markup: generated values\n')


def process_args_csv(args, obj):
    """
    Handle the csv option from the cli.

    :param args: the arguments namespace returned from argparse
    :param obj: the object to process
    :return: nothing
    """
    parser = JsonMarkup(obj)
    if args.markup:
        obj = parser.obj = parser(args.markup)
    rows = parser.get_csv(obj)
    for row in rows:
        print(row)
    args.log.write('markup: generated csv table\n')


def process_args_json(args, obj):
    """
    Handle the json option from the cli.

    :param args: the arguments namespace returned from argparse
    :param obj: the object to process
    :return: nothing
    """
    parser = ObjMarkup(obj)
    if args.markup:
        obj = parser.obj = parser(args.markup)
    args.output.write(json.dumps(obj, indent=2) + '\n')


def parse_args():
    """
    Parse and process the options from the command line

    :return: The options as a dictionary
    """
    parser = create_args_parser()

    args = parser.parse_args()
    ObjMarkup.def_sep = args.separator

    check_args_files(args)

    lines = args.filein.readlines()
    args.filein.close()

    content = ''.join(lines)
    if not content:
        exit(0)

    obj = json.loads(content)

    if args.basepaths:
        process_args_basepaths(args, obj)

    if args.values:
        process_args_values(args, obj)

    if args.csv:
        process_args_csv(args, obj)

    if args.json:
        process_args_json(args, obj)

    args.log.close()
    return args


if __name__ == '__main__':
    os.environ['COLUMNS'] = '100'
    parse_args()
