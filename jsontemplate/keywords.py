#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ['size', 'cast', 'starcast', 'kwcast', 'number', 'strict', 'enum']

from random import randrange

from .native import Template, template
from .exceptions import *

number = {int, float}


# python3 compatibility testing
try:
    unicode('hello')
except:
    unicode = str


class strict(Template):

    def __init__(self, value, name='config'):
        Template.__init__(self, name, True, value)

    def validate(self, config, strict=True):
        self.value.validate(config, True)

    def output(self, config, full=False, strict=True):
        return self.value.output(config, full, True)

    def example(self, full=False):
        return self.value.example(full)

    def rebuild(self, name, strict):
        self._name = name
        self.value.rebuild(name, True)

    @Template.strict.setter
    def strict(self, _strict):
        pass


class size(Template):

    def __init__(self, value, min=0, max=None, name=None, strict=False):
        if min > max:
            raise TemplateValueError("Min (%i) can't be inferior to max (%i)" % (min, max))
        if max == 0:
            raise TemplateValueError("Max can't be equal to zero")
        if not isinstance(value, list):
            raise TemplateTypeError("The size keyword only applies to arrays")
        self.min = min
        self.max = max
        Template.__init__(self, name, strict, value)

    def validate(self, config, strict=False):
        self.value.validate(config, strict)
        e = SizeValidationError(self.min, self.max, len(config), self.name)
        if len(config) < self.min:
            raise e
        if not ((self.max is None) or len(config) <= self.max):
            raise e

    def example(self, full=False):
        t = self.value.example(full)
        if full:
            return t*(self.max or 10)
        else:
            return t*randrange(self.min or 1, self.max or 10)

    def output(self, config, full=False, strict=False):
        self.validate(config, strict)
        return self.value.output(config, full, strict)


class cast(Template):

    def __init__(self, target, source=None, name=None, strict=False):
        Template.__init__(self, name, strict, source or {str, bool, int, float, list, dict})
        self.target = target

    def example(self, full=False):
        try:
            return self.target(self.value.example(full))
        except:
            return self.target()

    def validate(self, config, strict=False):
        self.value.validate(config, strict)
        try:
            x = self.value.output(config, full=False, strict=strict)
            self.target(x)
        except:
            try:
                self.target(config)
            except Exception as error:
                raise CastValidationError(self.target, self.name, error)

    def output(self, config, full=False, strict=False):
        self.validate(config, strict)
        return self.target(self.value.output(config, full, strict))


class starcast(cast):

    def validate(self, config, strict=False):
        self.value.validate(config, strict)
        try:
            self.target(*self.value.output(config, full=False, strict=strict))
        except Exception as error:
            raise CastValidationError(self.target, self.name, error)

    def example(self, full=False):
        return self.target(*self.value.example(full))

    def output(self, config, full=False, strict=False):
        self.validate(config, strict)
        return self.target(*self.value.output(config, full, strict))


class kwcast(cast):

    def validate(self, config, strict=False):
        self.value.validate(config, strict)
        try:
            self.target(**self.value.output(config, full=False, strict=strict))
        except Exception as error:
            raise CastValidationError(self.target, self.name, error)

    def example(self, full=False):
        return self.target(**self.value.example(full))

    def output(self, config, full=False, strict=False):
        self.validate(config, strict)
        return self.target(**self.value.output(config, full, strict))


class enum(Template):

    def __init__(self, *values, **kwargs):
        Template.__init__(self, kwargs.get('name'), kwargs.get('strict', False))
        if any(not isinstance(v, (unicode, str)) for v in values):
            raise TemplateTypeError("Enums can only have string values, {} has non string values: {}".format(
                self.name,
                ', '.join(unicode(v) for v in values if not isinstance(v, (str, unicode))))
            )
        self.value = {unicode(value) for value in values}
        self.upper_values = {unicode(v.upper()) for v in values}

    def example(self, full=False):
        for v in self.value:
            return v

    def validate(self, config, strict=False):
        if not isinstance(config, unicode):
            raise NativeValidationError(unicode, config, self.name)
        error = ValidationError('{} can only have the following values: {}. Instead, it is equal to {}'.format(
            self.name,
            ', '.join(str(v) for v in self.value),
            config)
        )
        if self.strict or strict:
            if not config in self.value:
                raise error
        elif config.upper() not in self.upper_values:
            raise error

    def output(self, config, full=False, strict=False):
        self.validate(config, strict)
        return config

    def rebuild(self, name, strict):
        self._name = name
        self._strict = strict

    @Template.name.setter
    def name(self, name):
        self._name = name

    @Template.strict.setter
    def strict(self, strict):
        self._strict = strict
