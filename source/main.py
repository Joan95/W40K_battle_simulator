import os.path
import random
from battlefield import Battlefield, BoardHandle, Objective
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


def load_players_army(random_player1=False, random_player2=False):
    global players_list

    players = list(players_cfg.keys())
    if random_player1:
        player_1 = None
        player = players[players.index('default')]
        while player == 'default':
            player = players[random.randint(0, len(players) - 1)]
            player_1 = Player(database, player, players_cfg[player])
    else:
        player = players[players.index('Shuan')]
        player_1 = Player(database, player, players_cfg[player],
                          database.get_faction_by_name(players_cfg[player]['faction'])[0][1])

    if random_player2:
        player_2 = None
        player = players[players.index('default')]
        while player == 'default':
            player = players[random.randint(0, len(players) - 1)]
            player_2 = Player(database, player, players_cfg[player])
    else:
        player = players[players.index('Warrià')]
        player_2 = Player(database, player, players_cfg[player],
                          database.get_faction_by_name(players_cfg[player]['faction'])[0][1])

    players_list.append(player_1)
    players_list.append(player_2)

    return player_1, player_2


def players_handshake(board_map, player_1, player_2):
    player_1.set_up_the_map(board_map)
    player_2.set_up_the_map(board_map)
    # Roll for set up the attacker and the defender
    print("[>>] - Rolling dices for setting up the attacker and the defender...")
    player_1.roll_players_dice()
    player_2.roll_players_dice()

    while player_1.last_roll_dice == player_2.last_roll_dice:
        print("[ *] - And it's been a DRAW! Re-rolling dices")
        player_1.roll_players_dice()
        player_2.roll_players_dice()

    if player_1.last_roll_dice > player_2.last_roll_dice:
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
    print("[>>] - Rolling dices for deciding initiatives...")
    player_1.roll_players_dice()
    player_2.roll_players_dice()

    while player_1.last_roll_dice == player_2.last_roll_dice:
        print("[ *] - And it's been a DRAW! Re-rolling dices")
        player_1.roll_players_dice()
        player_2.roll_players_dice()

    if player_1.last_roll_dice > player_2.last_roll_dice:
        print(f"\t{player_1.name} will go first!")
        players_turn = (player_1, player_2)
    else:
        print(f"\t{player_2.name} will go first!")
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
            player.deploy_unit()
        player_count += 1


def command_phase(active_player, inactive_player):
    # Calculate current army score
    active_player.army.calculate_danger_score()
    active_player.increment_command_points()
    inactive_player.army.calculate_danger_score()
    inactive_player.increment_command_points()

    for unit in active_player.army.units:
        if len(unit.models) < unit.unit_initial_force / 2:
            print(f"Unit {unit.name} at half of its initial force, will have to trow the dices for checking its moral")


def movement_phase(active_player, inactive_player):
    # Get enemy's alive units
    enemy_units = inactive_player.get_alive_units()
    # Force units to target enemies based on its score
    active_player.army.target_enemies(enemy_units)
    active_player.move_units()
    active_player.board_map.display_board()


def shooting_phase(active_player, inactive_player):
    pass


def charge_phase(active_player, inactive_player):
    pass


def fight_phase(active_player, inactive_player):
    pass


def execute_phase(active_player, inactive_player):
    for phase_sequence in phases:
        phase = phases[phase_sequence]
        phase_name_enum = GamePhase(phase_sequence).name.replace("_", " ").title()
        print(f"\t[{active_player.players_turn}] >> {active_player.name} {phase_name_enum}")
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
        print("[>>] - Weeeelcome to WARHAMMER 40K BATTLE SIMULATOR!")
        board = Battlefield(mapConfig1)
        board.place_objectives()

        load_game_configuration()

        # Army selection: will assign
        p1, p2 = load_players_army(random_player1=False, random_player2=False)

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
            print(f"\t{Fore.LIGHTYELLOW_EX}Game turn [{game_turn}]{Fore.RESET}")
            attacker.players_turn = game_turn
            defender.players_turn = game_turn

            # Execute Attacker phase
            execute_phase(attacker, defender)
            # Execute Defender phase
            execute_phase(defender, attacker)
            print()

    except KeyboardInterrupt:
        pass
