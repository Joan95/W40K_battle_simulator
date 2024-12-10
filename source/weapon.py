from enums import WeaponType
MAX_THROW_D6 = 6


def set_abilities(abilities):
    abilities_list = []
    for ability in abilities:
        abilities_list.append(WeaponAbility(ability))
    return abilities_list


class WeaponAbility:
    def __init__(self, name):
        self.name = name


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
        """Retrieve the number of attacks for the weapon."""
        attacks = self.num_attacks
        try:
            return int(attacks)
        except ValueError:
            # It's a D or +something in the num_attacks characteristic
            base, extra = (attacks.split('+') + [0])[:2] if '+' in attacks else (attacks, 0)
            return int(base.replace('D', '')) + int(extra)

    def get_weapon_damage(self):
        damage = self.damage
        try:
            return int(damage)
        except ValueError:
            # It's a D or +something in the num_attacks characteristic
            base, extra = (damage.split('+') + [0])[:2] if '+' in damage else (damage, 0)
            return int(base.replace('D', '')) + int(extra)


class MeleeWeapon(Weapon):
    def __init__(self, name, attributes_tuple, weapon_abilities):
        super().__init__(name, attributes_tuple)
        self.type = WeaponType.MELEE.name
        self.abilities = set_abilities(weapon_abilities)
        self.description = self.set_description()

    def attack(self):
        pass

    def get_description(self):
        return self.description

    def set_description(self):
        description = f'\tWeapon name: [{self.name}]\n'
        description += f'\tTYPE\tRAN\tA\tBS\tS\tAP\tD\n'
        description += f'\t{self.type}\t{self.range_attack}\t{self.num_attacks}\t{self.ballistic_skill}\t' \
                       f'{self.strength}\t{self.armour_penetration}\t{self.damage}\n'
        description += f'\tWeapon abilities:\n\t\t[{", ".join([ability.name[0] for ability in self.abilities])}]'
        return description


class RangedWeapon(Weapon):
    def __init__(self, name, attributes_tuple, weapon_abilities):
        super().__init__(name, attributes_tuple)
        self.type = WeaponType.RANGED.name
        self.abilities = set_abilities(weapon_abilities)
        self.description = self.set_description()

    def attack(self):
        pass

    def get_description(self):
        return self.description

    def set_description(self):
        description = f'\tWeapon name: [{self.name}]\n'
        description += f'\tTYPE\tRAN\tA\tBS\tS\tAP\tD\n'
        description += f'\t{self.type}\t{self.range_attack}\t{self.num_attacks}\t{self.ballistic_skill}\t' \
                       f'{self.strength}\t{self.armour_penetration}\t{self.damage}\n'
        description += f'\tWeapon abilities:\n\t\t[{", ".join([ability.name[0] for ability in self.abilities])}]'
        return description
