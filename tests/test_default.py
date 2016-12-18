#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import json
import unittest
from copy import deepcopy

from jsontemplate import template, default
from jsontemplate.exceptions import *


# python3 compatibility testing
try:
    unicode('hello')
except:
    unicode = str


class DefaultTests(unittest.TestCase):

    dict_template = {
        "first_name": str,
        "last_name": str,
        "age": int,
        "animals": default([
            {
                "name": str,
                "age": int,
                "specie": 'cat'
            }
        ], []),
        "location": (str, int),
        "scores": [{float, int}],
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

    def test_validate_default_str(self):
        del self.data['animals'][0]['specie']
        self.assertIsNone(self.template.validate(self.data))

    def test_validate_default_list(self):
        del self.data['animals']
        self.assertIsNone(self.template.validate(self.data))

    def test_validate_invalid_list(self):
        self.data['animals'] = self.data['animals'][0]
        self.assertRaises(ValidationError, self.template.validate, self.data)

    def test_validate_invalid_str(self):
        self.data['animals'][0]['specie'] = [1,2]
        self.assertRaises(ValidationError, self.template.validate, self.data)

    def test_example(self):
        example = self.template.example()
        self.assertDictEqual(example, {
            'first_name': 'example',
            'last_name': 'example',
            'age': 0,
            'animals': [],
            'location': ['example', 0],
            'scores': [0.0]
        })

    def test_example_full(self):
        self.assertDictEqual(self.template.example(full=True), {
            'first_name': 'example',
            'last_name': 'example',
            'age': 0,
            'animals': [],
            'location': ['example', 0],
            'scores': [0.0]
        })

    def test_output(self):
        self.assertDictEqual(self.template.output(self.data), self.data)

    def test_output_default(self):
        data = deepcopy(self.data)
        del self.data['animals'][0]['specie']
        data['animals'][0]['specie'] = 'cat'
        self.assertDictEqual(self.template.output(self.data), data)

if __name__ == '__main__':
    unittest.main()
