from enums import AttackStrength, ResolveAttackSteps
from game_attack_handler import allocate_attack, inflict_damage, hit_roll, saving_throw, wound_roll
from logging_handler import log

"""
    1 - HIT ROLL
    2 - WOUND ROLL
    3 - ALLOCATE ATTACK
    4 - SAVING THROW
    5 - INFLICT DAMAGE
"""


class AttackHandler:
    def __init__(self):
        self.attacker = None
        self.attacking_model = None
        self.attacking_weapon = None
        self.defender = None
        self.defender_unit = None
        self.num_attacks = None
        self.attack_steps = dict()

        # Load attack steps
        self.load_attack_steps()

    def load_attack_steps(self):
        attack_steps = {
            ResolveAttackSteps.HIT_ROLL.name: hit_roll,
            ResolveAttackSteps.WOUND_ROLL.name: wound_roll,
            ResolveAttackSteps.ALLOCATE_ATTACK.name: allocate_attack,
            ResolveAttackSteps.SAVING_THROW.name: saving_throw,
            ResolveAttackSteps.INFLICT_DAMAGE.name: inflict_damage,
        }
        for step_name, function in attack_steps.items():
            self.attack_steps[step_name] = {
                'main_function': function
            }

    def do_attack(self):
        attacks_for_next_step = self.num_attacks
        critical_ones = 0
        for count, step_name in enumerate(self.attack_steps, start=1):
            attack_step = self.attack_steps[step_name]
            attacks_for_next_step, critical_ones = self.execute_attack_step(step_name, attack_step, count,
                                                                            attacks_for_next_step, critical_ones)
            if not attacks_for_next_step + critical_ones:
                # There is not a single hit, just stop
                break

    def execute_attack_step(self, step_name, attack_step, step_number, num_attacks, critical):
        current_step = attack_step['main_function']
        step_name = f'#{step_number} {step_name.replace("_", " ").title().upper()}'
        log(f"[ATTACK step: {step_name}] Attacking model(s) [{self.attacking_model.name}] "
            f"target unit: [{self.defender_unit.name}]",
            True)

        attacks_for_next_step, critical_ones = current_step(self.attacker, self.defender, self.attacking_model,
                                                            self.defender_unit, self.attacking_weapon, num_attacks,
                                                            critical)
        return attacks_for_next_step, critical_ones


    def set_new_attack(self, attacker, defender, attacks):
        self.attacker = attacker
        self.attacking_model = attacks['attacker']
        self.attacking_weapon = attacks['weapon']
        self.defender = defender
        self.defender_unit = attacks['target']
        self.num_attacks = attacks['count']



def resolve_impact_roll(active_player, weapon, num_shoots):
    log(f'\t\t----- ----- ----- HIT ROLL(s) ----- ----- -----')

    # Get weapon number of attacks to do
    log(f'[PLAYER {active_player.name}] there are #{num_shoots} [{weapon.name}] being shoot')
    weapon_num_attacks, weapon_ballistic_skill = weapon.get_num_attacks(active_player.dices)
    total_attacks = num_shoots * weapon_num_attacks

    log(f'[PLAYER {active_player.name}] [{weapon.name}] #{total_attacks} attack(s) will success at '
        f'{weapon_ballistic_skill}\'s')
    active_player.dices.roll_dices(number_of_dices='{}D6'.format(total_attacks))
    attacks = active_player.dices.last_roll_dice_values
    successful_attacks = list()
    critical_attacks = 0
    for count, attack in enumerate(attacks, start=1):
        if attack >= weapon_ballistic_skill:
            if attack == 6:
                critical_attacks += 1
            successful_attacks.append(attack)
    return successful_attacks, critical_attacks


