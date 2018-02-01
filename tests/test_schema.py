import os
import pytest
from docker_interface import plugins


@pytest.mark.parametrize('plugin, cls', plugins.Plugin.load_plugins().items())
def test_properties(plugin, cls):
    if not cls.SCHEMA:
        pytest.skip()
    required = ["additionalProperties", "anyOf", "oneOf", "allOf", "not"]
    queue = [('/', cls.SCHEMA)]
    while queue:
        path, property_ = queue.pop()
        assert any([r in property_ for r in required]), \
            "additionalProperties missing for plugin %s: %s" % (plugin, path)

        for name, child in property_.get('properties', {}).items():
            if child.get("type", "object") == "object":
                queue.append((os.path.join(path, name), child))
            child = child.get('items')
            if child and child["type"] == "object":
                queue.append((os.path.join(path, name, "items"), child))

        child = property_.get('additionalProperties')
        if child and child["type"] == "object":
            queue.append((os.path.join(path, "additionalProperties"), child))
