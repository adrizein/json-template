#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from template import template

class cardinal(template):

    def __init__(self, value, min=0, max=None):
        template.__init__(self, value)
        self.min = min
        self.max = max

    def validate(self, config):
        self._validate(config, self.value)
        assert len(config) >= self.min
        assert (self.max is None) or len(config) <= self.max

    def example(self, full=False):
        t = [self._(self.value).example(full)]
        if full:
            return t*(self.max or 10)
        else:
            return t*randrange(self.min, self.max or 10)


class cast(template):

    def __init__(self, target, source=None):
        template.__init__(self, source or {str, bool, int, float, list, dict})
        self.target = target

    def example(self, full=False):
        return self.target(template(self.value).example(full))

    def validate(self, config):
        self._validate(config, self.value)

    def __call__(self, config):
        return self.target(config)


class starcast(cast):

    def example(self, full=False):
        return self.target(*template(self.value).example(full))

    def __call__(self, config):
        return self.target(*config)


class kwcast(cast):

    def example(self, full=False):
        return self.target(**template(self.value).example(full))

    def __call__(self, config):
        return self.target(**config)

