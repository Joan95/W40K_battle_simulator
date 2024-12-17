import os.path
from battlefield import Battlefield, BoardHandle, Objective
from logging_handler import *
from shapely.geometry import Point
from colorama import init, Fore
from enums import AttackStrength, GamePhase, PlayerRol
from players_army_configuration import players_army_configuration as players_cfg
from database_handler import DatabaseHandler
from player import Player

init()

database = DatabaseHandler(os.path.join('..', 'database', 'database.db'))
players_list = list()
phases = dict()


def load_game_configuration():
    global phases
    local_phases = database.get_phases()
    for phase_name, phase_sequence in local_phases:
        phases[phase_sequence] = {'phase_name': phase_name, 'phase_function': None}

    phases[GamePhase.COMMAND_PHASE.value]['phase_function'] = command_phase
    phases[GamePhase.MOVEMENT_PHASE.value]['phase_function'] = movement_phase
    phases[GamePhase.SHOOTING_PHASE.value]['phase_function'] = shooting_phase
    phases[GamePhase.CHARGE_PHASE.value]['phase_function'] = charge_phase
    phases[GamePhase.FIGHT_PHASE.value]['phase_function'] = fight_phase


def load_players_army(player_1_name, player_2_name):
    global players_list
    players = list(players_cfg.keys())

    def create_player(player_name):
        return Player(database, player_name, players_cfg[player_name],
                      database.get_faction_by_name(players_cfg[player_name]['faction'])[0][1])

    player_1 = create_player(player_1_name)
    player_2 = create_player(player_2_name)

    players_list.extend([player_1, player_2])

    return player_1, player_2


def players_handshake(board_map, player_1, player_2):
    player_1.set_battlefield(board_map)
    player_2.set_battlefield(board_map)
    # Roll for set up the attacker and the defender
    log("[>>] - Setting up the attacker and the defender")
    player_1.roll_players_dice(number_of_dices=1, sides=6)
    player_2.roll_players_dice(number_of_dices=1, sides=6)

    while player_1.get_last_rolled_dice_values()[0] == player_2.get_last_rolled_dice_values()[0]:
        log("[ *] - And it's been a DRAW! Re-rolling dices")
        player_1.roll_players_dice()
        player_2.roll_players_dice()

    if player_1.get_last_rolled_dice_values()[0] > player_2.get_last_rolled_dice_values()[0]:
        player_1.set_rol(PlayerRol.ATTACKER.value)
        player_1.set_deployment_zone(board_map.map_configuration.attacker_zone)
        player_2.set_rol(PlayerRol.DEFENDER.value)
        player_2.set_deployment_zone(board_map.map_configuration.defender_zone)
    else:
        player_1.set_rol(PlayerRol.DEFENDER.value)
        player_1.set_deployment_zone(board_map.map_configuration.defender_zone)
        player_2.set_rol(PlayerRol.ATTACKER.value)
        player_2.set_deployment_zone(board_map.map_configuration.attacker_zone)


def initiatives(player_1, player_2):
    log("[>>] - Rolling dices for deciding initiatives")
    player_1.roll_players_dice(number_of_dices=1, sides=6)
    player_2.roll_players_dice(number_of_dices=1, sides=6)

    while player_1.get_last_rolled_dice_values()[0] == player_2.get_last_rolled_dice_values()[0]:
        log("[ *] - And it's been a DRAW! Re-rolling dices")
        player_1.roll_players_dice()
        player_2.roll_players_dice()

    if player_1.get_last_rolled_dice_values()[0] > player_2.get_last_rolled_dice_values()[0]:
        log(f"\t{player_1.name} will go first!", True)
        players_turn = (player_1, player_2)
    else:
        log(f"\t{player_2.name} will go first!", True)
        players_turn = (player_2, player_1)

    turns = list()
    for x in range(1, 6):
        turns.append([x, players_turn])
    return turns


def place_army_into_boardgame(turns):
    player_count = 0
    players = turns[0][1]
    while players[0].has_units_to_deploy() or players[1].has_units_to_deploy():
        player = players[player_count % len(players)]
        if player.has_units_to_deploy():
            player.deploy_units()
        player_count += 1


def command_phase(active_player, inactive_player):
    # Calculate current army score for both players
    active_player.army.calculate_danger_score()
    inactive_player.army.calculate_danger_score()

    # Now increase command points for each one
    active_player.increment_command_points()
    inactive_player.increment_command_points()

    for unit in active_player.get_units_alive():
        if len(unit.models) < unit.unit_initial_force / 2:
            log(f"Unit {unit.name} at half of its initial force, will have to throw the dices for checking its moral",
                True)
            active_player.roll_dice()
            unit.do_moral_check(active_player.last_roll_dice)


def movement_phase(active_player, inactive_player):
    # Get enemy's alive units
    enemy_units = inactive_player.get_units_alive()

    for unit in active_player.army.get_units_available_for_moving():
        # Force units to target enemies based on its score
        unit.chase_enemies(enemy_units)
    active_player.move_units()
    active_player.battlefield.display_board()