def resolve_wound_roll(active_player, attacks, weapon, enemy_unit):
    log(f'\t\t----- ----- ----- WOUND ROLL(s) ----- ----- -----')
    weapon_strength = weapon.get_strength()

    # Get the enemy unit toughness who will suffer this attack
    enemy_toughness = enemy_unit.get_unit_toughness()

    if weapon_strength == enemy_toughness:
        weapon_attack_strength = AttackStrength.EQUAL.value
    else:
        if weapon_strength > enemy_toughness:
            weapon_attack_strength = AttackStrength.WEAK.value
            if weapon_strength >= enemy_toughness * 2:
                weapon_attack_strength = AttackStrength.DOUBLE_WEAK.value
        else:
            weapon_attack_strength = AttackStrength.STRONG.value
            if weapon_strength * 2 <= enemy_toughness:
                weapon_attack_strength = AttackStrength.DOUBLE_STRONG.value

    log(f'[PLAYER {active_player.name}] [{weapon.name}] #{len(attacks)} attack(s) will success at '
        f'{weapon_attack_strength}\'s')
    active_player.dices.roll_dices(number_of_dices='{}D6'.format(len(attacks)))
    attacks = active_player.dices.last_roll_dice_values
    successful_wounds = list()
    critical_wounds = 0
    for count, attack in enumerate(attacks, start=1):
        if attack >= weapon_attack_strength:
            if attack == 6:
                critical_wounds += 1
            successful_wounds.append(attack)
    return successful_wounds, critical_wounds


def assign_attack(inactive_player, enemy_target):
    log(f'\t\t----- ----- ----- ASSIGNING ATTACKS ----- ----- -----')
    enemy_model = enemy_target.get_next_model_to_die()
    log(f'[{inactive_player.name}] assigns the attack to [{enemy_model.name}]')
    return enemy_model


def salvation_throw(inactive_player, weapon, enemy_model):
    model_salvation = inactive_player.calculate_model_salvation(enemy_model, weapon.get_armour_penetration())

    if inactive_player.dices.roll_dices() < model_salvation:
        log(f'[PLAYER {inactive_player.name}] Attack has not been defended, it\'s a successful wound')
        return False
    else:
        log(f'[PLAYER {inactive_player.name}] Attack has been defended by [{enemy_model.name}]')
        return True


def allocate_damage(active_player, inactive_player, weapon, enemy_model):
    log(f'\t\t----- ----- ----- ALLOCATING DAMAGE ----- ----- -----')
    damage = weapon.get_damage(active_player.dices)
    return inactive_player.allocate_damage(enemy_model, damage)


def resolve_player_attack(active_player, inactive_player, attack_dict):
    killed_models = list()
    model = attack_dict['attacker']
    weapon = attack_dict['weapon']
    num_shoots = attack_dict['count']
    enemy_target = attack_dict["target"]

    num_shoots_increment = weapon.handle_weapon_abilities(model, enemy_target)

    log(f'[PLAYER {active_player.name}] resolving #{num_shoots} impact roll(s) made by '
        f'[{model.name}] with [{weapon.name}]'
        f'[{", ".join([ability.name[0] for ability in weapon.get_abilities()])}] against unit '
        f'[{enemy_target.raw_name}]')

    # 1 - Impact Roll
    successful_impacts, critical_impacts = resolve_impact_roll(active_player, weapon, num_shoots)

    if successful_impacts:
        log(f'[PLAYER {active_player.name}] And there\'s a total of #{len(successful_impacts)} successful '
            f'impacts(s) from last throw {successful_impacts}, from these there are {critical_impacts} '
            f'critical impact(s)')

        # 2 - Wound Roll
        successful_attacks, critical_wounds = resolve_wound_roll(active_player, successful_impacts, weapon,
                                                                 enemy_target)
        if successful_attacks:
            log(f'[PLAYER {active_player.name}] And there\'s a total of #{len(successful_attacks)} successful '
                f'attack(s) from last throw {successful_attacks}, from these there are {critical_wounds} '
                f'critical wound(s)')

            for idx, _ in enumerate(successful_attacks, start=1):
                log(f'[Attack #{idx} out of {len(successful_attacks)}]')

                # 3 - Assign attack
                enemy_model = assign_attack(inactive_player, enemy_target)

                # 4 - Salvation throw
                if not salvation_throw(inactive_player, weapon, enemy_model):
                    # Has not saved
                    # 5 - Allocate damage
                    if allocate_damage(active_player, inactive_player, weapon, enemy_model):
                        # Model has been killed
                        killed_models.append(enemy_model)
        else:
            log(f'[PLAYER {active_player.name}] And there\'s no successful attack... [F]')
    else:
        log(f'[PLAYER {active_player.name}] And there\'s no successful impact... [F]')
    return killed_models