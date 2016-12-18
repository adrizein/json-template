#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module contains all the exceptions thrown by the package.
There are two base types for exceptions: TemplateError and ValidationError
"""

from __future__ import unicode_literals


class TemplateError(Exception):
    """
    TemplateError are errors thrown at the instantiation of a template with bad arguments or structure
    """
    pass


class TemplateValueError(TemplateError):
    """
    TemplateValueError are thrown when the arguments of the template do not make sense.
    """
    pass


class TemplateFormatError(TemplateError):
    """
    TemplateFormatError are thrown when the value for a given key has a type that cannot be produced
    by the parsing of a JSON file, like sets or tuples
    """

    def __init__(self, actual_type):
        msg = "JSON values are converted to either lists," \
              "dicts, unicode strings, ints, floats, or bools, <{}> is not accepted".format(actual_type.__name__)
        TemplateError.__init__(self, msg)


class TemplateTypeError(TemplateError):
    """
    TemplateTypeError are thrown when the type of a template value cannot be used by this specific template
    """
    pass


class ValidationError(Exception):
    """
    ValidationErrors are thrown when a JSON dictionary does not fit the specified template
    """
    pass


class NativeValidationError(ValidationError):
    """
    NativeValidationErrors when the value of a JSON dictionary should have one of the native JSON types but doesn't:
        - int
        - float
        - bool
        - string
        - list
    """

    def __init__(self, expected_type, actual_value, name):
        msg = "{} should be a <{}>, but is instead equal to {} of type <{}>".format(
            name,
            expected_type.__name__,
            actual_value,
            type(actual_value).__name__)
        ValidationError.__init__(self, msg)


class ListValidationError(ValidationError):
    """
    ListValidationError are thrown when a list has values whose type are not allowed by the template
    """

    def __init__(self, possible_types, actual_values, name):
        msg = "The values of {} can have one of the following types: {}." \
              "Instead, they have mixed types among {}.".format(
                  name,
                  ', '.join('<{}>'.format(t) for t in possible_types)[:-1],
                  ', '.join({'<{}>'.format(type(v).__name__) for v in actual_values})[:-1])
        ValidationError.__init__(self, msg)


class KeysValidationError(ValidationError):
    """
    KeysValidationError are thrown when a dictionary has keys that are not specified in the template.
    These only happen in strict mode
    """

    def __init__(self, keys, name):
        msg = "The following keys are not supposed to be in {}: {}".format(
            name,
            ', '.join('"{}"'.format(key) for key in keys)
        )
        ValidationError.__init__(self, msg)


class SizeValidationError(ValidationError):
    """
    SizeValidationError are thrown when a list has a number of elements which is outside
    of what is allowed by the template
    """

    def __init__(self, min_size, max_size, actual, name):
        msg = "{} should have between {} and {} elements but has {}".format(name, min_size, max_size, actual)
        if min_size == max_size:
            msg = "{} should have exactly {} elements but has {}".format(name, max_size, actual)
        if max_size is None:
            msg = "{} should have at least {} elements but has {}".format(name, min_size, actual)
        if min_size == 0 or min_size is None:
            msg = "{} should have at most {} elements but has {}".format(name, max_size, actual)
        ValidationError.__init__(self, msg)


class MixinValidationError(ValidationError):
    """
    MixinValidationError are thrown when a value is supposed to be of one of the type allowed by
    the mixin template, but isn't.
    """

    def __init__(self, possible_types, actual_value, name):
        msg = "{} can be of the following types: {}. Instead, it is equal to {} of type <{}>".format(
            name,
            ', '.join('<{}>'.format(t) for t in possible_types)[:-1],
            actual_value,
            repr(type(actual_value))
        )
        ValidationError.__init__(self, msg)


class CastValidationError(ValidationError):
    """
    CastValidationError are thrown when a value could not be cast to the target type
    """

    def __init__(self, target, name, error):
        try:
            typename = '<{}>'.format(target.__name__)
        except AttributeError:
            typename = repr(target)
        msg = "{} could not be cast to {} because of the following error: {}".format(name, typename, error)
        ValidationError.__init__(self, msg)
