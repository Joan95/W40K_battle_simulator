

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
