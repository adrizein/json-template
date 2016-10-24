# json-template
Python module for defining JSON templates which can be used to validate json files and cast them into python type-consistent dictionaries.

## Introduction
The goal of json-template is to allow developpers to define JSON templates in Python in a simple and elegant manner.
The most obvious use case of this module is to check and enforce the types of a config file written in JSON instead of just using json.loads and casting every value within the submodules themselves.

## Features
Here a the most important features of json-template:

1. Pure python template definition
2. JSON file structure validation
3. Generation of example JSON file and Python dict from a template
4. Optional fields
5. Default values
6. Casting to custom-defined Python objects (with `*args` and `**kwargs` support)
7. Mixin types
8. Lists with (un)constrained number of elements

## Usage

Here's what a simple template looks like:

```Python
import json
from template import template, optional

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
    "scores": [{float, int}]
    "some_array": [float, int]
})

with open('./config.json', r) as jsonfile:
    config = json.load(jsonfile)
    # raises an exception if config doesn't respect the template
    config_template.validate(config)
```

**What it means:**
 - The `first_name` and `last_name` fields of the JSON file must be strings
 - The `age` field of the JSON file must be a integer
 - If the `animals` field is defined, then it must be a list of objects containing the fields `name`, `age`, and `specie`
 - The `location` field must be a list of **exactly** two elements: the first must be a string, the second an integer
 - The `scores` field must be a list of floats or integers that can be mixed
 - The `some_array` field must be a list containing either only float, or only integers
 
 *Note: In python2.7 `str` will automatically replaced by `unicode` for JSON compliance.*
