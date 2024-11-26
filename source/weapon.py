

class Weapon:
    def __init__(self, name):
        self.name = name


class MeleeWeapon(Weapon):
    def attack(self):
        pass


class RangedWeapon(Weapon):
    def attack(self):
        pass
