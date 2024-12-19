from attack_handler import AttackHandler
from logging_handler import log

"""
    WARHAMMER 40K 10th edition:
    1 - COMMAND PHASE
    2 - MOVEMENT PHASE
    3 - SHOOTING PHASE
    4 - CHARGE PHASE
    5 - FIGHT PHASE
"""
resolve_attack = AttackHandler()


def command_phase(active_player, inactive_player, boardgame):
    """
        1 - COMMAND PHASE
            1 - COMMAND
            2 - BATTLE-SHOCK
    """
    active_player.new_turn()
    inactive_player.new_turn()


def command(active_player, inactive_player, boardgame):
    # Now increase command points for each one
    active_player.increment_command_points()
    inactive_player.increment_command_points()
    return True


def battle_shock(active_player, inactive_player, boardgame):
    for unit in active_player.get_units_alive():
        if len(unit.models) < unit.unit_initial_force / 2:
            log(f"[REPORT] Unit {unit.name} at half of its initial force, will have to throw the dices for checking "
                f"its moral", True)
            active_player.roll_dice()
            unit.do_moral_check(active_player.last_roll_dice)
    return True


def movement_phase(active_player, inactive_player, boardgame):
    """
        2 - MOVEMENT PHASE
            1 - MOVE UNITS
            2 - REINFORCEMENTS
    """
    # Get enemy's alive units
    enemy_units = inactive_player.get_units_alive()

    for unit in active_player.army.get_units_available_for_moving():
        # Force units to target enemies based on its score
        unit.chase_enemies(enemy_units)
    return True


def move_units(active_player, inactive_player, boardgame):
    # TODO: Check whether it's worth advancing or we might want to shoot instead
    active_player.move_units()
    return True


def reinforcements(active_player, inactive_player, boardgame):
    log(f'[REPORT] [{active_player.name}] has no more units to be placed. Not expecting further reinforcements')
    return True


def shooting_phase(active_player, inactive_player, boardgame):
    """
        3 - SHOOTING PHASE
            1 - SELECT ELIGIBLE UNIT
            2 - SELECT TARGETS
            3 - MAKE RANGED ATTACKS
            4 - REPEAT FOR NEXT ELIGIBLE UNIT
    """
    active_player.set_units_for_shooting()
    return True


def select_eligible_unit(active_player, inactive_player, boardgame):
    active_player.set_next_unit_for_shooting()
    log(f'[REPORT] [{active_player.name}] selects unit: [{active_player.get_selected_unit().name}]')
    return True


def select_targets(active_player, inactive_player, boardgame):
    # Choose targets for that unit
    enemy_units = inactive_player.get_units_alive()
    active_player.set_target_for_selected_unit(enemy_units)
    return True


def make_ranged_attacks(active_player, inactive_player, boardgame):
    selected_unit = active_player.get_selected_unit()
    # At least one model can shoot a target
    if selected_unit.has_shoot:
        attacks = selected_unit.get_models_ranged_attacks()

        for count, attack in enumerate(attacks, start=1):
            log(f'\t----- ----- ----- Resolving attack #{count} out of {len(attacks)} ----- ----- -----')
            resolve_attack.set_new_attack(active_player, inactive_player, attacks[attack])
            resolve_attack.do_attack()
            boardgame.display_board()
    else:
        log(f'\t[PLAYER {active_player.name}] [{selected_unit.name}] will not shoot since '
            f'it does not see anything')


def repeat_for_next_eligible_unit(active_player, inactive_player, boardgame):
    # Check if there are more units to be selected
    if active_player.are_more_units_to_be_selected():
        # Keep on executing the main loop since there are more units to come!
        return False
    else:
        # We are done so far
        return True


def charge_phase(active_player, inactive_player, boardgame):
    """
        4 - CHARGE PHASE
            1 - SELECT ELIGIBLE UNIT
            2 - SELECT TARGETS
            3 - MAKE CHARGE ROLL
            4 - MAKE CHARGE MOVE
            5 - REPEAT FOR NEXT ELIGIBLE UNIT
    """
    active_player.set_units_for_charge()
    return True


def make_charge_roll(active_player, inactive_player, boardgame):
    return True


def fight_phase(active_player, inactive_player, boardgame):
    """
        5 - FIGHT PHASE
            1 - FIGHTS FIRST
            2 - REMAINING COMBATS
                1 - PILE IN
                2 - MAKE MELEE ATTACKS
                3 - CONSOLIDATE
    """
    return True


def fight_first(active_player, inactive_player, boardgame):
    return True


def remaining_combats(active_player, inactive_player, boardgame):
    return True


def pile_in(active_player, inactive_player, boardgame):
    return True


def make_melee_attacks(active_player, inactive_player, boardgame):
    return True


def consolidate(active_player, inactive_player, boardgame):
    return True
