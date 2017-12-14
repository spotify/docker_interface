import os
import pytest
from docker_interface.core import plugins


@pytest.mark.parametrize('plugin, cls', plugins.Plugin.load_plugins().items())
def test_properties(plugin, cls):
    if not cls.SCHEMA:
        pytest.skip()
    queue = [('/', cls.SCHEMA)]
    while queue:
        path, property_ = queue.pop()
        assert "additionalProperties" in property_, \
            "additionalProperties missing for plugin %s: %s" % (plugin, path)

        for name, child in property_.get('properties', {}).items():
            if child.get("type", "object") == "object":
                queue.append((os.path.join(path, name), child))
            child = child.get('items')
            if child and child["type"] == "object":
                queue.append((os.path.join(path, name, "items"), child))

        child = property_['additionalProperties']
        if child and child["type"] == "object":
            queue.append((os.path.join(path, "additionalProperties"), child))
