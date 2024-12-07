from enums import WeaponType

MAX_THROW_D6 = 6


class ModelKeywords:
    def __init__(self, name):
        self.name = name


class Model:
    def __init__(self, name, attributes_tuple, weapons, keywords, is_warlord=False):
        self.name = name
        self.movement = attributes_tuple[0]
        self.toughness = attributes_tuple[1]
        self.salvation = attributes_tuple[2]
        self.wounds = attributes_tuple[3]
        self.leadership = attributes_tuple[4]
        self.objective_control = attributes_tuple[5]
        self.invulnerable_save = attributes_tuple[6]
        self.feel_no_pain = attributes_tuple[7]
        self.position = None
        self.weapons = list(weapons)
        self.keywords = list(keywords)
        self.can_be_disengaged_from_unit = 'CHARACTER' in keywords
        self.is_warlord = is_warlord
        self.is_alive = True
        self.is_visible = True
        self.melee_attack_impact_probability = 0
        self.ranged_attack_impact_probability = 0
        self.melee_attack_potential_damage = 0
        self.ranged_attack_potential_damage = 0
        self.model_potential_attack_damage = None
        self.model_potential_salvation = self.calculate_model_defence_score()
        # Calculate its score
        self.calculate_model_danger_score()

    def move(self):
        print(f"{self.name} moving!")

    def calculate_model_defence_score(self):
        chance_of_defence = (MAX_THROW_D6 - (int(self.salvation) - 1)) / 6
        if self.feel_no_pain:
            chance_of_defence += (MAX_THROW_D6 - (int(self.feel_no_pain) - 1)) / 6
        return chance_of_defence

    def calculate_all_weapon_hit_probability_and_damage(self):
        for weapon in self.weapons:
            if weapon.type == WeaponType.RANGED.value:
                self.ranged_attack_impact_probability += weapon.weapon_hit_probability
                self.ranged_attack_potential_damage += weapon.weapon_potential_damage
            elif weapon.type == WeaponType.MELEE.value:
                self.melee_attack_impact_probability += weapon.weapon_hit_probability
                self.melee_attack_potential_damage += weapon.weapon_potential_damage
        self.ranged_attack_impact_probability /= len([x for x in self.weapons if x.type == WeaponType.RANGED.value])
        self.melee_attack_impact_probability /= len([x for x in self.weapons if x.type == WeaponType.MELEE.value])

    def calculate_model_danger_score(self):
        self.calculate_all_weapon_hit_probability_and_damage()
        # Attack score will be the average a model can deal counting both types of weapon melee and ranged
        self.model_potential_attack_damage = (self.melee_attack_potential_damage +
                                              self.ranged_attack_potential_damage) / 2

