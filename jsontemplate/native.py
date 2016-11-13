#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# TODO: unittests

import json

from .exceptions import *

__all__ = ['template', 'mixin', 'optional', 'default']


def load_json(filename, t=None, full=False, strict=False):
    with open(filename, 'rb') as jsonfile:
        config = json.load(jsonfile)

    if t is None:
        return config

    if isinstance(t, Template):
        return t.output(config, full, strict)

    t = template(t, strict=strict)
    return t.output(config, full)


def template(value, name='config', strict=False):
    if strict:
        if value in {int, float, bool, str, unicode}:
            return Native(value, name, strict)
    elif isinstance(value, type):
        return Native(value, name, strict)

    if isinstance(value, dict):
        return Dict(value, name, strict)

    if isinstance(value, list):
        return Array(value, name, strict)

    if isinstance(value, tuple):
        return Tuple(value, name, strict)

    if isinstance(value, set):
        return mixin(*value, name=name, strict=strict)

    if isinstance(value, (int, float, str, unicode, bool)):
        return default(type(value), value)

    if isinstance(value, Template):
        value.rebuild(name, strict)
        return value

    raise TemplateFormatError(value)


class Template:

    def __init__(self, name='config', strict=False, value=None):
        self._name = name
        self._strict = strict
        if value is not None:
            self.value = template(value, name, strict)

    def output(self, config, full=False, strict=False):
        raise NotImplementedError

    def example(self, full=False):
        raise NotImplementedError

    def validate(self, config, strict=False):
        raise NotImplementedError

    def rebuild(self, name, strict):
        self._name = name
        self._strict = strict

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
            raise ValidationError(self.value, config, self.name)
        else:
            try:
                old_type = type(config)
                converted = self.value(config)
                back_conv = old_type(converted)
                if back_conv != config:
                    raise ValidationError(self.value, config, self.name)
            except (ValueError, TypeError):
                raise ValidationError(self.value, config, self.name)

    def example(self, full=False):
        if self.value is unicode:
            return u'example'
        return self.value()

    def output(self, config, full=False, strict=False):
        if self.strict or strict:
            self.validate(config, True)
            return config
        else:
            self.validate(config, strict)
            return self.value(config)

    def __repr__(self):
        return '<{}>'.format(self.value.__name__)


class Dict(Template):

    def __init__(self, value, name='config', strict=False):
        Template.__init__(self, name, strict)
        self.value = {k: template(v, '{}[{}]'.format(name, k), strict) for k,v in value.iteritems()}

    def validate(self, config, strict=False):
        if not isinstance(config, dict):
            raise ValidationError(dict, config, self.name)

        if self.strict or strict:
            keys = {config.iterkeys()} - {self.value.iterkeys()}
            if len(keys) > 0:
                raise KeysValidationError(keys, self.name)
        for key, subt in self.value.iteritems():
            subt.validate(config.get(key), strict)

    def example(self, full=False):
        example = dict()
        for k,v in self.value.iteritems():
            value = v.example(full)
            if value is not None:
                example[k] = value
        return example

    def output(self, config, full=False, strict=False):
        self.validate(config, strict)
        output = dict()
        keys = set()
        for k in config.iterkeys():
            keys.add(k)
        for k in self.value.iterkeys():
            keys.add(k)
        for k in keys:
            t = self.value.get(k)
            v = config.get(k)
            if t is None and v is not None:
                output[k] = v
                continue
            if t is not None and v is None:
                v = t.example(full)
            if t is not None and v is not None:
                v = t.output(v, full, strict)
            if v is not None:
                output[k] = v

        return output

    def rebuild(self, name, strict):
        self.name = name
        self.strict = strict
        for k,v in self.value.iteritems():
            v.rebuild('{}[{}]'.format(name, k), strict)

    @Template.name.setter
    def name(self, name):
        self._name = name
        for k,v in self.value.iteritems():
            v.name = '{}[{}]'.format(name, k)

    @Template.strict.setter
    def strict(self, strict):
        self._strict = strict
        for v in self.value.itervalues():
            v.strict = strict


class Array(Template):

    def __init__(self, value, name, strict=False):
        Template.__init__(self, name, strict)
        self.value = [template(v, '{}[{}]'.format(name, i), strict) for i,v in enumerate(value)]

    def validate(self, config, strict=False):
        if not isinstance(config, list):
            raise TemplateTypeError("{} should be a list, but is actually <{}>: {}".format(
                self.name,
                type(config).__name__,
                repr(config)))
        ok = False
        for subt in self.value:
            try:
                for element in config:
                    subt.validate(element, strict)
                ok = True
                break
            except ValidationError:
                continue
        if not ok:
            raise ArrayValidationError(self.value, config, self.name)

    def example(self, full=False):
        return [self.value[0].example()]

    def output(self, config, full=False, strict=False):
        self.validate(config, strict)
        output = list()
        for subt in self.value:
            for element in config:
                try:
                    output.append(subt.output(element, full, strict))
                except ValidationError:
                    output = list()
                    break
        return output

    def rebuild(self, name, strict):
        self.name = name
        self.strict = strict
        for i,v in self.value:
            v.rebuild('{}[{}]'.format(name, i), strict)

    @Template.name.setter
    def name(self, name):
        self._name = name
        for i,v in enumerate(self.value):
            v.name = '{}[{}]'.format(name, i)

    @Template.strict.setter
    def strict(self, strict):
        self._strict = strict
        for v in self.value:
            v.strict = strict

class Tuple(Array):

    def validate(self, config, strict):
        if not isinstance(config, list):
            raise ValidationError(list, config, self.name)
        if len(self.value) == len(config):
            for element, subt in zip(config, self.value):
                subt.validate(element, strict)
        else:
            raise SizeValidationError(len(self.value), len(self.value), len(config), self.name)

    def example(self, full=False):
        return [v.example(full) for v in self.value]

    def output(self, config, full=False, strict=False):
        self.validate(config, strict)
        return [v.output(e, full, strict) for v,e in zip(self.value, config)]


class optional(Template):

    def __init__(self, value, name=None, strict=False):
        Template.__init__(self, name, strict, value)

    def validate(self, config, strict):
        if config is not None:
            self.value.validate(config, strict)

    def output(self, config, full=False, strict=False):
        self.validate(config, strict)
        if config is not None:
            return self.value.output(config, full, strict)
        elif full:
            return self.example(full)

    def example(self, full=False):
        if full:
            return self.value.example(full)


class default(optional):

    def __init__(self, value, default_, name=None, strict=False):
        optional.__init__(self, value, name, strict)
        self.default = default_

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
        for typ in self.value:
            return template(typ).example(full)

    def validate(self, config, strict=False):
        ok = False
        for t in self.value:
            try:
                t.validate(config, strict)
                return t
            except ValidationError:
                continue
        if not ok:
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

