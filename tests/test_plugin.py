"""Tests for delegation-kit plugin structure and logic."""

import importlib.util
import json
import os
import sys
import types


def _load_plugin():
    """Load the plugin module with mocked tools.registry."""
    # Mock tools.registry
    class MockRegistry:
        def register(self, **kwargs):
            pass

    tools_pkg = types.ModuleType('tools')
    tools_pkg.__path__ = []
    registry_mod = types.ModuleType('tools.registry')
    registry_mod.registry = MockRegistry()
    sys.modules['tools'] = tools_pkg
    sys.modules['tools.registry'] = registry_mod

    # Load plugin
    plugin_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "plugin.py"
    )
    spec = importlib.util.spec_from_file_location("delegation_kit", plugin_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["delegation_kit"] = module  # Register before exec for dataclass support
    spec.loader.exec_module(module)
    return module


class TestPlugin:
    def test_plugin_imports(self):
        dk = _load_plugin()
        assert dk is not None

    def test_lanes_defined(self):
        dk = _load_plugin()
        expected = [
            "judgement-fable", "judgement-sol", "senior-opus",
            "builder-kimi", "builder-terra", "builder-sonnet",
            "clerk-luna", "clerk-glm", "reviewer-sol"
        ]
        for lane in expected:
            assert lane in dk.LANES, f"Missing lane: {lane}"
        assert len(dk.LANES) == 9

    def test_lane_structure(self):
        dk = _load_plugin()
        for name, lane in dk.LANES.items():
            assert lane.name == name
            assert lane.cli in ("claude", "codex", "kimi")
            assert lane.model is not None
            assert lane.effort is not None

    def test_builder_selection(self):
        dk = _load_plugin()
        assert dk._select_builder("Implement feature", False) == "builder-kimi"
        assert dk._select_builder("Design the schema", False) == "builder-sonnet"
        assert dk._select_builder("Implement auth", True) == "builder-sonnet"

    def test_judgement_selection(self):
        dk = _load_plugin()
        assert dk._select_judgement(False, False, False) == ["judgement-fable"]
        assert dk._select_judgement(True, False, False) == ["judgement-fable", "judgement-sol"]
        assert dk._select_judgement(False, True, False) == ["judgement-sol"]

    def test_clerk_selection(self):
        dk = _load_plugin()
        assert dk._select_clerk(False) == "clerk-luna"
        assert dk._select_clerk(True) == "clerk-glm"

    def test_kimi_lane_name_extraction(self):
        dk = _load_plugin()
        lane = dk.LANES["builder-kimi"]
        lane_name = lane.name.split("-")[0]
        assert lane_name == "builder"

    def test_brief_file_creation(self):
        dk = _load_plugin()
        brief = dk._write_brief("Test content")
        assert os.path.exists(brief)
        with open(brief) as f:
            assert f.read() == "Test content"
        os.unlink(brief)

    def test_escalation_map(self):
        dk = _load_plugin()
        assert "builder-kimi" in str(dk.delegation_escalate.__code__.co_consts)
        assert "senior-opus" in str(dk.delegation_escalate.__code__.co_consts)

    def test_status_structure(self):
        dk = _load_plugin()
        status = json.loads(dk.delegation_status())
        assert len(status) == 9
        for name, info in status.items():
            assert "available" in info
            assert "cli" in info
            assert "model" in info
            assert "effort" in info

    def test_plugin_yaml(self):
        import yaml
        plugin_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "plugin.yaml"
        )
        with open(plugin_path) as f:
            data = yaml.safe_load(f)
        assert data["name"] == "delegation-kit"
        assert data["kind"] == "tool"
        assert "version" in data
        assert "description" in data
