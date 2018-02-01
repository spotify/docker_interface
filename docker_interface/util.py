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

import contextlib
import os
import socket


TYPES = {
    'integer': int,
    'string': str,
    'number': float,
    'boolean': bool,
    'array': list,
}


def split_path(path, ref=None):
    if ref:
        path = os.path.join(ref, path)
    assert os.path.isabs(path), "expected an absolute path but got '%s'" %  path
    return path.strip(os.path.sep).split(os.path.sep)


def get_value(instance, path, ref=None):
    """
    Get the value from `instance` at the given `path`.
    """
    for part in split_path(path, ref):
        if isinstance(instance, list):
            part = int(part)
        elif not isinstance(instance, dict):
            raise TypeError("expected `list` or `int` but got `%s`" % instance)
        instance = instance[part]
    return instance


def pop_value(instance, path, ref=None):
    """
    Pop the value from `instance` at the given `path`.
    """
    *head, tail = split_path(path, ref)
    for part in head:
        if isinstance(instance, list):
            part = int(part)
        elif not isinstance(instance, dict):
            raise TypeError("expected `list` or `int` but got `%s`" % instance)
        instance = instance[part]
    if isinstance(instance, list):
        tail = int(tail)
    return instance.pop(tail)


def set_value(instance, path, value, ref=None):
    """
    Set `value` on `instance` at the given `path` and create missing intermediate objects.
    """
    *head, tail = split_path(path, ref)
    for part in head:
        instance = instance.setdefault(part, {})
    instance[tail] = value


def set_default(instance, path, value, ref=None):
    """
    Set `value` on `instance` at the given `path` and create missing intermediate objects.
    """
    *head, tail = split_path(path, ref)
    for part in head:
        instance = instance.setdefault(part, {})
    return instance.setdefault(tail, value)


def merge(x, y):
    """
    Merge two dictionaries and raise an error for inconsistencies.
    """
    keys_x = set(x)
    keys_y = set(y)

    for key in keys_y - keys_x:
        x[key] = y[key]

    for key in keys_x & keys_y:
        value_x = x[key]
        value_y = y[key]

        if isinstance(value_x, dict) and isinstance(value_y, dict):
            x[key] = merge(value_x, value_y)
        else:
            if value_x != value_y:
                raise ValueError

    return x


def set_default_from_schema(instance, schema):
    """
    Populate default values on an `instance` given a `schema`.
    """
    for name, property_ in schema.get('properties', {}).items():
        # Set the defaults at this level of the schema
        if 'default' in property_:
            instance.setdefault(name, property_['default'])
        # Descend one level if the property is an object
        if 'properties' in property_:
            set_default_from_schema(instance.setdefault(name, {}), property_)
    return instance


def apply(instance, func, path=None):
    """
    Apply `func` to all fundamental types of `instance`.
    """
    path = path or os.path.sep
    if isinstance(instance, list):
        return [apply(item, func, os.path.join(path, str(i))) for i, item in enumerate(instance)]
    elif isinstance(instance, dict):
        return {key: apply(value, func, os.path.join(path, key)) for key, value in instance.items()}
    return func(instance, path)


def get_free_port(ports=None):
    """
    Get a free port.

    Parameters
    ----------
    ports : iterable
        ports to check
    """
    if ports is None:
        with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as _socket:
            _socket.bind(('', 0))
            _, port = _socket.getsockname()
            return port

    # Get ports from the specified list
    for port in ports:
        with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as _socket:
            try:
                _socket.bind(('', port))
                return port
            except socket.error as ex:
                if ex.errno != 48:
                    raise

    raise RuntimeError("could not find a free port")
