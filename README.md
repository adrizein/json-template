# jsontemplate
Python module for defining templates JSON files which can be used to validate their Python equivalents (obtained with `json.load` for example) and cast them into type-consistent dictionaries.

## Introduction
The goal of jsontemplate is to allow developers to define JSON templates in Python in a simple and elegant manner.

The most obvious use case of this module is to check and enforce the types of a config file written in JSON instead of just using `json.load` and casting every value within the concerned submodules. This module allows for a more explicit and centralized way of controlling the types of the configuration values for a Python project.

The Python 3 port of this package is available on the python3 branch.

## Features
Here a the most important features of jsontemplate:

1. Pure python template definition
2. JSON file structure validation
3. Generation of example JSON file and Python dict from a template
4. Optional fields
5. Default values
6. Casting to custom-defined Python objects
7. Mixin types
8. Lists with or without a constrained number of elements
8. Strict mode (no extra keys and casting)

## Basic usage

Here's what a simple template looks like:

```Python
import json
from jsontemplate import template, optional

config_template = template({
    "first_name": str,
    "last_name": str,
    "age": int,
    "animals": optional([
        {
            "name": str,
            "age": int,
            "specie": str
        }
    ]),
    "location": (str, int),
    "scores": [{float, int}], # {float, int} is a type mixin
    "some_array": [float, int]
})

with open('./config.json', r) as jsonfile:
    config = json.load(jsonfile)
    # raises an exception if config doesn't respect the template
    config_template.validate(config)
```

**What it means:**
 - The `first_name` and `last_name` fields of the JSON file must be strings
 - The `age` field of the JSON file must castable to an integer without loss of information
 - If the `animals` field is defined, then it must be a list of objects containing at least the fields `name`, `age`, and `specie`
 - The `location` field must be a list of **exactly** two elements: the first must be a string, the second an integer
 - The `scores` field must be a list of floats or integers that can be mixed
 - The `some_array` field must be a list containing either only float, or only integers
 
*Note: In Python 2.7 `str` will automatically be replaced by `unicode` for JSON compliance.*

## Advanced usage

### Example generation
With the previously defined template we can do the following:
```Python
>>> config_template.example()
>>> {
    "first_name": u'example',
    "last_name": u'example',
    "age": 0,
    "location": (u'example', 0),
    "scores": [0.0], # or [0]
    "some_array": [0.0]
}

>>> config_template.example(full=True)
>>> {
    "first_name": u'example',
    "last_name": u'example',
    "age": 0,
    "animals": [
        {
            "name": u'example',
            "age": 0,
            "specie": u'example'
        }
    ],
    "location": [u'example', 0],
    "scores": [0.0], # or [0]
    "some_array": [0.0]
}
```

### Default values
Let's modify (and simplify) our template a little:
```Python
>>> config_template = template({
    "first_name": str,
    "last_name": str,
    "age": default(int, 42)
})

>>> config_template.example()
>>> {
    'first_name': u'example',
    'last_name': u'example',
    'age': 42
}

>>> config_template.output({
    'first_name': u'Adrien',
    'last_name': u'El Zein'})
>>> {
    'first_name': u'Adrien',
    'last_name': u'El Zein'
    'age': 42
    }
```
*Note: it is possible to simply write 42 instead of default(int, 42), the type will be infered from the value.*

### Strict mode
By passing `strict=True` to the `template` factory, or in the `validate` and `output` methods,
the template will not accept extra keys in the json file and will enforce the types
instead of checking that the values are castable.

### Casting
It is possible to cast the Python native types of a converted JSON file into more complex and/or custom-defined Python objects.
```Python
from uuid import UUID

def uuid(integer):
    return UUID(int=integer)

from jsontemplate import template, cast, starcast, kwcast

class Animal:
    def __init__(self, name, specie, age):
        self.name = name
        self.specie = specie
        self.age = age
    
    def some_method(self):
        pass
        
config_template = template({
    "id": cast(uuid, source=int), # the first argument of cast doesn't have to be a type, a callable will work too
    "animals": [starcast(Animal, source=(str, str, int))], # Animal(*('string', 'string', integer)) will be called
    "id2": kwcast(UUID, source={'hex': str}) # UUID(**dict(hex='string')) will be called
})

print config_template.output({
    "id": 343,
    "animals": [(u'kupa', u'cat', 12)],
    "id2": u'12344532323473451234453232347345'
})
```

This script will print the following:
```Python
>>> {
    'id': UUID('00000000-0000-0000-0000-000000000157'),
    'animals': [<__main__.Animal instance at 0x000000000>],
    'id2': UUID('12344532-3234-7345-1234-453232347345')
}
```

### Advanced mixins
It is possible to define more complex mixin types than with a simple set, the latter being limited by its inability to contain non-hashable templates.
```Python
from jsontemplate import template, mixin

config_template = template({
    "first_name": str,
    "last_name": str,
    "age": int,
    "animal": mixin({
            "name": str,
            "age": int,
            "specie": str},
            (str, str, int))
})
```
The `animal` field in this template accepts a dictionary or a tuple. This behavior would be impossible to obtain with the set notation for mixins, since dicts can't be elements of sets.

### Cardinal constraints
It is possible to check if a list has an number of elements between a min and a max:
```Python
from jsontemplate import template, mixin

config_template = template({
    "first_name": str,
    "last_name": str,
    "age": int,
    "animals": cardinal([{
            "name": str,
            "age": int,
            "specie": str
        }], min=1, max=5)
})
```
The `animals` field can only contain a list containing at least 1 element and at most 5 elements. `min` defaults to 0 and if `max` is not present, the list length has no upper limit.
