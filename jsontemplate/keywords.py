#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

__all__ = ['size', 'cast', 'starcast', 'kwcast', 'number']

from random import randrange

from .native import Template
from .exceptions import *

number = {int, float}


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
            self.target(config)
        except:
            try:
                x = self.value.output(config, full=False, strict=strict)
                self.target(x)
            except:
                raise CastValidationError(self.target, config, self.name)

    def output(self, config, full, strict):
        self.validate(config, strict)
        return self.target(self.value.output(config, full, strict))


class starcast(cast):

    def validate(self, config, strict=False):
        self.value.validate(config, strict)
        try:
            self.target(*self.value.output(config, full=False, strict=strict))
        except:
            raise CastValidationError(self.target, config, self.name)

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
        except:
            raise CastValidationError(self.target, config, self.name)

    def example(self, full=False):
        return self.target(**self.value.example(full))

    def output(self, config, full=False, strict=False):
        self.validate(config, strict)
        return self.target(**self.value.output(config, full, strict))

