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

    def set_weapon(self, weapon):
        self.weapons.append(weapon)

    def move(self):
        print(f"{self.name} moving!")


class Unit:
    def __init__(self, name, models):
        self.name = name
        self.models = models
        self.is_warlord_in_the_unit = self.is_warlord_in_the_unit()

        if self.is_warlord_in_the_unit:
            self.name = f'{Fore.MAGENTA}{bold_on}{self.name} (WL){bold_off}'

    def is_warlord_in_the_unit(self):
        is_warlord = True in [model.is_warlord for model in self.models]
        return is_warlord


class Army:
    def __init__(self):
        self.warlord = None
        self.units = list()

    def add_unit_into_army(self, unit):
        self.units.append(unit)

    def set_warlord(self, warlord):
        self.warlord = warlord

    def move_unit(self, position):
        pass
