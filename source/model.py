from enums import ModelPreferredStyle, ModelPriority, WeaponType
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
        self.is_wounded = False
        self.model_impact_probability_melee_attack = 0
        self.model_impact_probability_ranged_attack = 0
        self.model_potential_damage_melee_attack = 0
        self.model_potential_damage_ranged_attack = 0
        self.model_potential_salvation = self.calculate_model_defence_score()
        self.model_preferred_attack_style = None
        self.position = None
        self.priority_to_die = self.set_model_priority_to_die(more_than_one)

        # Calculate its score
        self.set_model_preferred_attack_style()
        self.description = self.set_description()

    def calculate_model_defence_score(self):
        base_chance_of_defence = (MAX_THROW_D6 - (int(self.salvation) - 1)) / 6
        chance_of_defence = base_chance_of_defence
        if self.feel_no_pain:
            # Now there's a base_chance_of_defence possibilities to save, the rest 1 - base_chance_of_defence
            # must be saved at feel_no_pain, let's calculate the chances and add them to chance_of_defence
            chance_of_defence += (1 - base_chance_of_defence) * (MAX_THROW_D6 - (int(self.feel_no_pain) - 1)) / 6
        return chance_of_defence

    def get_description(self):
        return self.description

    def get_invulnerable_save(self):
        return self.invulnerable_save

    def get_model_melee_weapons_hit_probability_and_damage(self):
        melee_weapons = self.get_model_weapons_melee()
        for weapon in melee_weapons:
            self.model_impact_probability_melee_attack += weapon.weapon_hit_probability
            self.model_potential_damage_melee_attack += weapon.weapon_potential_damage

        if melee_weapons:
            self.model_impact_probability_melee_attack /= len(melee_weapons)

    def get_model_ranged_weapons_hit_probability_and_damage(self):
        ranged_weapons = self.get_model_weapons_ranged()
        for weapon in ranged_weapons:
            self.model_impact_probability_ranged_attack += weapon.weapon_hit_probability
            self.model_potential_damage_ranged_attack += weapon.weapon_potential_damage

        if ranged_weapons:
            self.model_impact_probability_ranged_attack /= len(ranged_weapons)

    def get_model_priority_to_die(self):
        return self.priority_to_die

    def get_model_salvation(self):
        log(f'\t\t[MODEL] {self.name} has salvation of {self.salvation}+ ')
        return self.salvation

    def get_model_toughness(self):
        log(f'\t\t[MODEL] {self.name} has toughness of {self.toughness}')
        return self.toughness

    def get_model_weapons_hit_probability_and_damage(self):
        self.get_model_melee_weapons_hit_probability_and_damage()
        self.get_model_ranged_weapons_hit_probability_and_damage()

    def get_model_weapons_melee(self):
        return [weapon for weapon in self.weapons if weapon.type == WeaponType.MELEE.name]

    def get_model_weapons_ranged(self):
        return [weapon for weapon in self.weapons if weapon.type == WeaponType.RANGED.name]

    def move(self):
        print(f"{self.name} moving!")

    def receive_damage(self, dices, wounds):
        if self.feel_no_pain:
            log(f'[MODEL] [{self.name}] has feel no pain at {self.feel_no_pain}+')
            dices.roll_dices('{}D6'.format(wounds))
            for dice in dices.last_roll_dice_values:
                if dice >= self.feel_no_pain:
                    wounds -= 1

        self.wounds -= wounds
        if self.wounds <= 0:
            self.is_alive = False
            log(f'[MODEL] [{self.name}] receives {wounds} wound(s) and dies honorably')
            return True
        else:
            log(f'[MODEL] [{self.name}] receives {wounds} wound(s). Remaining wound(s) {self.wounds}')
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

    def set_model_preferred_attack_style(self):
        # First of all calculate the hit probability and the potential damage for all the weapons
        self.get_model_weapons_hit_probability_and_damage()
        if (self.model_impact_probability_melee_attack * self.model_potential_damage_melee_attack) > \
                (self.model_impact_probability_ranged_attack * self.model_potential_damage_ranged_attack):
            self.model_preferred_attack_style = ModelPreferredStyle.MELEE_ATTACK
        else:
            self.model_preferred_attack_style = ModelPreferredStyle.RANGED_ATTACK

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