def resolve_impact_roll(active_player, weapon):
    log(f'IMPACT ROLL(s):')
    # Get weapon number of attacks to do
    log(f'[PLAYER {active_player.name}] [{weapon.name}] attacks {weapon.num_attacks}')
    weapon_num_attacks, weapon_ballistic_skill = weapon.get_num_attacks(active_player.dices)

    log(f'[PLAYER {active_player.name}] [{weapon.name}] attack(s) will success at {weapon_ballistic_skill}\'s')
    active_player.dices.roll_dices(number_of_dices='{}D6'.format(weapon_num_attacks))
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
    log(f'WOUND ROLL(s):')
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
    log(f'Assigning attacks')
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
    damage = weapon.get_damage(active_player.dices)
    return inactive_player.allocate_damage(enemy_model, damage)


def resolve_player_attacks(active_player, inactive_player, active_player_attacks):
    log(f'Resolving attacks')
    killed_models = list()
    for weapon in active_player_attacks:
        log(f'[PLAYER {active_player.name}] resolving attacks for '
            f'[{active_player_attacks[weapon]["attacker"].name}] [{weapon.name}] against '
            f'[{active_player_attacks[weapon]["target"].raw_name}]')

        # 1 - Impact Roll
        successful_impacts, critical_impacts = resolve_impact_roll(active_player, weapon)

        if successful_impacts:
            log(f'[PLAYER {active_player.name}] And there\'s a total of #{len(successful_impacts)} successful '
                f'impacts(s) from last throw {successful_impacts}, from these there are {critical_impacts} '
                f'critical impact(s)')

            # 2 - Wound Roll
            enemy_target = active_player_attacks[weapon]["target"]
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


def shooting_phase(active_player, inactive_player):
    enemy_units = inactive_player.get_units_alive()
    units_available_for_shooting = active_player.get_available_units_for_shooting()

    # 1 - Choose Unit for performing shoots
    for unit in units_available_for_shooting:
        # 2 - Choose targets for that unit
        unit_can_shoot = active_player.set_target_for_unit(unit, enemy_units)

        # 3 - Perform range attack
        # At least one model can shoot a target
        if unit_can_shoot:
            attacks = unit.get_models_ranged_attacks()
            killed_models = resolve_player_attacks(active_player, inactive_player, attacks)
            if killed_models:
                for model in killed_models:
                    log(f'[REPORT] [{model.name}] has died this turn')
                    board.kill_model(model)

        # 4 - Repeat with very next Unit


def charge_phase(active_player, inactive_player):
    pass


def fight_phase(active_player, inactive_player):
    pass


def execute_phase(active_player, inactive_player):
    for phase_sequence in phases:
        phase = phases[phase_sequence]
        phase_name_enum = GamePhase(phase_sequence).name.replace("_", " ").title()
        log(f"\t[{active_player.players_turn}] >> {active_player.name} {phase_name_enum}", True)
        phase['phase_function'](active_player, inactive_player)


mapConfig1 = BoardHandle(
    name="Map 1",
    wide=44,
    large=60,
    attacker_zone=[Point(0, 0), Point(17, 0), Point(17, 43), Point(0, 43)],     # Rectangle
    defender_zone=[Point(42, 0), Point(59, 0), Point(59, 43), Point(42, 43)],   # Rectangle
    objectives=[Objective(coord=(9, 21)), Objective(coord=(49, 21)), Objective(coord=(21, 9)),
                Objective(coord=(37, 9)), Objective(coord=(21, 33)), Objective(coord=(37, 33))]
)


if __name__ == '__main__':
    try:
        log("----- ----- ----- ----- ----- STARTING A NEW GAME ----- ----- ----- ----- -----")
        log("[>>] - Weeeelcome to WARHAMMER 40K BATTLE SIMULATOR!", True)
        board = Battlefield(mapConfig1)
        board.place_objectives()

        load_game_configuration()

        # Army selection: will assign
        p1, p2 = load_players_army("Shuan", "Guarrià")

        # Players Handshake: configuration of factions, here will be selected which factions will fight
        # choosing which one will be the attacker and which one will be the defender
        players_handshake(board, p1, p2)

        # Initiatives
        turn_list = initiatives(p1, p2)

        # Print Boards configuration
        board.display_board()

        # Place all the army in the board
        place_army_into_boardgame(turn_list)

        # If here all the Units have been displayed so the game can start!
        board.start_the_game()

        # Remove Attackers and defenders zone
        board.remove_attacker_defender_zone()

        board.display_board()

        print()
        for (game_turn, (attacker, defender)) in turn_list:
            log(f"\t{Fore.LIGHTYELLOW_EX}Game turn [{game_turn}]{Fore.RESET}", True)
            attacker.players_turn = game_turn
            defender.players_turn = game_turn

            # Execute Attacker phase
            execute_phase(attacker, defender)
            # Execute Defender phase
            execute_phase(defender, attacker)
            print()

    except KeyboardInterrupt:
        pass
