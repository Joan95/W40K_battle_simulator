from enums import ModelPriority, ModelToughnessAgainstWeaponAttack, WeaponType
from logging_handler import *

MAX_THROW_D6 = 6
# Constants for bold text
BOLD_ON = "\033[1m"
BOLD_OFF = "\033[0m"


class ModelKeywords:
    def __init__(self, name):
        self.name = name


class Model:
    def __init__(self, name, attributes_tuple, weapons, keywords, is_warlord=False, more_than_one=False):
        self.name = name
        self.movement = attributes_tuple[0]
        self.toughness = attributes_tuple[1]
        self.salvation = attributes_tuple[2]
        self.wounds = attributes_tuple[3]
        self.leadership = attributes_tuple[4]
        self.objective_control = attributes_tuple[5]
        self.invulnerable_save = attributes_tuple[6]
        self.feel_no_pain = attributes_tuple[7]

        self.keywords = list(keywords)
        self.weapons = list(weapons)

        self.can_be_disengaged_from_unit = 'CHARACTER' in keywords
        self.is_warlord = is_warlord
        self.is_alive = True
        self.is_visible = True
        self.melee_attack_impact_probability = 0
        self.melee_attack_potential_damage = 0
        self.model_potential_attack_damage = None
        self.model_potential_salvation = self.calculate_model_defence_score()
        self.position = None
        self.priority_to_die = self.set_model_priority_to_die(more_than_one)
        self.ranged_attack_impact_probability = 0
        self.ranged_attack_potential_damage = 0

        # Calculate its score
        self.calculate_model_danger_score()
        self.description = self.set_description()

    def calculate_model_defence_score(self):
        chance_of_defence = (MAX_THROW_D6 - (int(self.salvation) - 1)) / 6
        if self.feel_no_pain:
            chance_of_defence += (MAX_THROW_D6 - (int(self.feel_no_pain) - 1)) / 6
        return chance_of_defence

    def calculate_all_weapon_hit_probability_and_damage(self):
        """Calculate the hit probability and potential damage for all weapons."""
        ranged_weapons = [weapon for weapon in self.weapons if weapon.type == WeaponType.RANGED.name]
        melee_weapons = [weapon for weapon in self.weapons if weapon.type == WeaponType.MELEE.name]

        for weapon in ranged_weapons:
            self.ranged_attack_impact_probability += weapon.weapon_hit_probability
            self.ranged_attack_potential_damage += weapon.weapon_potential_damage

        for weapon in melee_weapons:
            self.melee_attack_impact_probability += weapon.weapon_hit_probability
            self.melee_attack_potential_damage += weapon.weapon_potential_damage

        if ranged_weapons:
            self.ranged_attack_impact_probability /= len(ranged_weapons)
        if melee_weapons:
            self.melee_attack_impact_probability /= len(melee_weapons)

    def calculate_model_danger_score(self):
        self.calculate_all_weapon_hit_probability_and_damage()
        # Attack score will be the average a model can deal counting both types of weapon melee and ranged
        self.model_potential_attack_damage = (self.melee_attack_potential_damage +
                                              self.ranged_attack_potential_damage) / 2

    def defend(self, player_attacking, dices, weapon):
        log(f'[MODEL] [{self.name}]\'s salvation is {self.salvation}')
        salvation = self.salvation - weapon.armour_penetration
        log(f'[MODEL] [{self.name}]\'a salvation should be of {salvation} for this attack')
        if self.invulnerable_save and salvation > self.invulnerable_save:
            log(f'[MODEL] [{self.name}] will save with invulnerable save of {self.invulnerable_save} instead')
            used_salvation = self.invulnerable_save
        else:
            used_salvation = self.salvation

        if dices.roll_dices() >= used_salvation:
            log(f'[MODEL] [{self.name}] saves!')
        else:
            if self.feel_no_pain:
                log(f'[MODEL] [{self.name}] has feel no pain of {self.feel_no_pain}')
                damage = 0
                for _ in weapon.damage:
                    if dices.roll_dices() >= self.feel_no_pain:
                        log(f'[MODEL] [{self.name}] wound saved')
                    else:
                        damage += 1
                return self.receive_damage(player_attacking, damage)
            else:
                return self.receive_damage(player_attacking, weapon.damage)

    def get_description(self):
        return self.description

    def get_model_toughness_against_weapon_attack(self, weapon_strength):
        """
        Determine the model's toughness against a weapon's attack strength.

        :param weapon_strength: The strength of the attacking weapon.
        :return: A value from ModelToughnessAgainstWeaponAttack indicating the relative toughness.
        """
        log(f'\t\t[MODEL] {self.name} has toughness of {self.toughness}')

        if weapon_strength == self.toughness:
            return ModelToughnessAgainstWeaponAttack.EQUAL.value
        elif weapon_strength > self.toughness:
            if weapon_strength >= self.toughness * 2:
                return ModelToughnessAgainstWeaponAttack.DOUBLE_WEAK.value
            else:
                return ModelToughnessAgainstWeaponAttack.WEAK.value
        else:
            if weapon_strength * 2 <= self.toughness:
                return ModelToughnessAgainstWeaponAttack.DOUBLE_STRONG.value
            else:
                return ModelToughnessAgainstWeaponAttack.STRONG.value

    def get_model_priority_to_die(self):
        return self.priority_to_die

    def get_ranged_weapons(self):
        return [weapon for weapon in self.weapons if weapon.type == WeaponType.RANGED.name]

    def move(self):
        print(f"{self.name} moving!")

    def receive_damage(self, player_attacking, wounds):
        log(f'[MODEL] [{self.name}] receives {wounds} wound(s)')
        if type(wounds) == str and 'D' in wounds:
            num_wounds = player_attacking.dices.roll_dices(wounds)
        else:
            num_wounds = wounds
        try:
            self.wounds -= num_wounds
        except TypeError:
            self.wounds -= int(num_wounds)

        if self.wounds <= 0:
            self.is_alive = False
            log(f'[MODEL] [{self.name}] has died honorably')
            return True
        else:
            log(f'[MODEL] [{self.name}] remaining wound(s) {self.wounds}')
            return False

    def set_description(self):
        description = f'\n----- ----- ----- ----- ----- ----- ----- ----- -----\n'
        description += f'\t[{self.name.upper()}]\n'
        description += f'\tM\tT\tSV\tW\tLD\tOC\n'
        description += f'\t{self.movement}\t{self.toughness}\t{self.salvation}\t{self.wounds}\t{self.leadership}\t' \
                       f'{self.objective_control}\n'
        if self.invulnerable_save:
            description += f'\tINVULNERABLE SAVE\t{self.invulnerable_save}\n'
        description += f'\tKEYWORDS:\n'
        description += f'\t\t[{", ".join([keyword for keyword in self.keywords])}]\n'
        for weapon in self.weapons:
            description += f'{weapon.get_description()}\n'
        log(description)
        return description

    def set_model_priority_to_die(self, more_than_one):
        if self.is_warlord:
            return ModelPriority.WARLORD.value
        elif 'EPIC HERO' in self.keywords:
            return ModelPriority.EPIC_HERO.value
        elif 'CHARACTER' in self.keywords:
            return ModelPriority.CHARACTER.value
        elif 'INFANTRY' in self.keywords:
            if more_than_one:
                # This is unit basic model
                return ModelPriority.INFANTRY.value
            else:
                # This is boss unit basic model
                return ModelPriority.UNIT_BOSS.value
