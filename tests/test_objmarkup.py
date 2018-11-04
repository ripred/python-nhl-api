#!/usr/bin/env python3
""" unit tests for objmarkup.py """

import unittest
import os
import sys
import json
import urllib.request
import objmarkup

class Unit01MarkupTests(unittest.TestCase):
    """
    Unit Tests for the ObjMarkup class
    """
    def setUp(self):
        """Fixture that loads the test data for the unit tests to use."""
        self.obj = {}
        self.orig = sys.argv
        self.parser = None
        basepath = os.getcwd()
        filename = basepath + '/json/sample.json'
        with urllib.request.urlopen(''.join(['file://', filename])) as url:
            raw_data = url.read().decode('utf-8')
            self.obj = json.loads(raw_data)
            self.assertIsNotNone(self.obj)

    def tearDown(self):
        """Fixture that removes the test data used by the unit tests."""
        del self.obj
        del self.parser

    def test_01_create_base_parser(self):
        """
        Run the test on the ObjMarkup class

        :param self: reference to the test framework object
        :return: Nothing
        """
        self.parser = objmarkup.ObjMarkup(self.obj)
        self.assertTrue(self.parser)
        # self.all_games = self.json_data['dates'][0]['games']
        # self.games_dict = sports.create_games_dict(self.all_games)
        # self.assertEqual(sports.get_games_count(self.json_data), 8)
        # self.assertTrue('dates' in self.json_data)
        # self.assertGreater(len(self.json_data['dates']), 0)
        # self.assertGreaterEqual(key[:5], last_key)

    def test_02_utility_methods(self):
        """
        Run the test on the ObjMarkup class

        :param self: reference to the test framework object
        :return: Nothing
        """
        # perform basic sanity checks on the class utility methods
        self.parser = objmarkup.ObjMarkup(self.obj)
        self.assertTrue(self.parser)
        self.assertTrue(self.parser.is_dict({}))
        self.assertFalse(self.parser.is_dict([]))
        self.assertTrue(self.parser.is_list([]))
        self.assertFalse(self.parser.is_list({}))
        self.assertTrue(self.parser.is_scalar('hello'))
        self.assertTrue(self.parser.is_scalar(1))
        self.assertTrue(self.parser.is_scalar(1.5))
        self.assertFalse(self.parser.is_scalar({}))
        self.assertFalse(self.parser.is_scalar([]))
        self.assertFalse(self.parser.is_scalar(()))

    def test_03_basic_parse_dict_value(self):
        """
        Run the test on the ObjMarkup class

        :param self: reference to the test framework object
        :return: Nothing
        """
        markup = 'company'
        self.parser = objmarkup.ObjMarkup(self.obj)
        self.assertTrue(self.parser)
        obj = self.parser.parse(markup)
        self.assertIsNotNone(obj)

    def test_04_basic_evaluate_call_dict(self):
        """
        Run the test on the ObjMarkup class

        :param self: reference to the test framework object
        :return: Nothing
        """
        markup = 'company'
        self.parser = objmarkup.ObjMarkup(self.obj)
        self.assertTrue(self.parser)
        obj = self.parser(markup)
        self.assertIsNotNone(obj)

    def test_05_basic_parse_list_value(self):
        """
        Run the test on the ObjMarkup class

        :param self: reference to the test framework object
        :return: Nothing
        """
        markup = 'company[0]'
        self.parser = objmarkup.ObjMarkup(self.obj)
        self.assertTrue(self.parser)
        obj = self.parser(markup)
        self.assertIsNotNone(obj)

    def test_06_parse_dict_list_value(self):
        """
        Run the test on the ObjMarkup class

        :param self: reference to the test framework object
        :return: Nothing
        """
        markup = 'company[0].name'
        answer = 'Slate Rock and Gravel Company'
        self.parser = objmarkup.ObjMarkup(self.obj)
        self.assertTrue(self.parser)
        value = self.parser(markup)
        self.assertEqual(value, answer)

    def test_07_parse_mult_dict_list_value_1(self):
        """
        Run the test on the ObjMarkup class

        :param self: reference to the test framework object
        :return: Nothing
        """
        markup = 'company[0]employees[0]name'
        answer = 'Fred Flintstone'
        self.parser = objmarkup.ObjMarkup(self.obj)
        self.assertTrue(self.parser)
        value = self.parser(markup)
        self.assertEqual(value, answer)

    def test_08_parse_mult_dict_list_value_2(self):
        """
        Run the test on the ObjMarkup class

        :param self: reference to the test framework object
        :return: Nothing
        """
        markup = 'company[0]employees[0]hobby[0]name'
        answer = 'Bowling'
        self.parser = objmarkup.ObjMarkup(self.obj)
        self.assertTrue(self.parser)
        value = self.parser(markup)
        self.assertEqual(value, answer)

    def test_09_basic_get_schema(self):
        """
        Run the test on the ObjMarkup class

        :param self: reference to the test framework object
        :return: Nothing
        """
        self.parser = objmarkup.ObjMarkup(self.obj)
        self.assertTrue(self.parser)
        schema = self.parser.get_fields()
        self.assertIsNotNone(schema)

    def test_10_schema_check(self):
        """
        Run the test on the ObjMarkup class

        :param self: reference to the test framework object
        :return: Nothing
        """
        self.parser = objmarkup.ObjMarkup(self.obj)
        self.assertTrue(self.parser)
        schema = self.parser.get_fields()
        self.assertEqual(len(schema), 4)
        self.assertEqual(schema[0], 'company[1].name')
        self.assertEqual(schema[1], 'company[1].employees[2].name')
        self.assertEqual(schema[2], 'company[1].employees[2].job title')
        self.assertEqual(schema[3], 'company[1].employees[2].hobby[2].name')

