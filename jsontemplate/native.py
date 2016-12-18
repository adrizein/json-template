#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This file implements all the template features that are expressible with Python native types.
The validation scheme is the following:
    - str: string
    - int: integer
    - float: float
    - bool: boolean
    - list: array
    - dict: sub-object
    - set of types: value is of one of the type in the set
    - tuple of types: value is an array with the exact number of elements and the exact types of the tuple
    - value: value is of the same type than the templates or absent
    - optional(type): the value is of the specified type or absent
    - any: the value can be anything, but not absent
"""

from __future__ import unicode_literals
import json

# pylint: disable=wildcard-import,unused-wildcard-import
from .exceptions import *

__all__ = ['template', 'mixin', 'optional', 'default']


# python3 compatibility testing
try:
    unicode('hello') # pylint: disable=invalid-name
except NameError:
    unicode = str # pylint: disable=invalid-name,redefined-builtin


def template(value, name='config', strict=False):
    """
    The template function returns a Template which can then be used to validate JSON dictionaries

    :param value: the Python dictionary to be transformed in a template
    :param name: the name of the expected JSON file
    :param strict: if True, then strict mode is activated
    :return: Template object
    """
    if strict:
        if value in (int, float, bool, str, unicode, list, dict):
            return Native(value, name, strict)
    elif isinstance(value, type):
        return Native(value, name, strict)

    if value is any:
        return Template(name, strict)

    if isinstance(value, dict):
        return Dict(value, name, strict)

    if isinstance(value, list):
        return List(value, name, strict)

    if isinstance(value, tuple):
        return Tuple(value, name, strict)

    if isinstance(value, set):
        return mixin(*value, name=name, strict=strict)

    if isinstance(value, (int, float, str, unicode, bool)):
        if isinstance(value, str):
            value = unicode(value)
        return default(type(value), value, name=name, strict=strict)

    if isinstance(value, Template):
        value.rebuild(name, strict)
        return value

    raise TemplateFormatError(value)


class Template(object):
    """
    The Template class is the base class of all templates.
    Its behavior is to allow the value to be of any type
    """

    def __init__(self, name='config', strict=False, value=None):
        self._name = name
        self._strict = strict
        if value is not None:
            self.value = template(value, name, strict)

    def load(self, filepath, full=False, strict=False):
        with open(filepath, 'rb') as data:
            data = json.load(data)
        return self.output(data, full, strict)

    def loads(self, data, full=False, strict=False):
        return self.output(json.loads(data), full, strict)

    # pylint: disable=unused-argument,no-self-use
    def output(self, config, full=False, strict=False):
        return config

    # pylint: disable=unused-argument,no-self-use
    def example(self, full=False):
        return 'example'

    # pylint: disable=unused-argument,no-self-use
    def validate(self, config, strict=False):
        pass

    def rebuild(self, name, strict):
        self._name = name or self._name
        self._strict = strict
        self.value.name = self._name
        self.value.strict = strict

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name
        self.value.name = name

    @property
    def strict(self):
        return self._strict

    @strict.setter
    def strict(self, strict):
        self._strict = strict
        self.value.strict = strict

    def __repr__(self):
        return repr(self.value)


class Native(Template):

    def __init__(self, value, name, strict=False):
        Template.__init__(self, name, strict)
        if value is str:
            self.value = unicode

        elif value in {int, float, bool, dict, list, unicode}:
            self.value = value

        elif not strict:
            self.value = value

        else:
            raise TemplateFormatError(value)

    def validate(self, config, strict=False):
        if (self.strict or strict) and not isinstance(config, self.value):
            raise NativeValidationError(self.value, config, self.name)
        else:
            try:
                old_type = type(config)
                converted = self.value(config)
                back_conv = old_type(converted)
                if back_conv != config:
                    raise NativeValidationError(self.value, config, self.name)
            except (ValueError, TypeError):
                raise NativeValidationError(self.value, config, self.name)

    def example(self, full=False):
        if self.value is unicode:
            return 'example'
        return self.value()

    def output(self, config, full=False, strict=False):
        if self.strict or strict:
            self.validate(config, True)
            return config
        else:
            self.validate(config, strict)
            return self.value(config)

    def rebuild(self, name, strict):
        self._name = name
        self._strict = strict

    @Template.name.setter
    def name(self, name):
        self._name = name

    @Template.strict.setter
    def strict(self, strict):
        self._strict = strict

    def __repr__(self):
        return '<{}>'.format(self.value.__name__)


class Dict(Template):

    def __init__(self, value, name='config', strict=False):
        Template.__init__(self, name, strict)
        self.value = {k: template(v, '{}[{}]'.format(name, k), strict) for k, v in value.items()}

    def validate(self, config, strict=False):
        if not isinstance(config, dict):
            raise NativeValidationError(dict, config, self.name)

        if self.strict or strict:
            keys = set(config.keys()).difference(set(self.value.keys()))
            if len(keys) > 0:
                raise KeysValidationError(keys, self.name)

        for key, subt in self.value.items():
            subt.validate(config.get(key), strict)

    def example(self, full=False):
        example = dict()
        for key, templ in self.value.items():
            value = templ.example(full)
            if value is not None:
                example[key] = value
        return example

    def output(self, config, full=False, strict=False):
        self.validate(config, strict)
        output = dict()
        keys = set(config.keys()).union(set(self.value.keys()))
        for key in keys:
            templ = self.value.get(key)
            value = config.get(key)
            if templ is None and value is not None:
                output[key] = value
                continue
            if templ is not None and value is None:
                value = templ.example(full)
            if templ is not None and value is not None:
                value = templ.output(value, full, strict)
            if value is not None:
                output[key] = value

        return output

    def rebuild(self, name, strict):
        self._name = name
        self._strict = strict
        for key, value in self.value.items():
            value.rebuild('{}[{}]'.format(name, key), strict)

    @Template.name.setter
    def name(self, name):
        self._name = name
        for key, value in self.value.items():
            value.name = '{}[{}]'.format(name, key)

    @Template.strict.setter
    def strict(self, strict):
        self._strict = strict
        for value in self.value.values():
            value.strict = strict


class List(Template):

    def __init__(self, value, name, strict=False):
        Template.__init__(self, name, strict)
        self.value = [template(val, '{}[{}]'.format(name, i), strict) for i, val in enumerate(value)]

    def validate(self, config, strict=False):
        if not isinstance(config, list):
            raise NativeValidationError(list, config, self.name)
        valid = False
        for subt in self.value:
            try:
                for element in config:
                    subt.validate(element, strict)
                valid = True
                return subt
            except ValidationError:
                continue
        if not valid:
            raise ListValidationError(self.value, config, self.name)

    def example(self, full=False):
        return [self.value[0].example()]

    def output(self, config, full=False, strict=False):
        templ = self.validate(config, strict)
        return [templ.output(value, full, strict) for value in config]

    def rebuild(self, name, strict):
        self._name = name
        self._strict = strict
        for i, value in self.value:
            value.rebuild('{}[{}]'.format(name, i), strict)

    @Template.name.setter
    def name(self, name):
        self._name = name
        for i, value in enumerate(self.value):
            value.name = '{}[{}]'.format(name, i)

    @Template.strict.setter
    def strict(self, strict):
        self._strict = strict
        for value in self.value:
            value.strict = strict


class Tuple(List):

    def validate(self, config, strict=False):
        if not isinstance(config, list):
            raise NativeValidationError(list, config, self.name)
        if len(self.value) == len(config):
            for element, subt in zip(config, self.value):
                subt.validate(element, strict)
        else:
            raise SizeValidationError(len(self.value), len(self.value), len(config), self.name)

    def example(self, full=False):
        return [v.example(full) for v in self.value]

    def output(self, config, full=False, strict=False):
        self.validate(config, strict)
        return [v.output(e, full, strict) for v, e in zip(self.value, config)]


class optional(Template): # pylint: disable=invalid-name

    def __init__(self, value, name=None, strict=False):
        Template.__init__(self, name, strict, value)

    def validate(self, config, strict=False):
        if config is not None:
            self.value.validate(config, strict)

    def output(self, config, full=False, strict=False):
        self.validate(config, strict)
        if config is not None:
            return self.value.output(config, full, strict)
        return self.example(full)

    def example(self, full=False):
        if full:
            return self.value.example(full)


# pylint: disable=invalid-name
class default(optional):

    def __init__(self, value, default_value, name=None, strict=False):
        optional.__init__(self, value, name, strict)
        self.default = default_value

    def example(self, full=False):
        return self.default

    def output(self, config, full=False, strict=False):
        if config is None:
            return self.default
        return self.value.output(config, full, strict)


class mixin(Template):

    def __init__(self, *templates, **kwargs):
        name = kwargs.get('name')
        strict = kwargs.get('strict', False)
        Template.__init__(self, name, strict)
        self.value = [template(t, name, strict) for t in templates]

    def example(self, full=False):
        return self.value[0].example(full)

    def validate(self, config, strict=False):
        for t in self.value:
            try:
                t.validate(config, strict)
                return t
            except ValidationError:
                continue
        raise MixinValidationError(self.value, config, self.name)

    def output(self, config, full=False, strict=False):
        t = self.validate(config, strict)
        return t.output(config, full, strict)

    def rebuild(self, name, strict):
        self._name = name
        self._strict = strict
        for v in self.value:
            v.rebuild(name, strict)

    @Template.name.setter
    def name(self, name):
        self._name = name
        for v in self.value:
            v.name = name

    @Template.strict.setter
    def strict(self, strict):
        self._strict = strict
        for v in self.value:
            v.strict = strict
