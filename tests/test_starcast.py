#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import json

import unittest
from copy import deepcopy

from jsontemplate import template, starcast
from jsontemplate.exceptions import ValidationError


# python3 compatibility testing
try:
    unicode('hello')
except:
    unicode = str


class Animal:

    def __init__(self, age=1, name='medor', specie='dog'):
        self.age = int(age)
        self.specie = specie
        self.name = name

    def __eq__(self, other):
        if isinstance(other, Animal):
            return (self.age == other.age)\
               and (self.specie == other.specie)\
               and (self.name == other.name)
        return False

    def __repr__(self):
        return repr({
            'age': self.age,
            'specie': self.specie,
            'name': self.name
        })


class StarCastTests(unittest.TestCase):

    dict_template = {
        "first_name": str,
        "last_name": str,
        "age": int,
        "animal": starcast(Animal, (int, str, str)),
        "location": (str, int),
        "scores": [{float, int}],
    }

    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None
        cls.json = """{
            "first_name": "Adrien",
            "last_name": "El Zein",
            "age": 25,
            "animal": [8, "kupa", "cat"],
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

    def test_validate_data(self):
        self.assertIsNone(self.template.validate(self.data))

    def test_invalidate_data(self):
        self.data['animal'][0] = 'a12'
        self.assertRaises(ValidationError, self.template.validate, self.data)

    def test_example(self):
        self.assertDictEqual(self.template.example(), {
            'first_name': 'example',
            'last_name': 'example',
            'age': 0,
            'animal': Animal(name='example', age=0, specie='example'),
            'location': ['example', 0],
            'scores': [0.0]
        })

    def test_example_full(self):
        self.assertDictEqual(self.template.example(full=True), {
            'first_name': 'example',
            'last_name': 'example',
            'age': 0,
            'animal': Animal(name='example', specie='example', age=0),
            'location': ['example', 0],
            'scores': [0.0]
        })

    def test_output(self):
        data = deepcopy(self.data)
        data['age'] = int(data['age'])
        data['animal'] = Animal(*self.data['animal'])
        self.assertDictEqual(self.template.output(self.data), data)

if __name__ == '__main__':
    unittest.main()