class Unit02JsonMarkupTests(unittest.TestCase):
    """
    Unit Tests for the JsonMarkup class
    """
    def setUp(self):
        """Fixture that loads the test data for the unit tests to use."""
        self.obj = {}
        self.orig = sys.argv
        self.parser = None
        basepath = os.getcwd()
        filename = basepath + '/json/sample.json'
        with urllib.request.urlopen(''.join(['file://', filename])) as url:
            raw_data = url.read().decode('utf-8')
            self.obj = json.loads(raw_data)
            self.assertIsNotNone(self.obj)

    def tearDown(self):
        """Fixture that removes the test data used by the unit tests."""
        del self.obj
        del self.parser

    def test_01_create_basic_json_parser(self):
        """
        Run the test on the ObjMarkup class

        :param self: reference to the test framework object
        :return: Nothing
        """
        self.parser = objmarkup.JsonMarkup(self.obj)
        self.assertIsNotNone(self.parser)

    def test_02_basic_json_parser_csv_1(self):
        """
        Run the test on the ObjMarkup class

        :param self: reference to the test framework object
        :return: Nothing
        """
        self.parser = objmarkup.JsonMarkup(self.obj)
        self.assertIsNotNone(self.parser)
        csv = self.parser.get_csv()
        self.assertIsNotNone(csv)
        self.assertEqual(len(csv), 2)
        self.assertEqual(len(self.parser.csv_fields), 9)

    def test_03_basic_json_parser_csv_2(self):
        """
        Run the test on the ObjMarkup class

        :param self: reference to the test framework object
        :return: Nothing
        """
        markup = 'company[0]employees[0]hobby[0]'
        self.parser = objmarkup.JsonMarkup(self.obj)
        self.assertIsNotNone(self.parser)
        self.parser.get_fields()
        obj = self.parser.obj = self.parser(markup)
        csv = self.parser.get_csv(obj)
        self.assertIsNotNone(csv)
        self.assertEqual(len(csv), 2)

    def test_04_basic_json_parser_csv_3(self):
        """
        Run the test on the ObjMarkup class

        :param self: reference to the test framework object
        :return: Nothing
        """
        markup = 'company[0]employees[0]hobby'
        self.parser = objmarkup.JsonMarkup(self.obj)
        self.assertIsNotNone(self.parser)
        obj = self.parser.obj = self.parser(markup)
        csv = self.parser.get_csv(obj)
        self.assertIsNotNone(csv)
        self.assertEqual(len(csv), 3)

    def test_05_basic_json_parser_csv_4(self):
        """
        Run the test on the ObjMarkup class

        :param self: reference to the test framework object
        :return: Nothing
        """
        markup = 'company[0]employees[0]'
        self.parser = objmarkup.JsonMarkup(self.obj)
        self.assertIsNotNone(self.parser)
        obj = self.parser.obj = self.parser(markup)
        csv = self.parser.get_csv(obj)
        self.assertIsNotNone(csv)
        self.assertEqual(len(csv), 2)

    def test_06_basic_json_parser_csv_5(self):
        """
        Run the test on the ObjMarkup class

        :param self: reference to the test framework object
        :return: Nothing
        """
        markup = 'company[0]employees'
        self.parser = objmarkup.JsonMarkup(self.obj)
        self.assertIsNotNone(self.parser)
        obj = self.parser.obj = self.parser(markup)
        csv = self.parser.get_csv(obj)
        self.assertIsNotNone(csv)
        self.assertEqual(len(csv), 3)

    def test_07_using_split_indexing_in_markup(self):
        """
        Run the test on the ObjMarkup class

        :param self: reference to the test framework object
        :return: Nothing
        """
        markup = 'company[0]employees[0:1]name'
        self.parser = objmarkup.JsonMarkup(self.obj)
        self.assertIsNotNone(self.parser)
        value = self.parser(markup)
        answer = {'name': 'Fred Flintstone'}
        self.assertEqual(value[0], answer)

    def test_08_cli_tool_runs(self):
        """
        Basic smoke test: Does the function run?
        Run the test on the ObjMarkup class

        :param self: reference to the test framework object
        :return: Nothing
        """
        print()
        self.orig = sys.argv
        sys.argv = ['./objmarkup.py', '-f', 'json/sample.json', '-m', "company[0].employees",
                    '--csv']
        objmarkup.parse_args()
        sys.argv = self.orig


if __name__ == '__main__':
    unittest.main()
