#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import json
import unittest

from jsontemplate import template, optional, mixin


class MixinTests(unittest.TestCase):

    dict_template = {
        "first_name": str,
        "last_name": str,
        "age": int,
        "animal": mixin(
            {
                "name": str,
                "age": int,
                "specie": optional(str),
            }, str),
        "location": (str, int),
        "scores": [{float, int}]
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

    def test_validate_complex_mixin(self):
        self.assertIsNone(self.template.validate(self.data))

    def test_validate_simple_mixin(self):
        self.data['animal'] = u'cat'
        self.assertIsNone(self.template.validate(self.data))

    def test_validate_complex_mixin_optional(self):
        del self.data['animal']['specie']
        self.assertIsNone(self.template.validate(self.data))

    def test_example(self):
        self.assertEquals(self.template.example(), {
            'first_name': u'example',
            'last_name': u'example',
            'age': 0,
            'animal': {
                    'name': u'example',
                    'age': 0,
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

    def test_output(self):
        self.assertEquals(self.template.output(self.data), self.data)

if __name__ == '__main__':
    unittest.main()

