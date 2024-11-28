from colorama import Fore
# Constants for bold text
bold_on = "\033[1m"
bold_off = "\033[0m"


class Weapon:
    def __init__(self, name, attributes_tuple):
        self.name = name
        self.range_attack = attributes_tuple[0]
        self.attack = attributes_tuple[1]
        self.ballistic_skill = attributes_tuple[2]
        self.strength = attributes_tuple[3]
        self.armour_penetration = attributes_tuple[4]
        self.damage = attributes_tuple[5]


class MeleeWeapon(Weapon):
    def attack(self):
        pass


class RangedWeapon(Weapon):
    def attack(self):
        pass


class Keywords:
    def __init__(self, name):
        self.name = name


class Model:
    def __init__(self, name, attributes_tuple, keywords, is_warlord=False):
        self.name = name
        self.movement = attributes_tuple[0]
        self.toughness = attributes_tuple[1]
        self.armor_save = attributes_tuple[2]
        self.wounds = attributes_tuple[3]
        self.leadership = attributes_tuple[4]
        self.objective_control = attributes_tuple[5]
        self.invulnerable_save = attributes_tuple[6]
        self.feel_no_pain = attributes_tuple[7]
        self.position = None
        self.weapons = list()
        self.keywords = list(keywords)
        self.is_warlord = is_warlord
        self.is_alive = True

    def set_weapon(self, weapon):
        self.weapons.append(weapon)

    def move(self):
        print(f"{self.name} moving!")


class Unit:
    def __init__(self, name, models):
        self.name = name
        self.models = models
        self.is_warlord_in_the_unit = self.is_warlord_in_the_unit()
        self.is_destroyed = False
        self.has_been_deployed = False

        if self.is_warlord_in_the_unit:
            self.name = f'{Fore.MAGENTA}{bold_on}{self.name} (WL){bold_off}'

    def is_warlord_in_the_unit(self):
        is_warlord = True in [model.is_warlord for model in self.models]
        return is_warlord


class Army:
    def __init__(self):
        self.warlord = None
        self.units = list()
        self.units_left_to_deploy = 0

    def add_unit_into_army(self, unit):
        self.units.append(unit)
        self.units_left_to_deploy += 1

    def are_there_units_still_to_be_deployed(self):
        if self.units_left_to_deploy > 0:
            return True
        else:
            return False

    def set_warlord(self, warlord):
        self.warlord = warlord

    def place_unit(self):
        if self.units_left_to_deploy > 0:
            for unit in self.units:
                if not unit.has_been_deployed:
                    unit.has_been_deployed = True
                    self.units_left_to_deploy -= 1
                    print(f"\t\t[>>] - Placed {unit.name} [left: {self.units_left_to_deploy}]")
                    break
            pass

    def move_unit(self, position):
        pass
