from enums import WeaponType
from logging_handler import log

MAX_THROW_D6 = 6


def set_abilities(abilities):
    abilities_list = []
    for ability in abilities:
        abilities_list.append(WeaponAbility(ability[0]))
    return abilities_list


class WeaponAbility:
    def __init__(self, name):
        self.name = name

    def check_for_weapon_ability(self, model, enemy_target):
        modifier = None
        ability_name = self.name

        # Define a dictionary where keys are abilities and values are their handler functions
        ability_handlers = {
            'Anti-infantry 4': lambda: self.handle_anti_infantry_ability(4),
            'Anti-monster 4': lambda: self.handle_anti_monster_ability(4),
            'Anti-vehicle 3': lambda: self.handle_anti_vehicle_ability(model, 3),
            'Anti-vehicle 4': lambda: self.handle_anti_vehicle_ability(model, 4),
            'Blast': lambda: self.handle_blast_ability(model, enemy_target),
            'Devastating Wounds': lambda: self.handle_devastating_wounds_ability(),
            'Extra Attacks': lambda: self.handle_extra_attacks_ability(),
            'Heavy': lambda: self.handle_heavy_ability(model),
            # Add more abilities here as needed
        }

        # Get the corresponding handler function for the ability
        handler = ability_handlers.get(ability_name)

        if handler:
            # Execute the handler and get the modifier
            modifier = handler()
        else:
            log(f'[WARNING] Unknown weapon ability: {self.name}')

        return modifier

    def handle_extra_attacks_ability(self):
        pass

    def handle_heavy_ability(self, model):
        if not model.has_moved_this_turn():
            log(f'[{model.name}] did not move this turn, applying HEAVY ability: +1 to impact roll.')
            return 1  # Modifier for the impact roll
        else:
            log(f'[{model.name}] moved this turn, HEAVY ability cannot be applied.')
            return 0  # No modifier

    def handle_anti_infantry_ability(self, x):
        pass

    def handle_anti_monster_ability(self, x):
        pass

    def handle_anti_vehicle_ability(self, model, x):
        log(f'[{model.name}] applies ANTI-VEHICLE ability: improved effectiveness against vehicles.')
        # Implement anti-vehicle logic here
        return None

    def handle_blast_ability(self, model, enemy_target):
        modifier = len(enemy_target.get_models_alive()) % 5
        log(f'[{model.name}] [{self.name}] ability: additional attacks against large units. '
            f'[{enemy_target.name}] has {len(enemy_target.get_models_alive())} models, attack modifier +{modifier}')
        return modifier

    def handle_devastating_wounds_ability(self):
        pass


