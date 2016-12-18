#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This file implements all the template features which can only be used through "keywords", that is,
python function that return a template with a specific behavior
"""

from __future__ import unicode_literals
from random import randrange

from .native import Template
from .exceptions import *  # pylint: disable=unused-wildcard-import,wildcard-import

__all__ = ['size', 'cast', 'starcast', 'kwcast', 'number', 'strict', 'enum', 'choice']

number = {int, float}  # pylint: disable=invalid-name


# python3 compatibility testing
try:
    unicode('hello')  # pylint: disable=invalid-name
except NameError:
    unicode = str  # pylint: disable=invalid-name,redefined-builtin


class strict(Template):

    def __init__(self, value, name='config'):
        Template.__init__(self, name, True, value)

    def validate(self, config, strict_=True):  # pylint: disable=unused-argument
        self.value.validate(config, True)

    def output(self, config, full=False, strict_=True):  # pylint: disable=unused-argument
        return self.value.output(config, full, True)

    def example(self, full=False):
        return self.value.example(full)

    def rebuild(self, name, strict_):  # pylint: disable=unused-argument
        self._name = name
        self.value.rebuild(name, True)

    @Template.strict.setter
    def strict(self, strict_):
        pass


class size(Template):

    def __init__(self, value, min_value=0, max_value=None, name=None, strict_=False):
        if min_value > max_value:
            raise TemplateValueError("Min (%i) can't be inferior to max (%i)" % (min_value, max_value))
        if max_value == 0:
            raise TemplateValueError("Max can't be equal to zero")
        if not isinstance(value, list):
            raise TemplateTypeError("The size keyword only applies to arrays")
        self.min = min_value
        self.max = max_value
        Template.__init__(self, name, strict_, value)

    def validate(self, config, strict_=False):
        self.value.validate(config, strict_)
        error = SizeValidationError(self.min, self.max, len(config), self.name)
        if len(config) < self.min:
            raise error
        if not ((self.max is None) or len(config) <= self.max):
            raise error

    def example(self, full=False):
        element = self.value.example(full)
        if full:
            return element*(self.max or 10)
        else:
            return element*randrange(self.min or 1, self.max or 10)

    def output(self, config, full=False, strict_=False):
        self.validate(config, strict_)
        return self.value.output(config, full, strict_)


class cast(Template):

    def __init__(self, target, source=None, name=None, strict_=False):
        Template.__init__(self, name, strict_, source or {str, bool, int, float, list, dict})
        self.target = target

    def example(self, full=False):
        try:
            return self.target(self.value.example(full))
        except Exception: # pylint: disable=broad-except
            return self.target()

    def validate(self, config, strict_=False):
        self.value.validate(config, strict_)
        try:
            value = self.value.output(config, full=False, strict=strict_)
            self.target(value)
        except Exception: # pylint: disable=broad-except
            try:
                self.target(config)
            except Exception as error:
                raise CastValidationError(self.target, self.name, error)

    def output(self, config, full=False, strict_=False):
        self.validate(config, strict_)
        return self.target(self.value.output(config, full, strict_))


class starcast(cast):

    def validate(self, config, strict_=False):
        self.value.validate(config, strict_)
        try:
            self.target(*self.value.output(config, full=False, strict=strict_))
        except Exception as error:
            raise CastValidationError(self.target, self.name, error)

    def example(self, full=False):
        return self.target(*self.value.example(full))

    def output(self, config, full=False, strict_=False):
        self.validate(config, strict_)
        return self.target(*self.value.output(config, full, strict_))


class kwcast(cast):

    def validate(self, config, strict_=False):
        self.value.validate(config, strict_)
        try:
            self.target(**self.value.output(config, full=False, strict=strict_))
        except Exception as error:
            raise CastValidationError(self.target, self.name, error)

    def example(self, full=False):
        return self.target(**self.value.example(full))

    def output(self, config, full=False, strict_=False):
        self.validate(config, strict_)
        return self.target(**self.value.output(config, full, strict_))


class enum(Template):

    def __init__(self, *values, **kwargs):
        Template.__init__(self, kwargs.get('name'), kwargs.get('strict_', False))
        if any(not isinstance(v, (unicode, str)) for v in values):
            raise TemplateTypeError(
                "Enums can only have string values, {} has non string values: {}".format(
                    self.name,
                    ', '.join(unicode(v) for v in values if not isinstance(v, (str, unicode)))
                )
            )
        self.value = {unicode(value) for value in values}
        self.upper_values = {unicode(v.upper()) for v in values}

    def example(self, full=False):
        for value in self.value:
            return value

    def validate(self, config, strict_=False):
        if not isinstance(config, unicode):
            raise NativeValidationError(unicode, config, self.name)
        error = ValidationError(
            '{} can only have the following values: {}. Instead, it is equal to {}'.format(
                self.name,
                ', '.join(str(v) for v in self.value),
                config
            )
        )
        if self.strict or strict_:
            if not config in self.value:
                raise error
        elif config.upper() not in self.upper_values:
            raise error

    def output(self, config, full=False, strict_=False):
        self.validate(config, strict_)
        return config

    def rebuild(self, name, strict_):
        self._name = name
        self._strict = strict_

    @Template.name.setter
    def name(self, name):
        self._name = name

    @Template.strict.setter
    def strict(self, strict_):
        self._strict = strict_

choice = enum
