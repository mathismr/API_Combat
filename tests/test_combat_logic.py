import unittest

from app.crud.CRUD_turn import (
    _determine_priority,
    _affinity_multiplier,
    _calculate_damage,
    _build_cooldown_map,
)
from app.utils.ai import affinity_chart


class TestDeterminePriority(unittest.TestCase):

    def test_user_faster(self):
        self.assertEqual(_determine_priority(100.0, 50.0), (0, 1))

    def test_ai_faster(self):
        self.assertEqual(_determine_priority(50.0, 100.0), (1, 0))

    def test_equal_speed_user_first(self):
        self.assertEqual(_determine_priority(80.0, 80.0), (0, 1))

    def test_zero_speed(self):
        self.assertEqual(_determine_priority(0.0, 0.0), (0, 1))


class TestAffinityMultiplier(unittest.TestCase):

    def test_strong_matchup(self):
        self.assertEqual(_affinity_multiplier("fire", "wind"), 1.5)

    def test_weak_matchup(self):
        self.assertEqual(_affinity_multiplier("fire", "water"), 0.5)

    def test_neutral_matchup(self):
        self.assertEqual(_affinity_multiplier("fire", "light"), 1.0)

    def test_same_element(self):
        self.assertEqual(_affinity_multiplier("fire", "fire"), 1.0)

    def test_case_insensitive(self):
        self.assertEqual(_affinity_multiplier("Fire", "Wind"), 1.5)

    def test_none_attacker(self):
        self.assertEqual(_affinity_multiplier(None, "water"), 1.0)

    def test_none_defender(self):
        self.assertEqual(_affinity_multiplier("fire", None), 1.0)

    def test_unknown_element(self):
        self.assertEqual(_affinity_multiplier("ice", "fire"), 1.0)


class TestAffinityChart(unittest.TestCase):

    def test_all_elements_present(self):
        expected = {"fire", "water", "wind", "earth", "light", "darkness"}
        self.assertEqual(set(affinity_chart.keys()), expected)

    def test_strengths_and_weaknesses_are_lists(self):
        for element, data in affinity_chart.items():
            self.assertIsInstance(data["strengths"], list, f"{element} strengths")
            self.assertIsInstance(data["weaknesses"], list, f"{element} weaknesses")

    def test_symmetry(self):
        """If A is strong against B, then B should be weak against A."""
        for atk_el, data in affinity_chart.items():
            for def_el in data["strengths"]:
                weaknesses = affinity_chart.get(def_el, {}).get("weaknesses", [])
                self.assertIn(
                    atk_el, weaknesses,
                    f"{atk_el} is strong vs {def_el}, but {def_el} does not list {atk_el} as weakness"
                )


class TestCalculateDamage(unittest.TestCase):

    def _make_skill(self, damage=100.0, ratio_stat=None, ratio_percent=0.0):
        skill = {"damage": damage}
        if ratio_stat:
            skill["ratio"] = {"stat": ratio_stat, "percent": ratio_percent}
        return skill

    def _make_monster(self, element="fire", hp=1000.0, atk=100.0, defn=50.0, vit=80.0):
        return {"element": element, "hp": hp, "atk": atk, "def": defn, "vit": vit}

    def test_base_damage_neutral(self):
        skill = self._make_skill(damage=100.0)
        attacker = self._make_monster(element="fire")
        defender = self._make_monster(element="fire", defn=0.0)
        self.assertAlmostEqual(_calculate_damage(skill, attacker, defender), 100.0)

    def test_strong_affinity_bonus(self):
        skill = self._make_skill(damage=100.0)
        attacker = self._make_monster(element="fire")
        defender = self._make_monster(element="wind", defn=0.0)
        self.assertAlmostEqual(_calculate_damage(skill, attacker, defender), 150.0)

    def test_weak_affinity_penalty(self):
        skill = self._make_skill(damage=100.0)
        attacker = self._make_monster(element="fire")
        defender = self._make_monster(element="water", defn=0.0)
        self.assertAlmostEqual(_calculate_damage(skill, attacker, defender), 50.0)

    def test_defense_reduces_damage(self):
        skill = self._make_skill(damage=100.0)
        attacker = self._make_monster(element="fire")
        defender = self._make_monster(element="fire", defn=100.0)
        # 100 * 1.0 / (1 + 100/100) = 50
        self.assertAlmostEqual(_calculate_damage(skill, attacker, defender), 50.0)

    def test_ratio_bonus_atk(self):
        skill = self._make_skill(damage=50.0, ratio_stat="ATK", ratio_percent=0.5)
        attacker = self._make_monster(element="fire", atk=200.0)
        defender = self._make_monster(element="fire", defn=0.0)
        # 50 + 200*0.5 = 150
        self.assertAlmostEqual(_calculate_damage(skill, attacker, defender), 150.0)

    def test_damage_floors_at_zero(self):
        skill = self._make_skill(damage=0.0)
        attacker = self._make_monster()
        defender = self._make_monster(defn=9999.0)
        self.assertEqual(_calculate_damage(skill, attacker, defender), 0.0)

    def test_missing_skill_fields_default_zero(self):
        damage = _calculate_damage({}, {"element": ""}, {"element": "", "def": 0.0})
        self.assertEqual(damage, 0.0)


class TestBuildCooldownMap(unittest.TestCase):

    def test_empty_turns(self):
        self.assertEqual(_build_cooldown_map("m1", []), {})

    def test_single_turn(self):
        turns = [
            {"monsters": [{"id": "m1", "used_skill": "s1"}, {"id": "m2", "used_skill": "s2"}]}
        ]
        result = _build_cooldown_map("m1", turns)
        self.assertEqual(result, {"s1": 0})

    def test_multiple_turns_keeps_latest(self):
        turns = [
            {"monsters": [{"id": "m1", "used_skill": "s1"}]},
            {"monsters": [{"id": "m1", "used_skill": "s2"}]},
            {"monsters": [{"id": "m1", "used_skill": "s1"}]},
        ]
        result = _build_cooldown_map("m1", turns)
        self.assertEqual(result, {"s1": 2, "s2": 1})

    def test_ignores_other_monster(self):
        turns = [
            {"monsters": [{"id": "m1", "used_skill": "s1"}, {"id": "m2", "used_skill": "s3"}]}
        ]
        result = _build_cooldown_map("m1", turns)
        self.assertNotIn("s3", result)

    def test_skips_none_turns(self):
        turns = [None, {"monsters": [{"id": "m1", "used_skill": "s1"}]}]
        result = _build_cooldown_map("m1", turns)
        self.assertEqual(result, {"s1": 1})


if __name__ == "__main__":
    unittest.main()