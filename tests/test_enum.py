#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import json
import unittest

from jsontemplate import template, enum
from jsontemplate.exceptions import ValidationError, TemplateTypeError


class EnumTests(unittest.TestCase):

    dict_template = {
        "first_name": str,
        "last_name": str,
        "age": int,
        "animal": {
            "name": str,
            "age": int,
            "specie": enum('cat', 'dog', 'fish', 'turtle', 'bird'),
        },
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

    def test_validate_enum(self):
        for specie in u'cat', u'dog', u'fish', u'turtle', u'bird':
            self.data['animal']['specie'] = specie
            self.assertIsNone(self.template.validate(self.data))

    def test_bad_template(self):
        self.assertRaises(TemplateTypeError, lambda x: enum(*x), (1, 2, 'dog'))

    def test_invalidate_enum(self):
        self.data['animal']['specie'] = u'bat'
        self.assertRaises(ValidationError, self.template.validate, self.data)

    def test_invalidate_strict_enum(self):
        self.data['animal']['specie'] = 'Dog'
        self.assertRaises(ValidationError, self.template.validate, self.data)

    def test_example(self):
        self.assertEquals(self.template.example(full=True), {
            'first_name': u'example',
            'last_name': u'example',
            'age': 0,
            'animal': {
                'name': u'example',
                'age': 0,
                'specie': u'turtle'
            },
            'location': [u'example', 0],
            'scores': [0.0]
        })

    def test_output(self):
        self.assertEquals(self.template.output(self.data), self.data)

if __name__ == '__main__':
    unittest.main()

