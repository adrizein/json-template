#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import json

from .exceptions import *

__all__ = ['template', 'mixin', 'optional', 'default']


# python3 compatibility testing
try:
    unicode('hello')
except:
    unicode = str


def template(value, name='config', strict=False):
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
        if type(value) is str:
            value = unicode(value)
        return default(type(value), value, name=name, strict=strict)

    if isinstance(value, Template):
        value.rebuild(name, strict)
        return value

    raise TemplateFormatError(value)


class Template(object):

    def __init__(self, name='config', strict=False, value=None):
        self._name = name
        self._strict = strict
        if value is not None:
            self.value = template(value, name, strict)

    def load(self, filepath, full=False, strict=False):
        with open(filepath, 'rb') as f:
            data = json.load(f)
        return self.output(data, full, strict)

    def loads(self, data, full=False, strict=False):
        return self.output(json.loads(data), full, strict)

    def output(self, config, full=False, strict=False):
        return config

    def example(self, full=False):
        return 'example'

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
        self.value = {k: template(v, '{}[{}]'.format(name, k), strict) for k,v in value.items()}

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
        for k,v in self.value.items():
            value = v.example(full)
            if value is not None:
                example[k] = value
        return example

    def output(self, config, full=False, strict=False):
        self.validate(config, strict)
        output = dict()
        keys = set(config.keys()).union(set(self.value.keys()))
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
        self._name = name
        self._strict = strict
        for k,v in self.value.items():
            v.rebuild('{}[{}]'.format(name, k), strict)

    @Template.name.setter
    def name(self, name):
        self._name = name
        for k,v in self.value.items():
            v.name = '{}[{}]'.format(name, k)

    @Template.strict.setter
    def strict(self, strict):
        self._strict = strict
        for v in self.value.values():
            v.strict = strict


class List(Template):

    def __init__(self, value, name, strict=False):
        Template.__init__(self, name, strict)
        self.value = [template(v, '{}[{}]'.format(name, i), strict) for i,v in enumerate(value)]

    def validate(self, config, strict=False):
        if not isinstance(config, list):
            raise NativeValidationError(list, config, self.name)
        ok = False
        for subt in self.value:
            try:
                for element in config:
                    subt.validate(element, strict)
                ok = True
                return subt;
            except ValidationError:
                continue
        if not ok:
            raise ListValidationError(self.value, config, self.name)

    def example(self, full=False):
        return [self.value[0].example()]

    def output(self, config, full=False, strict=False):
        t = self.validate(config, strict);
        return [t.output(e, full, strict) for e in config];

    def rebuild(self, name, strict):
        self._name = name
        self._strict = strict
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
        return [v.output(e, full, strict) for v,e in zip(self.value, config)]


class optional(Template):

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


class default(optional):

    def __init__(self, value, default, name=None, strict=False):
        optional.__init__(self, value, name, strict)
        self.default = default

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

