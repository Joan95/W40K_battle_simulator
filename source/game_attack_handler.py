from enums import AttackStrength
from logging_handler import log


def hit_roll(attacker, defender, model, enemy_target, weapon, num_shoots, critical):
    # Get weapon number of attacks to do
    log(f'[HIT ROLL(s)] there are #{num_shoots} [{weapon.name}] being shoot. Attack(s) '
        f'{weapon.get_raw_num_attacks()}')

    num_shoots_increment = weapon.handle_weapon_abilities(model, enemy_target)

    if num_shoots_increment:
        num_shoots_increment = int(num_shoots_increment)
    else:
        num_shoots_increment = 0

    weapon_num_attacks, weapon_ballistic_skill = weapon.get_num_attacks(attacker.dices)
    total_attacks = (num_shoots + num_shoots_increment) * weapon_num_attacks

    log(f'[HIT ROLL(s)][{weapon.name}] #{total_attacks} attack(s) will success at '
        f'{weapon_ballistic_skill}+ [(Base shoots {num_shoots} + Weapon Ability {num_shoots_increment}) x '
        f'Weapon Num Attacks {weapon_num_attacks}]')
    attacker.dices.roll_dices(number_of_dices='{}D6'.format(total_attacks))
    hits = attacker.dices.last_roll_dice_values
    successful_hits = list()
    critical_hits = 0
    for hit in hits:
        if hit == 6:
            critical_hits += 1
        elif hit >= weapon_ballistic_skill:
            successful_hits.append(hit)
    log(f'[HIT ROLL(s)][{weapon.name}] Basic hit(s) [{len(successful_hits)}], '
        f'Critical hit(s) [{critical_hits}] -> Total hit(s) [{len(successful_hits) + critical_hits}]')
    return len(successful_hits), critical_hits


def wound_roll(attacker, defender, model, enemy_target, weapon, successful_hits, critical_hits):
    num_hits = successful_hits + critical_hits
    if num_hits:
        weapon_strength = weapon.get_strength()

        # Get the enemy unit toughness who will suffer this attack
        enemy_toughness = enemy_target.get_unit_toughness()

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

        log(f'[WOUND ROLL(s)][{weapon.name}] #{num_hits} hit(s) will success at '
            f'{weapon_attack_strength}\'s')
        attacker.dices.roll_dices(number_of_dices='{}D6'.format(num_hits))
        wounds = attacker.dices.last_roll_dice_values
        successful_wounds = list()
        critical_wounds = 0
        for wound in wounds:
            if wound == 6:
                critical_wounds += 1
            elif wound >= weapon_attack_strength:
                successful_wounds.append(wound)
        log(f'[WOUND ROLL(s)][{weapon.name}] #{len(successful_wounds)} wound(s), '
            f'#{critical_wounds} critical wounds(s) -> total wound(s) #{len(successful_wounds) + critical_wounds}')
        return len(successful_wounds), critical_wounds
    else:
        log(f'[WOUND ROLL(s)][{weapon.name}] And there\'s no successful hit to be done... [F]')
        return successful_hits, critical_hits


def allocate_attack(attacker, defender, model, enemy_target, weapon, successful_wounds, critical_wounds):
    num_wounds = successful_wounds + critical_wounds
    if num_wounds:
        # 3 - Assign attack
        enemy_model = enemy_target.get_next_model_to_die()
        log(f'[ALLOCATE DAMAGE][{defender.name}] first model to die will be [{enemy_model.name}] from unit '
            f'[{enemy_target.name}]')
        return successful_wounds, critical_wounds
    else:
        log(f'[WOUND ROLL(s)][{weapon.name}] And there\'s no successful wound to be performed... [F]')
        return successful_wounds, critical_wounds


def saving_throw(attacker, defender, model, enemy_target, weapon, successful_wounds, critical_wounds):
    enemy_model = enemy_target.get_next_model_to_die()
    model_salvation = defender.calculate_model_salvation(enemy_model, weapon.get_armour_penetration())
    num_wounds = successful_wounds + critical_wounds
    damage = 0
    defended = 0
    defender.dices.roll_dices('{}D6'.format(num_wounds))
    for throw in defender.dices.last_roll_dice_values:
        if throw < model_salvation:
            damage += 1
        else:
            defended += 1
    log(f'[SAVING THROW(s)][{enemy_model.name}] has successfully defended #{defended} receiving a total of #{damage} '
        f'damage')
    return damage, 0


def inflict_damage(attacker, defender, model, enemy_target, weapon, successful_attacks, critical_attacks):
    # 5 - Allocate damage
    num_wounds = successful_attacks + critical_attacks
    if num_wounds:
        killed_models = list()
        damage = weapon.get_damage(attacker.dices)
        for _ in range(num_wounds):
            enemy_model = enemy_target.get_next_model_to_die()
            if defender.allocate_damage(enemy_model, damage):
                killed_models.append(enemy_model)
    return 0, 0