class Weapon:
    def __init__(self, name, attributes_tuple):
        self.name = name
        self.range_attack = attributes_tuple[0]
        self.num_attacks = attributes_tuple[1]
        self.ballistic_skill = int(attributes_tuple[2])
        self.strength = int(attributes_tuple[3])
        self.armour_penetration = attributes_tuple[4]
        self.damage = attributes_tuple[5]
        self.weapon_hit_probability = self.calculate_weapon_hit_probability()
        self.weapon_potential_damage_per_attack = self.calculate_weapon_potential_damage()
        self.target_unit = None
        self.target_distance = None

    def calculate_weapon_hit_probability(self):
        # Calculate the hit probability for each dice
        hit_probability_single_dice = (MAX_THROW_D6 - (self.ballistic_skill - 1)) / 6
        # Account for the number of attacks
        total_hit_probability = 1 - (1 - hit_probability_single_dice) ** self.get_weapon_max_num_attacks()

        log(f'[WEAPON] [{self.name}] hit probability for one attack: {hit_probability_single_dice * 100:.2f}%')
        log(f'[WEAPON] [{self.name}] hit probability for {self.num_attacks} attacks: '
            f'{total_hit_probability * 100:.2f}%')
        return total_hit_probability

    def calculate_weapon_potential_damage(self):
        if isinstance(self.damage, str) and 'D' in self.damage:
            # Split the string into base (number of dice) and extra (sides of the dice)
            parts = self.damage.split('D')

            # If the base is empty, it means we only have something like "D6", so set base damage to 1
            base_damage = int(parts[0]) if parts[0] else 1  # Default base damage is 1 if empty

            # The extra part contains the sides of the dice, default to 6 if not specified
            sides = int(parts[1]) if len(parts) > 1 else 6  # Damage dice sides (D6 by default)

            # Calculate the average damage per die
            average_damage = base_damage * (sides + 1) / 2  # Average roll per die

            # If there's a modifier (e.g., +1), apply it to the damage
            if '+' in self.damage:
                modifier = int(self.damage.split('+')[1])
                average_damage += modifier
        else:
            # If the damage is a fixed number (e.g., "4"), just use it directly
            average_damage = int(self.damage)

        log(f'[WEAPON] [{self.name}] potential damage: {average_damage} per attack')
        return average_damage

    def get_armour_penetration(self):
        log(f'[WEAPON] {self.name} has Armour Penetration of {self.armour_penetration}')
        return self.armour_penetration

    def get_damage(self, dices):
        if isinstance(self.damage, str) and 'D' in self.damage:
            log(f'[WEAPON] {self.name}\'s damage is {self.damage}. Throwing a dice for knowing the amount of damage')
            dices.roll_dices('{}'.format(self.damage))
            damage = dices.last_roll_dice_value
        else:
            damage = int(self.damage)
        log(f'[WEAPON] {self.name}\'s damage is {damage}')
        return damage

    def get_num_attacks(self, dices):
        if isinstance(self.num_attacks, str) and 'D' in self.num_attacks:
            num_attacks = dices.roll_dices(self.num_attacks)
        else:
            num_attacks = self.num_attacks
        log(f'[WEAPON] A single {self.name} performs #{num_attacks} number of attack(s) at BS {self.ballistic_skill}')
        return num_attacks, self.ballistic_skill

    def get_strength(self):
        log(f'[WEAPON] {self.name}\'s strength is {self.strength}')
        return self.strength

    def get_weapon_max_num_attacks(self):
        """Retrieve the number of attacks for the weapon."""
        attacks = self.num_attacks
        try:
            return int(attacks)
        except ValueError:
            # It's a D or +something in the num_attacks characteristic
            base, extra = (attacks.split('+') + [0])[:2] if '+' in attacks else (attacks, 0)
            return int(base.replace('D', '')) + int(extra)    # Do the average if it is a die

    def get_weapon_range_attack(self):
        return int(self.range_attack.replace('"', ''))


class MeleeWeapon(Weapon):
    def __init__(self, name, attributes_tuple, weapon_abilities):
        super().__init__(name, attributes_tuple)
        self.type = WeaponType.MELEE.name
        self.abilities = set_abilities(weapon_abilities)
        self.description = self.set_description()

    def get_abilities(self):
        return self.abilities

    def get_armour_penetration(self):
        return super().get_armour_penetration()

    def get_description(self):
        return self.description

    def get_num_attacks(self, dices):
        return super().get_num_attacks(dices)

    def get_strength(self):
        return super().get_strength()

    def handle_weapon_abilities(self, model, enemy_target):
        for ability in self.abilities:
            ability.check_for_weapon_ability(model, enemy_target)

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

    def get_abilities(self):
        return self.abilities

    def get_armour_penetration(self):
        return super().get_armour_penetration()

    def get_description(self):
        return self.description

    def get_num_attacks(self, dices):
        return super().get_num_attacks(dices)

    def get_strength(self):
        return super().get_strength()

    def handle_weapon_abilities(self, model, enemy_target):
        for ability in self.abilities:
            ability.check_for_weapon_ability(model, enemy_target)

    def set_description(self):
        description = f'\tWeapon name: [{self.name}]\n'
        description += f'\tTYPE\tRAN\tA\tBS\tS\tAP\tD\n'
        description += f'\t{self.type}\t{self.range_attack}\t{self.num_attacks}\t{self.ballistic_skill}\t' \
                       f'{self.strength}\t{self.armour_penetration}\t{self.damage}\n'
        description += f'\tWeapon abilities:\n\t\t[{", ".join([ability.name[0] for ability in self.abilities])}]'
        return description
