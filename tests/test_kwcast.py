#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import json
import unittest
from copy import deepcopy

from jsontemplate import template, optional, kwcast

class Animal:

    def __init__(self, age=1, name=u'medor', specie=u'dog'):
        self.age = age
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

class KWCastTests(unittest.TestCase):

    dict_template = {
        "first_name": str,
        "last_name": str,
        "age": int,
        "animal": kwcast(Animal, {
            "name": str,
            "age": optional(int),
            "specie": str,
        }),
        "location": (str, int),
        "scores": [{float, int}]
    }

    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None
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

    def test_example(self):
        self.assertEquals(self.template.example(), {
            'first_name': u'example',
            'last_name': u'example',
            'age': 0,
            'animal': Animal(name=u'example', specie=u'example'),
            'location': [u'example', 0],
            'scores': [0.0]
        })

    def test_example_full(self):
        self.assertEquals(self.template.example(full=True), {
            'first_name': u'example',
            'last_name': u'example',
            'age': 0,
            'animal': Animal(name=u'example', specie=u'example', age=0),
            'location': [u'example', 0],
            'scores': [0.0]
        })

    def test_output_optional(self):
        data = deepcopy(self.data)
        data['age'] = int(data['age'])
        del self.data['animal']['age']
        data['animal'] = Animal(**self.data['animal'])
        self.assertEquals(self.template.output(self.data), data)

    def test_output_optional_full(self):
        data = deepcopy(self.data)
        data['age'] = int(data['age'])
        self.data['animal']['age'] = 0
        data['animal'] = Animal(**self.data['animal'])
        del self.data['animal']['age']
        self.assertEquals(self.template.output(self.data, full=True), data)

    def test_output(self):
        data = deepcopy(self.data)
        data['age'] = int(data['age'])
        data['animal'] = Animal(**self.data['animal'])
        self.assertEquals(self.template.output(self.data), data)

if __name__ == '__main__':
    unittest.main()

