#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

#TODO: unittests
#TODO: strict mode

from random import randrange

class template:

    def __init__(self, value):
        if isinstance(value, (type, template, tuple, list, dict, set)):
            self.value = self._str_to_unicode(value)
        else:
            raise Exception("Bad Template")

    @property
    def type(self):
        return type(self.value)

    def output(self, config):
        self._validate(config, self)
        return self._output(config, self)

    def example(self, full=False):
        return self._example(self, full)

    def validate(self, config):
        self._validate(config, self)

    @staticmethod
    def _validate(config, t):
        if not isinstance(t, template):
            t = template(t)

        if isinstance(t.value, template):
            t.value.validate(config)

        elif t.type is type:
            if not isinstance(config, t.value):
                raise TypeError("{} is not a {}".format(config, t.value.__name__))

        elif t.type is dict:
            if not isinstance(config, dict):
                raise TypeError("%r must be a dict" % config)
            for key, subt in t.value.iteritems():
                template(subt).validate(config.get(key))

        elif t.type is list:
            if not isinstance(config, list):
                raise TypeError("%r must be a list" % config)
            ok = False
            for subt in t.value:
                try:
                    for element in config:
                        template(subt).validate(element)
                    ok = True
                except:
                    continue
            if not ok:
                raise TypeError("types are not consistent along the array")

        elif t.type is set:
            # native notation for the mixin
            t = mixin(*t.value)
            t.validate(config)

        elif t.type is tuple:
            if not isinstance(config, list):
                raise TypeError("%r must be a list" % config)
            if len(t.value) == len(config):
                for element, subt in zip(config, t.value):
                    template(subt).validate(element)
            else:
                raise Exception("Invalid structure")
        else:
            raise Exception("Bad Template")


    @staticmethod
    def _example(t, full):
        if not isinstance(t, template):
            t = template(t)

        if t.value is unicode:
            return u'example'

        if t.type is type:
            return t.value()

        if isinstance(t.value, template):
            return t.value.example(full)

        if t.type is dict:
            example = dict()
            for k,v in t.value.iteritems():
                if not isinstance(v, optional) or full:
                    example[k] = template._example(v, full)
                elif isinstance(v, optional):
                    optex = v.example(full)
                    if optex is not None:
                        example[k] = optex
            return example

        if t.type is list:
            typ = t.value[0]
            if typ is None:
                return list()
            return [template(typ).example(full)]

        if t.type is tuple:
            return map(lambda v: template(v).example(full), t.value)

        if t.type is set:
            for typ in t.value:
                return template(typ).example(full)

        raise Exception("Bad Template")


    @staticmethod
    def _str_to_unicode(t):
        if t is str:
            return unicode

        if isinstance(t, dict):
            converted = dict()
            for k,v in t.iteritems():
                converted[k] = template._str_to_unicode(v)
            return converted

        if isinstance(t, (list, tuple)):
            converted = list()
            for e in t:
                converted.append(template._str_to_unicode(e))
            return type(t)(converted)

        if isinstance(t, set):
            converted = set()
            for e in t:
                converted.add(template._str_to_unicode(e))
            return converted

        return t


    @staticmethod
    def _output(config, t):
        if not isinstance(t, template):
            t = template(t)

        if callable(t):
            return t(config)

        if callable(t.value):
            return t.value(config)

        if isinstance(t.value, template):
            return template._output(config, t.value.value)

        if t.type is dict:
            output = dict()
            for k,v in t.value.iteritems():
                o = config.get(k)
                if isinstance(v, optional) and not isinstance(v, default) and o is None:
                    continue
                o = template._output(o, v) or o
                if o is not None:
                    output[k] = o
            return output

        if t.type is list:
            output = list()
            for element in config:
                for subt in t.value:
                    try:
                        template(subt).validate(element)
                        output.append(template._output(element, subt))
                    except:
                        output = list()
                        continue
            return output

        if t.type is tuple:
            output = list()
            for element, subt in zip(config, t.value):
                output.append(template._output(element, subt))
            return output

        if t.type is set:
            # native notation for the mixin
            t = mixin(*t.value)
            return t.output(config)


class optional(template):

    def validate(self, config):
        if config is not None:
            self._validate(config, self.value)

    def example(self, full=False):
        if full:
            return template._example(self.value, full)


class default(optional):

    def __init__(self, value, default_):
        optional.__init__(self, value)
        self.default = default_

    def example(self, full=False):
        return self.default

    def __call__(self, config):
        return config or self.default


class mixin(template):

    def __init__(self, *templates):
        template.__init__(self, templates)

    @property
    def type(self):
        return type(self)

    def example(self, full=False):
        for typ in self.value:
            return template(typ).example(full)

    def validate(self, config):
        ok = False
        for typ in self.value:
            try:
                self._validate(config, typ)
                ok = True
                break
            except:
                continue
        if not ok:
            raise TypeError("mixin")

