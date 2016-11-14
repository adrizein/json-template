#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

class TemplateError(Exception):
    pass


class TemplateValueError(TemplateError):
    pass


class TemplateFormatError(TemplateError):

    def __init__(self, type):
        msg = "JSON values are converted to either lists," \
              "dicts, unicode strings, ints, floats, or bools, <{}> is not accepted".format(type.__name__)
        TemplateError.__init__(self, msg)


class TemplateTypeError(TemplateError):
    pass


class ValidationError(Exception):
    pass


class NativeValidationError(ValidationError):

    def __init__(self, expected_type, actual_value, name):
        msg = "{} should be a <{}>, but is instead equal to {} of type <{}>".format(
            name,
            expected_type.__name__,
            actual_value,
            type(actual_value).__name__)
        ValidationError.__init__(self, msg)


class ListValidationError(ValidationError):

    def __init__(self, possible_types, actual_values, name):
        msg = "The values of {} can have one of the following types: {}." \
              "Instead, they have mixed types among {}.".format(
            name,
            ', '.join('<{}>'.format(t) for t in possible_types)[:-1],
            ', '.join({'<{}>'.format(type(v).__name__) for v in actual_values})[:-1]
        )
        ValidationError.__init__(self, msg)


class KeysValidationError(ValidationError):

    def __init__(self, keys, name):
        msg = "The following keys are not supposed to be in {}: {}".format(
            name,
            ', '.join('"{}"'.format(key) for key in keys)
        )
        ValidationError.__init__(self, msg)


class SizeValidationError(ValidationError):

    def __init__(self, min, max, actual, name):
        msg = "{} should have between {} and {} elements but has {}".format(name, min, max, actual)
        if min == max:
            msg = "{} should have exactly {} elements but has {}".format(name, max, actual)
        if max is None:
            msg = "{} should have at least {} elements but has {}".format(name, min, actual)
        if min == 0 or min is None:
            msg = "{} should have at most {} elements but has {}".format(name, max, actual)
        ValidationError.__init__(self, msg)


class MixinValidationError(ValidationError):

    def __init__(self, possible_types, actual_value, name):
        msg = "{} can be of the following types: {}. Instead, it is equal to {} of type <{}>".format(
            name,
            ', '.join('<{}>'.format(t) for t in possible_types)[:-1],
            actual_value,
            repr(type(actual_value))
        )
        ValidationError.__init__(self, msg)


class CastValidationError(ValidationError):

    def __init__(self, target, name, error):
        try:
            typename = '<{}>'.format(target.__name__)
        except AttributeError:
            typename = repr(target)
        msg = "{} could not be cast to {} because of the following error:".format(name, typename, error)
        ValidationError.__init__(self, msg)
