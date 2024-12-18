from logging_handler import *
"""
    WARHAMMER 40K 10th edition:
    1 - COMMAND PHASE
    2 - MOVEMENT PHASE
    3 - SHOOTING PHASE
    4 - CHARGE PHASE
    5 - FIGHT PHASE
"""
units_available_for_shooting = list()


def command_phase(active_player, inactive_player):
    """
        1 - COMMAND PHASE
            1 - COMMAND
            2 - BATTLE-SHOCK
    """
    active_player.new_turn()
    inactive_player.new_turn()


def command(active_player, inactive_player):
    # Now increase command points for each one
    active_player.increment_command_points()
    inactive_player.increment_command_points()


def battle_shock(active_player, inactive_player):
    for unit in active_player.get_units_alive():
        if len(unit.models) < unit.unit_initial_force / 2:
            log(f"Unit {unit.name} at half of its initial force, will have to throw the dices for checking its moral",
                True)
            active_player.roll_dice()
            unit.do_moral_check(active_player.last_roll_dice)


def movement_phase(active_player, inactive_player):
    """
        2 - MOVEMENT PHASE
            1 - MOVE UNITS
            2 - REINFORCEMENTS
    """
    pass


def move_units(active_player, inactive_player):
    # Get enemy's alive units
    enemy_units = inactive_player.get_units_alive()

    for unit in active_player.army.get_units_available_for_moving():
        # Force units to target enemies based on its score
        unit.chase_enemies(enemy_units)

    # TODO: Check whether it's worth advancing or we might want to shoot instead
    active_player.move_units()


def reinforcements(active_player, inactive_player):
    pass


def shooting_phase(active_player, inactive_player):
    """
        3 - SHOOTING PHASE
            1 - SELECT ELIGIBLE UNIT
            2 - SELECT TARGETS
            3 - MAKE RANGED ATTACKS
            4 - REPEAT FOR NEXT ELIGIBLE UNIT
    """
    global units_available_for_shooting
    log(f'[Shooting Phase #1] - Choose Unit for performing ranged attacks')
    units_available_for_shooting = active_player.get_available_units_for_shooting()


def select_eligible_unit(active_player, inactive_player):
    log(f'[{active_player.name}] is declaring for following unit(s) shooting phase that: ')
    enemy_units = inactive_player.get_units_alive()

    # 1 - Choose Unit for performing shoots
    for unit in units_available_for_shooting:
        log(f'\t\t----- ----- ----- UNIT DECLARATION ----- ----- -----')
        # 2 - Choose targets for that unit
        unit_can_shoot = active_player.set_target_for_unit(unit, enemy_units)

        # 3 - Perform range attack
        # At least one model can shoot a target
        if unit_can_shoot:
            attacks = unit.get_models_ranged_attacks()

            for count, attack in enumerate(attacks, start=1):
                log('')
                log(f'\t----- ----- ----- Resolving attack #{count} out of {len(attacks)} ----- ----- -----')
                log('')
                killed_models = list()
                killed_models.extend(resolve_player_attack(active_player, inactive_player, attacks[attack]))

                if killed_models:
                    for model in killed_models:
                        log(f'[KILL REPORT] [{model.name}] has died this turn')
                        board.kill_model(model)
        else:
            log(f'\t[PLAYER {active_player.name}] [{unit.name}] will not shoot since it does not see anything')

        # 4 - Repeat with very next Unit
        log('')


def select_targets(active_player, inactive_player):
    pass


def make_ranged_attacks(active_player, inactive_player):
    pass


def repeat_for_next_eligible_unit(active_player, inactive_player):
    pass


def charge_phase(active_player, inactive_player):
    """
        4 - CHARGE PHASE
            1 - SELECT ELIGIBLE UNIT
            2 - SELECT TARGETS
            3 - MAKE CHARGE ROLL
            4 - MAKE CHARGE MOVE
            5 - REPEAT FOR NEXT ELIGIBLE UNIT
    """
    pass


def make_charge_roll(active_player, inactive_player):
    pass


def fight_phase(active_player, inactive_player):
    """
        5 - FIGHT PHASE
            1 - FIGHTS FIRST
            2 - REMAINING COMBATS
                1 - PILE IN
                2 - MAKE MELEE ATTACKS
                3 - CONSOLIDATE
    """
    pass


def fight_first(active_player, inactive_player):
    pass


def remaining_combats(active_player, inactive_player):
    pass


def pile_in(active_player, inactive_player):
    pass


def make_melee_attacks(active_player, inactive_player):
    pass


def consolidate(active_player, inactive_player):
    pass
