from colorama import Fore
from enums import WeaponType

# Constants for bold text
bold_on = "\033[1m"
bold_off = "\033[0m"
MAX_THROW_D6 = 6


class Weapon:
    def __init__(self, name, attributes_tuple):
        self.name = name
        self.range_attack = attributes_tuple[0]
        self.num_attacks = attributes_tuple[1]
        self.ballistic_skill = attributes_tuple[2]
        self.strength = attributes_tuple[3]
        self.armour_penetration = attributes_tuple[4]
        self.damage = attributes_tuple[5]
        self.weapon_hit_probability = self.calculate_weapon_hit_probability()
        self.weapon_potential_damage = self.calculate_weapon_potential_damage()

    def calculate_weapon_hit_probability(self):
        # First we want to know the chance of success of a single dice,
        # it will be 6 - ballistic_skill (that included) / 6
        # And all this will be ^ to num of attacks from that weapon
        hit_probability_single_dice = (MAX_THROW_D6 - (int(self.ballistic_skill) - 1)) / 6
        hit_probability = hit_probability_single_dice ** self.get_weapon_num_attacks()
        return hit_probability

    def calculate_weapon_potential_damage(self):
        return self.weapon_hit_probability * self.get_weapon_num_attacks() * self.get_weapon_damage()

    def get_weapon_num_attacks(self):
        attacks = self.num_attacks
        try:
            return int(attacks)
        except ValueError:
            # It's a D or +something in the num_attacks characteristic
            if '+' in attacks:
                base, extra = attacks.split('+')
                extra = int(extra)
            else:
                base = attacks
                extra = 0

            return round(int(base.replace('D', '')) / 2) + extra

    def get_weapon_damage(self):
        return int(self.damage)


class MeleeWeapon(Weapon):
    def __init__(self, name, attributes_tuple):
        super().__init__(name, attributes_tuple)
        self.type = WeaponType.MELEE.value

    def attack(self):
        pass


class RangedWeapon(Weapon):
    def __init__(self, name, attributes_tuple):
        super().__init__(name, attributes_tuple)
        self.type = WeaponType.RANGED.value

    def attack(self):
        pass


class Keywords:
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


class Unit:
    def __init__(self, name, models):
        self.name = name
        self.models = models
        self.is_warlord_in_the_unit = self.is_warlord_in_the_unit()
        self.is_destroyed = False
        self.is_engaged = False
        self.is_unit_visible = self.check_unit_visibility()
        self.has_been_deployed = False
        self.targeted_enemy_unit_to_chase = None
        self.unit_initial_force = len(self.models)
        self.unit_potential_damage = None
        self.unit_potential_salvation = None
        self.unit_leadership = None
        self.unit_objective_control = None
        self.unit_survivability = None
        self.unit_total_score = None
        # Calculate all the unit attributes
        self.update_unit_total_score()

        if self.is_warlord_in_the_unit:
            self.name = f'{Fore.MAGENTA}{bold_on}{self.name} (WL){bold_off}'

    def is_warlord_in_the_unit(self):
        is_warlord = True in [model.is_warlord for model in self.models]
        return is_warlord

    def calculate_unit_potential_attack_damage(self):
        self.unit_potential_damage = sum(model.model_potential_attack_damage for model in self.models if model.is_alive)

    def calculate_salvation_chance(self):
        self.unit_potential_salvation = sum(model.model_potential_salvation for model in self.models if model.is_alive)

    def calculate_unit_leadership(self):
        self.unit_leadership = sum(model.leadership for model in self.models if model.is_alive) / len(self.models)

    def calculate_unit_objective_control(self):
        self.unit_objective_control = sum(model.objective_control for model in self.models if model.is_alive)

    def calculate_unit_survivability(self):
        self.unit_survivability = sum(model.wounds * model.model_potential_salvation for model in self.models
                                      if model.is_alive)

    def update_unit_total_score(self):
        # Recalculate everything in case of model's fainted
        self.calculate_unit_potential_attack_damage()
        self.calculate_salvation_chance()
        self.calculate_unit_leadership()
        self.calculate_unit_objective_control()
        self.calculate_unit_survivability()
        # Formula for knowing how challenging a unit is by getting the potential damage it can deal and salvation
        self.unit_total_score = (self.unit_potential_damage * 0.4 +
                                 self.unit_potential_salvation * 0.25 +
                                 self.unit_leadership * 0.1 +
                                 self.unit_objective_control * 0.1 +
                                 self.unit_survivability * 0.15)

    def check_unit_visibility(self):
        is_visible = True in [model.is_visible for model in self.models]
        return is_visible

    def get_unit_movement(self):
        return int(self.models[0].movement.replace('"', ''))


class Army:
    def __init__(self):
        self.warlord = None
        self.units = list()
        self.army_total_score = None

    def add_unit_into_army(self, unit):
        self.units.append(unit)

    def check_units_left_to_deploy(self):
        units_left_to_deploy = 0
        for unit in self.units:
            if not unit.has_been_deployed:
                units_left_to_deploy += 1
        return units_left_to_deploy

    def are_there_units_still_to_be_deployed(self):
        if self.check_units_left_to_deploy() > 0:
            return True
        else:
            return False

    def calculate_danger_score(self):
        self.army_total_score = sum(unit.unit_total_score for unit in self.units if not unit.is_destroyed)

    def set_warlord(self, warlord):
        self.warlord = warlord

    def get_unit_to_place(self):
        if self.check_units_left_to_deploy() > 0:
            for unit in self.units:
                if not unit.has_been_deployed:
                    return unit

    def move_units(self, position):
        pass

    def target_enemies(self, enemies_list):
        pass
