import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "python"))

import agents
from agents import FieldReader, Profile, StyleRegistry, generate_profile


class FieldReaderTest(unittest.TestCase):
    def test_positive_rejects_bool(self):
        r = FieldReader({"qty": 5, "tick": True}, "ctx")
        self.assertEqual(r.positive("qty"), 5)
        with self.assertRaises(TypeError):
            r.positive("tick")

    def test_missing_key(self):
        with self.assertRaises(ValueError):
            FieldReader({}, "ctx").positive("qty")


class ProfileTest(unittest.TestCase):
    def test_with_overrides_keeps_original(self):
        p = Profile(5000, 10, 3, 200)
        self.assertEqual(p.with_overrides({"max_lot": 99}).max_lot, 99)
        self.assertEqual(p.max_lot, 10)

    def test_unknown_override(self):
        with self.assertRaises(ValueError):
            Profile(5000, 10, 3, 200).with_overrides({"foo": 1})

    def test_out_of_range(self):
        with self.assertRaises(ValueError):
            Profile(5000, 101, 3, 200)

    def test_package_exports(self):
        from agents.profile import Profile as P
        self.assertIs(agents.Profile, P)
        self.assertEqual(agents.FieldReader.require_int(5, "x"), 5)


class GenerateProfileTest(unittest.TestCase):
    def test_override_applied(self):
        self.assertEqual(generate_profile("moderado", {"max_lot": 50}, 8)["max_lot"], 50)

    def test_same_seed_same_profile(self):
        self.assertEqual(generate_profile("agressivo", {}, 3), generate_profile("agressivo", {}, 3))

    def test_style_ignores_case_and_spaces(self):
        self.assertEqual(generate_profile(" Moderado ", {}, 1), generate_profile("moderado", {}, 1))

    def test_bad_seed(self):
        with self.assertRaises(TypeError):
            generate_profile("moderado", {}, "1")

    def test_unknown_style(self):
        with self.assertRaises(ValueError):
            generate_profile("x", {}, 1)


class StyleRegistryTest(unittest.TestCase):
    def test_names(self):
        self.assertEqual(sorted(StyleRegistry.names()), ["agressivo", "conservador", "moderado"])

    def test_unknown(self):
        with self.assertRaises(ValueError):
            StyleRegistry.resolve("x")


if __name__ == "__main__":
    unittest.main()
