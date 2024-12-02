from enums import WeaponType
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
