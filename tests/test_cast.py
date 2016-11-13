#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import json
import unittest
from copy import deepcopy

from jsontemplate import template, optional, cast
from jsontemplate.exceptions import *


class CastTests(unittest.TestCase):

    dict_template = {
        "first_name": str,
        "last_name": str,
        "age": cast(int, {int, str}),
        "animal": {
                "name": str,
                "age": optional(cast(int)),
                "specie": str,
            },
        "location": (str, int),
        "scores": cast(lambda l: sorted(l, reverse=True), [{float, int}])
    }

    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None
        cls.json = """{
            "first_name": "Adrien",
            "last_name": "El Zein",
            "age": "25",
            "animal": {
                "name": "kupa",
                "age": "8",
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

    def test_validate_str_to_int(self):
        self.data['age'] = u'12'
        self.assertIsNone(self.template.validate(self.data))

    def test_validate_nested_float_to_int(self):
        self.data['animal']['age'] = 5.4
        self.assertIsNone(self.template.validate(self.data))

    def test_validate_optional_cast(self):
        del self.data['animal']['age']
        self.assertIsNone(self.template.validate(self.data))

    def test_validate_invalid_source(self):
        self.data['age'] = 'adrien'
        self.assertRaises(ValidationError, self.template.validate, self.data)

    def test_example(self):
        self.assertEquals(self.template.example(), {
            'first_name': u'example',
            'last_name': u'example',
            'age': 0,
            'animal': {
                'name': u'example',
                'specie': u'example'
            },
            'location': [u'example', 0],
            'scores': [0.0]
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
            'scores': [0.0]
        })

    def test_output_optional(self):
        data = deepcopy(self.data)
        data['age'] = int(data['age'])
        del data['animal']['age']
        del self.data['animal']['age']
        data['scores'] = sorted(data['scores'], reverse=True)
        self.assertEquals(self.template.output(self.data), data)

    def test_output_optional_full(self):
        data = deepcopy(self.data)
        data['age'] = int(data['age'])
        data['animal']['age'] = 0
        del self.data['animal']['age']
        data['scores'] = sorted(data['scores'], reverse=True)
        self.assertEquals(self.template.output(self.data, full=True), data)

    def test_output(self):
        data = deepcopy(self.data)
        data['age'] = int(data['age'])
        data['animal']['age'] = int(data['animal']['age'])
        data['scores'] = sorted(data['scores'], reverse=True)
        self.assertEquals(self.template.output(self.data), data)

if __name__ == '__main__':
    unittest.main()
