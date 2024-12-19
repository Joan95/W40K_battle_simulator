from logging_handler import log

def hit_roll(attacker, defender, model, enemy_target, weapon, num_shoots):
    killed_models = list()
    # Get weapon number of attacks to do
    log(f'[] there are #{num_shoots} [{weapon.name}] being shoot')

    num_shoots_increment = weapon.handle_weapon_abilities(model, enemy_target)

    log(f'\t\t----- ----- ----- HIT ROLL(s) ----- ----- -----')
    weapon_num_attacks, weapon_ballistic_skill = weapon.get_num_attacks(attacker.dices)
    total_attacks = num_shoots * weapon_num_attacks

    log(f'[{weapon.name}] #{total_attacks} attack(s) will success at '
        f'{weapon_ballistic_skill}\'s')
    attacker.dices.roll_dices(number_of_dices='{}D6'.format(total_attacks))
    attacks = attacker.dices.last_roll_dice_values
    successful_attacks = list()
    critical_attacks = 0
    for count, attack in enumerate(attacks, start=1):
        if attack >= weapon_ballistic_skill:
            if attack == 6:
                critical_attacks += 1
            successful_attacks.append(attack)
    return successful_attacks, critical_attacks




    # 1 - Hit Roll
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

def wound_roll():
    pass

def allocate_attack():
    pass

def saving_throw():
    pass

def inflict_damage():
    pass
