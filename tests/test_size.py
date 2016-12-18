#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import json
import unittest

from jsontemplate import template, size
from jsontemplate.exceptions import *


# python3 compatibility testing
try:
    unicode('hello')
except:
    unicode = str


class SizeTests(unittest.TestCase):

    dict_template = {
        "first_name": str,
        "last_name": str,
        "age": int,
        "animals": [
            {
                "name": str,
                "age": int,
                "specie": str
            }
        ],
        "location": (str, int),
        "scores": size([{float, int}], min_value=1, max_value=5)
    }

    @classmethod
    def setUpClass(cls):
        cls.json = """{
            "first_name": "Adrien",
            "last_name": "El Zein",
            "age": 25,
            "animals": [{
                "name": "kupa",
                "age": 8,
                "specie": "cat"
            },
            {
                "name": "pikachu",
                "age": 7,
                "specie": "pokemon"
            }],
            "location": ["Paris", 75001],
            "scores": [0.34, 0.54, 0.66]
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

    def test_validate_min_size(self):
        self.data['scores'] = []
        self.assertRaises(ValidationError, self.template.validate, self.data)

    def test_validate_max_size(self):
        self.data['scores'] = [0]*10
        self.assertRaises(ValidationError, self.template.validate, self.data)

    def test_example(self):
        data = self.template.example()
        self.assertLessEqual(len(data['scores']), 5)
        self.assertGreaterEqual(len(data['scores']), 1)
        data['scores'] = [data['scores'][0]]
        self.assertDictEqual(data, {
            'first_name': 'example',
            'last_name': 'example',
            'age': 0,
            'animals': [{
                'name': 'example',
                'age': 0,
                'specie': 'example'
            }],
            'location': ['example', 0],
            'scores': [0.0]
        })

    def test_example_full(self):
        self.assertDictEqual(self.template.example(full=True), {
            'first_name': 'example',
            'last_name': 'example',
            'age': 0,
            'animals': [
                {
                    'name': 'example',
                    'age': 0,
                    'specie': 'example'
                }
            ],
            'location': ['example', 0],
            'scores': [0.0]*5
        })

    def test_output(self):
        self.assertDictEqual(self.template.output(self.data), self.data)

if __name__ == '__main__':
    unittest.main()
