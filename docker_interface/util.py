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


def abspath(path, ref=None):
    """
    Create an absolute path.

    Parameters
    ----------
    path : str
        absolute or relative path with respect to `ref`
    ref : str or None
        reference path if `path` is relative

    Returns
    -------
    path : str
        absolute path

    Raises
    ------
    ValueError
        if an absolute path cannot be constructed
    """
    if ref:
        path = os.path.join(ref, path)
    if not os.path.isabs(path):
        raise ValueError("expected an absolute path but got '%s'" %  path)
    return path


def split_path(path, ref=None):
    """
    Split a path into its components.

    Parameters
    ----------
    path : str
        absolute or relative path with respect to `ref`
    ref : str or None
        reference path if `path` is relative

    Returns
    -------
    list : str
        components of the path
    """
    path = abspath(path, ref)
    return path.strip(os.path.sep).split(os.path.sep)


def get_value(instance, path, ref=None):
    """
    Get the value from `instance` at the given `path`.

    Parameters
    ----------
    instance : dict or list
        instance from which to retrieve a value
    path : str
        path to retrieve a value from
    ref : str or None
        reference path if `path` is relative

    Returns
    -------
    value :
        value at `path` in `instance`

    Raises
    ------
    KeyError
        if `path` is not valid
    TypeError
        if a value along the `path` is not a list or dictionary
    """
    for part in split_path(path, ref):
        if isinstance(instance, list):
            part = int(part)
        elif not isinstance(instance, dict):
            raise TypeError("expected `list` or `dict` but got `%s`" % instance)
        try:
            instance = instance[part]
        except KeyError:
            raise KeyError(abspath(path, ref))
    return instance


def pop_value(instance, path, ref=None):
    """
    Pop the value from `instance` at the given `path`.

    Parameters
    ----------
    instance : dict or list
        instance from which to retrieve a value
    path : str
        path to retrieve a value from
    ref : str or None
        reference path if `path` is relative

    Returns
    -------
    value :
        value at `path` in `instance`
    """
    head, tail = os.path.split(abspath(path, ref))
    instance = get_value(instance, head)
    if isinstance(instance, list):
        tail = int(tail)
    return instance.pop(tail)


def set_value(instance, path, value, ref=None):
    """
    Set `value` on `instance` at the given `path` and create missing intermediate objects.

    Parameters
    ----------
    instance : dict or list
        instance from which to retrieve a value
    path : str
        path to retrieve a value from
    value :
        value to set
    ref : str or None
        reference path if `path` is relative
    """
    *head, tail = split_path(path, ref)
    for part in head:
        instance = instance.setdefault(part, {})
    instance[tail] = value


def set_default(instance, path, value, ref=None):
    """
    Set `value` on `instance` at the given `path` and create missing intermediate objects.

    Parameters
    ----------
    instance : dict or list
        instance from which to retrieve a value
    path : str
        path to retrieve a value from
    value :
        value to set
    ref : str or None
        reference path if `path` is relative
    """
    *head, tail = split_path(path, ref)
    for part in head:
        instance = instance.setdefault(part, {})
    return instance.setdefault(tail, value)


def merge(x, y):
    """
    Merge two dictionaries and raise an error for inconsistencies.

    Parameters
    ----------
    x : dict
        dictionary x
    y : dict
        dictionary y

    Returns
    -------
    x : dict
        merged dictionary

    Raises
    ------
    ValueError
        if `x` and `y` are inconsistent
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

    Parameters
    ----------
    instance : dict
        instance to populate default values for
    schema : dict
        JSON schema with default values

    Returns
    -------
    instance : dict
        instance with populated default values
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

    Parameters
    ----------
    instance : dict
        instance to apply functions to
    func : callable
        function with two arguments (instance, path) to apply to all fundamental types recursively
    path : str
        path in the document (defaults to '/')

    Returns
    -------
    instance : dict
        instance after applying `func` to fundamental types
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
        ports to check (obtain a random port by default)

    Returns
    -------
    port : int
        a free port
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
                if ex.errno not in (48, 98):
                    raise

    raise RuntimeError("could not find a free port")
