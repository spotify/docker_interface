# Copyright 2018 Spotify AB

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
from docker_interface import util


def test_set_value():
    obj = {}
    util.set_value(obj, '/some/value', 1)
    assert obj == {'some': {'value': 1}}


def test_get_value():
    obj = {'some': [{'path': 3}]}
    assert util.get_value(obj, '/some/0/path') == 3


def test_pop_value():
    obj = {'some': [{'path': 3}]}
    assert util.pop_value(obj, '/some/0/path') == 3
    assert obj['some'][0] == {}
    assert util.pop_value(obj, '/some/0') == {}
    assert obj['some'] == []


def test_set_default():
    obj = {'a': 1}
    assert util.set_default(obj, '/a', 5) == 1
    assert obj['a'] == 1
    assert util.set_default(obj, '/b', 3) == 3
    assert obj['b'] == 3
    assert util.set_default(obj, 'd', 'hello', ref='/c') == 'hello'
    assert obj['c']['d'] == 'hello'


def test_merge():
    merged = util.merge({'a': 1, 'b': {'c': 3}, 'd': 8}, {'a': 1, 'b': {'d': 7}, 'e': 9})
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
        util.merge({'a': 1}, {'a': 2})


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
    assert util.set_default_from_schema({}, schema) == {'a': 1, 'b': {'c': []}}


def test_apply():
    assert util.apply({'a': 3, 'b': [4, 5]}, lambda x, _: x ** 2) == {'a': 9, 'b': [16, 25]}


def test_get_free_port_random():
    assert util.get_free_port() > 0


def test_get_free_port_bounded():
    assert 8888 <= util.get_free_port((8888, 9999)) <= 9999
