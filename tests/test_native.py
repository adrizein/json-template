#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import json
import unittest

from jsontemplate import template
from jsontemplate.exceptions import *


# python3 compatibility testing
try:
    unicode('hello')
except:
    unicode = str


class NativeTests(unittest.TestCase):

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
            "scores": [{float, int}]
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

    def test_validate_invalid_tuple(self):
        self.data['location'][1] = u'75001ZEZ'
        self.assertRaises(ValidationError, self.template.validate, self.data)

    def test_validate_invalid_list(self):
        self.data['scores'][4] = u'2az'
        self.assertRaises(ValidationError, self.template.validate, self.data)

    def test_validate_invalid_dict(self):
        del self.data['animals'][0]['specie']
        self.assertRaises(ValidationError, self.template.validate, self.data)

    def test_validate_invalid_type(self):
        self.data['first_name'] = [u'Adrien', u'El Zein']
        self.assertRaises(ValidationError, self.template.validate, self.data)

    def test_example(self):
        self.assertDictEqual(self.template.example(), {
            'first_name': u'example',
            'last_name': u'example',
            'age': 0,
            'animals': [
                {
                    'name': u'example',
                    'age': 0,
                    'specie': u'example'
                    }
                ],
            'location': [u'example', 0],
            'scores': [0.0]
            })

    def test_example_full(self):
        self.assertDictEqual(self.template.example(full=True), {
            'first_name': u'example',
            'last_name': u'example',
            'age': 0,
            'animals': [
                {
                    'name': u'example',
                    'age': 0,
                    'specie': u'example'
                    }
                ],
            'location': [u'example', 0],
            'scores': [0.0]
            })

    def test_output(self):
        self.assertDictEqual(self.template.output(self.data), self.data)

if __name__ == '__main__':
    unittest.main()

