#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import json
import unittest
from copy import deepcopy

from jsontemplate import template, optional
from jsontemplate.exceptions import *


class OptionalTests(unittest.TestCase):

    dict_template = {
            "first_name": str,
            "last_name": str,
            "age": optional(int),
            "animal": optional({
                "name": str,
                "age": int,
                "specie": optional(str),
                }),
            "location": (str, int),
            "scores": optional([{float, int}]),
            }

    @classmethod
    def setUpClass(cls):
        cls.json = """{
            "first_name": "Adrien",
            "last_name": "El Zein",
            "age": 25,
            "animal": {
                "name": "kupa",
                "age": 8,
                "specie": "cat"
            },
            "location": ["Paris", 75001],
            "scores": [0.34, 0.54, 0.66, 0.81, 1.44, 23.4, 50]
        }"""

    @classmethod
    def tearDownClass(cls):
        cls.json = None

    def setUp(self):
        self.data = json.loads(self.json)
        self.template = template(self.dict_template)

    def tearDown(self):
        self.data = None
        self.template = None

    def test_validate_valid_data(self):
        self.assertIsNone(self.template.validate(self.data))

    def test_validate_optional_int(self):
        del self.data['age']
        self.assertIsNone(self.template.validate(self.data))

    def test_validate_optional_str(self):
        del self.data['animal']['specie']
        self.assertIsNone(self.template.validate(self.data))

    def test_validate_optional_list(self):
        del self.data['scores']
        self.assertIsNone(self.template.validate(self.data))

    def test_validate_optional_dict(self):
        del self.data['animal']
        self.assertIsNone(self.template.validate(self.data))

    def test_validate_invalid_int(self):
        self.data['age'] = u'1az2'
        self.assertRaises(ValidationError, self.template.validate, self.data)

    def test_validate_invalid_str(self):
        self.data['animal']['specie'] = [1,2]
        self.assertRaises(ValidationError, self.template.validate, self.data)

    def test_example(self):
        self.assertEquals(self.template.example(), {
            'first_name': u'example',
            'last_name': u'example',
            'location': [u'example', 0],
            })

    def test_example_full(self):
        self.assertEquals(self.template.example(full=True), {
            'first_name': u'example',
            'last_name': u'example',
            'age': 0,
            'animal': {
                'name': u'example',
                'age': 0,
                'specie': u'example'
                },
            'location': [u'example', 0],
            'scores': [0.0],
            })

    def test_output(self):
        self.assertEquals(self.template.output(self.data), self.data)

    def test_output_full(self):
        data = deepcopy(self.data)
        del data['animal']
        del data['age']
        del data['scores']
        self.data['animal'] = {'name': u'example', 'specie': u'example', 'age': 0}
        self.data['age'] = 0
        self.data['scores'] = [0]
        self.assertEquals(self.template.output(data, full=True), self.data)

if __name__ == '__main__':
    unittest.main()


