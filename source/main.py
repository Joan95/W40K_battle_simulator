import os.path
from battlefield import Battlefield, BoardHandle, Objective
from logging_handler import *
from shapely.geometry import Point
from colorama import init, Fore
from enums import GamePhase, PlayerRol
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

    player = players[players.index(player_1_name)]
    player_1 = Player(database, player, players_cfg[player],
                      database.get_faction_by_name(players_cfg[player]['faction'])[0][1])

    player = players[players.index(player_2_name)]
    player_2 = Player(database, player, players_cfg[player],
                      database.get_faction_by_name(players_cfg[player]['faction'])[0][1])

    players_list.append(player_1)
    players_list.append(player_2)

    return player_1, player_2


def players_handshake(board_map, player_1, player_2):
    player_1.set_battlefield(board_map)
    player_2.set_battlefield(board_map)
    # Roll for set up the attacker and the defender
    log("[>>] - Setting up the attacker and the defender")
    player_1.roll_players_dice(number_of_dices=1, sides=6)
    player_2.roll_players_dice(number_of_dices=1, sides=6)

    while player_1.last_roll_dice_values[0] == player_2.last_roll_dice_values[0]:
        log("[ *] - And it's been a DRAW! Re-rolling dices")
        player_1.roll_players_dice()
        player_2.roll_players_dice()

    if player_1.last_roll_dice_values[0] > player_2.last_roll_dice_values[0]:
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

    while player_1.last_roll_dice_values[0] == player_2.last_roll_dice_values[0]:
        log("[ *] - And it's been a DRAW! Re-rolling dices")
        player_1.roll_players_dice()
        player_2.roll_players_dice()

    if player_1.last_roll_dice_values[0] > player_2.last_roll_dice_values[0]:
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
    # Force units to target enemies based on its score
    active_player.army.target_enemies(enemy_units)
    active_player.move_units()
    active_player.battlefield.display_board()


def shooting_phase(active_player, inactive_player):
    enemy_units = inactive_player.get_units_alive()
    active_player.allocate_players_ranged_attacks(enemy_units)

    # Once attacks have been allocated shot everything


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
        p1, p2 = load_players_army("Shuan", "Warrià")

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
