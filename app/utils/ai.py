from typing import Dict, List, Optional

from app.utils.external_requests import fetch_api


affinity_chart = {
    "fire":     {"strengths": ["wind", "earth"],      "weaknesses": ["water"]},
    "water":    {"strengths": ["fire"],               "weaknesses": ["wind", "earth"]},
    "wind":     {"strengths": ["water", "light"],     "weaknesses": ["fire", "darkness"]},
    "earth":    {"strengths": ["water", "darkness"],  "weaknesses": ["fire", "light"]},
    "light":    {"strengths": ["darkness", "earth"],  "weaknesses": ["wind"]},
    "darkness": {"strengths": ["light", "wind"],      "weaknesses": ["earth"]},
}

HP_THRESHOLD = 0.3
DEF_SCALING_FACTOR = 100


class AI:
    def __init__(self, combat: Dict, u_skill: str, turns_data: List[Dict] = None):
        self.combat = combat

        self.u_skill   = fetch_api("skill", u_skill)
        self.ai_skill: Optional[Dict] = None

        self.u_monster  = fetch_api("monster", combat.get("monsters")[0])
        self.ai_monster = fetch_api("monster", combat.get("monsters")[1])

        self._turns_data = turns_data or []

        self._cooldown_map: Dict[str, int] = self._build_cooldown_map()

    # ---------------------
    # Gestion des cooldowns
    # ---------------------

    def _build_cooldown_map(self) -> Dict[str, int]:
        """
        Parcourt tous les tours passés pour mémoriser à quel tour
        chaque skill de l'IA a été utilisé pour la dernière fois.
        """
        cooldown_map: Dict[str, int] = {}
        ai_id = self.ai_monster.get("monsterId")

        for turn_index, turn in enumerate(self._turns_data):
            if not turn:
                continue
            for monster_info in turn.get("monsters", []):
                if monster_info.get("id") == ai_id:
                    skill_id = str(monster_info.get("used_skill"))
                    cooldown_map[skill_id] = turn_index  # écrase → garde le plus récent

        return cooldown_map

    def _get_available_skills(self) -> List[Dict]:
        """
        Retourne les skills de l'IA dont le cooldown est écoulé.
        Un skill est disponible si : jamais utilisé, ou (tour_actuel - dernier_tour) > cooldown.
        """
        current_turn = len(self.combat.get("turns", []))
        available: List[Dict] = []

        for skill_id in self.ai_monster.get("skills", []):
            skill = fetch_api("skill", skill_id)
            if not skill:
                continue

            last_used = self._cooldown_map.get(str(skill_id))
            cooldown   = skill.get("cooldown", 0)

            if last_used is None or (current_turn - last_used) > cooldown:
                available.append(skill)

        return available

    # ------------------------------------------
    # Calcul des affinités et des dégâts estimés
    # ------------------------------------------

    def _affinity_multiplier(self, attacker_element: str, defender_element: str) -> float:
        """
        Retourne le multiplicateur élémentaire :
          1.5× si l'attaquant est fort contre le défenseur
          0.5× si l'attaquant est faible contre le défenseur
          1.0× sinon
        """
        atk_el = attacker_element.lower()
        def_el = defender_element.lower()

        chart = affinity_chart.get(atk_el, {})
        if def_el in chart.get("strengths", []):
            return 1.5
        if def_el in chart.get("weaknesses", []):
            return 0.5
        return 1.0

    def _estimate_damage(self, skill: Dict, attacker: Dict, defender: Dict) -> float:
        """
        Formule :
          dégâts bruts  = skill.damage + attacker[ratio.stat] × ratio.percent
          dégâts finaux = dégâts bruts × affinité / (1 + def / DEF_SCALING_FACTOR)
        """
        base   = skill.get("damage", 0.0)
        ratio  = skill.get("ratio", {})

        stat_map = {
            "HP":  attacker.get("hp",  0.0),
            "ATK": attacker.get("atk", 0.0),
            "DEF": attacker.get("def", 0.0),
            "VIT": attacker.get("vit", 0.0),
        }
        ratio_bonus = stat_map.get(ratio.get("stat", "").upper(), 0.0) * ratio.get("percent", 0.0)

        raw_damage = base + ratio_bonus

        affinity = self._affinity_multiplier(
            attacker.get("element", ""),
            defender.get("element", ""),
        )

        def_mitigation = 1.0 + (defender.get("def", 0.0) / DEF_SCALING_FACTOR)

        return (raw_damage * affinity) / def_mitigation

    # -------
    # Scoring
    # -------

    def _score_skill(self, skill: Dict) -> float:
        """
        Score final d'un skill — plus il est élevé, plus le skill est prioritaire.

        Modificateurs situationnels :
          • IA en danger (HP ≤ seuil)  → +50 % (finir le combat avant de mourir)
          • Adversaire presque mort     → +20 % (enfoncer le clou)
          • Adversaire utilise un skill fort contre l'IA → +30 % (contre-attaque urgente)
        """
        score = self._estimate_damage(skill, self.ai_monster, self.u_monster)

        ai_hp = self.ai_monster.get("hp", 1.0)
        u_hp  = self.u_monster.get("hp",  1.0)

        if ai_hp <= HP_THRESHOLD:          # l'IA est en danger → burst
            score *= 1.5

        if u_hp <= HP_THRESHOLD:           # l'adversaire est presque mort → finir
            score *= 1.2

        # Le skill adverse est fortement avantageux → répondre par les dégâts max
        u_skill_dmg = self._estimate_damage(self.u_skill, self.u_monster, self.ai_monster)
        if u_skill_dmg > self.ai_monster.get("hp", 1.0) * 0.5:
            score *= 1.3

        return score

    # ------------------------
    # Point d'entrée principal
    # ------------------------

    def choose_skill(self) -> str:
        """
        Choisit le skill le plus adapté pour l'IA et retourne son UUID.
        Fallback : premier skill de la liste si tous sont en cooldown.
        """
        available = self._get_available_skills()

        if not available:
            # Tous les skills en cooldown → on réutilise le premier (cas dégénéré)
            fallback_id = self.ai_monster.get("skills", [None])[0]
            self.ai_skill = fetch_api("skill", fallback_id) if fallback_id else None
            return fallback_id

        best = max(available, key=self._score_skill)
        self.ai_skill = best
        return best.get("skillId")