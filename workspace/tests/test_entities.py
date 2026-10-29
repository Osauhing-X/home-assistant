import ast
import importlib.util
import pathlib
import unittest
ROOT = pathlib.Path(__file__).resolve().parents[2]
COMPONENT = ROOT / "integrations/x_entities/custom_components/extaas_com"
spec = importlib.util.spec_from_file_location("workspace_health", COMPONENT / "workspace_health.py")
health = importlib.util.module_from_spec(spec)
spec.loader.exec_module(health)
class WorkspaceHealthTests(unittest.TestCase):
    def test_exact_health_contract(self):
        self.assertTrue(health.is_workspace_health({"ok": True, "service": "workspace-core"}))
        for value in (None, [], {"ok": 1, "service": "workspace-core"}, {"ok": True, "service": "other"}):
            self.assertFalse(health.is_workspace_health(value))
    def test_target_url_is_fixed_and_bounded(self):
        self.assertEqual(health.workspace_health_url("HOMEASSISTANT.local", 3010), "http://homeassistant.local:3010/health")
        self.assertEqual(health.workspace_health_url("::1", 3010), "http://[::1]:3010/health")
        for host in ("http://example.com", "a/b", "user@host", "host?secret=x", "", None):
            with self.assertRaises(ValueError): health.workspace_health_url(host, 3010)
        for port in (True, 0, 65536, "3010"):
            with self.assertRaises(ValueError): health.workspace_health_url("host", port)
    def test_native_sources_parse_and_entity_publishing_requires_auth(self):
        for source in COMPONENT.rglob("*.py"): ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
        tree = ast.parse((COMPONENT / "api.py").read_text(encoding="utf-8"))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "ExtaasApiView")
        values = {n.targets[0].id: n.value.value for n in cls.body if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and isinstance(n.value, ast.Constant)}
        self.assertIs(values["requires_auth"], True)
if __name__ == "__main__": unittest.main()
