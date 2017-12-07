import pytest
from docker_interface.core import json_util


def test_set_value():
    obj = {}
    json_util.set_value(obj, '/some/value', 1)
    assert obj == {'some': {'value': 1}}


def test_get_value():
    obj = {'some': [{'path': 3}]}
    assert json_util.get_value(obj, '/some/0/path') == 3


def test_pop_value():
    obj = {'some': [{'path': 3}]}
    assert json_util.pop_value(obj, '/some/0/path') == 3
    assert obj['some'][0] == {}
    assert json_util.pop_value(obj, '/some/0') == {}
    assert obj['some'] == []


def test_set_default():
    obj = {'a': 1}
    assert json_util.set_default(obj, '/a', 5) == 1
    assert obj['a'] == 1
    assert json_util.set_default(obj, '/b', 3) == 3
    assert obj['b'] == 3
    assert json_util.set_default(obj, 'd', 'hello', ref='/c') == 'hello'
    assert obj['c']['d'] == 'hello'


def test_merge():
    merged = json_util.merge({'a': 1, 'b': {'c': 3}, 'd': 8}, {'a': 1, 'b': {'d': 7}, 'e': 9})
    assert merged == {
        'a': 1,
        'b': {
            'c': 3,
            'd': 7
        },
        'd': 8,
        'e': 9
    }


def test_merge_conflict():
    with pytest.raises(ValueError):
        json_util.merge({'a': 1}, {'a': 2})


def test_set_default_from_schema():
    schema = {
        "properties": {
            "a": {
                "default": 1
            },
            "b": {
                "properties": {
                    "c": {
                        "default": []
                    }
                }
            }
        }
    }
    assert json_util.set_default_from_schema({}, schema) == {'a': 1, 'b': {'c': []}}


def test_apply():
    assert json_util.apply({'a': 3, 'b': [4, 5]}, lambda x, _: x ** 2) == {'a': 9, 'b': [16, 25]}
