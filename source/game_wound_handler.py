from enums import AttackStrength
from logging_handler import *


def resolve_impact_roll(active_player, weapon, num_shoots):
    log(f'\t\t----- ----- ----- IMPACT ROLL(s) ----- ----- -----')

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