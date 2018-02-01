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

import os
import json
import textwrap
from docker_interface import plugins, util


def build_property_tree(schema, depth=0):
    for name, property_ in schema.get('properties', {}).items():
        parts = [' ' * depth, '* %s' % name]
        type_ = property_.get('type')
        if type_:
            parts.append(' (:code:`%s`)' % type_)
        parts.append(': %s' % property_.get('description', '').strip('.'))
        default = property_.get('default')
        if default:
            parts.append(' (default: :code:`%s`)' % default)
        parts.append('.')
        yield ''.join(parts)
        if 'properties' in property_:
            for line in build_property_tree(property_, depth + 4):
                yield line


lines = """
Plugin reference
================

This document lists all plugins in order of execution.

""".splitlines()[1:]

classes = plugins.Plugin.load_plugins()
classes['base'] = plugins.base.BasePlugin
schema = {}
for name, plugin_cls in sorted(classes.items(), key=lambda x: x[1].ORDER or 0):
    title = plugin_cls.__name__
    lines.extend([title, '-' * len(title), ''])
    lines.extend([textwrap.dedent(plugin_cls.__doc__), ''])

    tree = list(build_property_tree(plugin_cls.SCHEMA))
    if tree:
        lines.extend(['Properties', '~~~~~~~~~~', ''])
        lines.extend(tree)
    lines.append('')
    schema = util.merge(schema, plugin_cls.SCHEMA)

dirname = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(dirname, 'plugin_reference.rst'), 'w') as fp:
    fp.write("\n".join(lines))

with open(os.path.join(dirname, 'schema.json'), 'w') as fp:
    json.dump(schema, fp, indent=4)
