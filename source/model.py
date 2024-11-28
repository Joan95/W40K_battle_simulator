
class Model:
    def __init__(self, name, attributes_tuple):
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

    def set_weapon(self, weapon):
        self.weapons.append(weapon)

    def move(self):
        print(f"{self.name} moving!")
