import os.path
from battlefield import Battlefield, BoardHandle, Objective
from colorama import init
from database_handler import DatabaseHandler
from enums import PlayerRol
from game_handler import GameHandler
from logging_handler import log
from players_army_configuration import players_army_configuration as players_cfg
from player import Player
from shapely.geometry import Point

init()

database = DatabaseHandler(os.path.join('..', 'database', 'database.db'))
players_list = list()
game_handler = None


def load_players_army(player_1_name, player_2_name):
    global players_list

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
    log("[REPORT][ATTACKER_DEFENDER] Setting up the ATTACKER and the DEFENDER ----- ----- ----- ----- -----")
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
        players_turn = (player_1, player_2)
    else:
        player_1.set_rol(PlayerRol.DEFENDER.value)
        player_1.set_deployment_zone(board_map.map_configuration.defender_zone)
        player_2.set_rol(PlayerRol.ATTACKER.value)
        player_2.set_deployment_zone(board_map.map_configuration.attacker_zone)
        players_turn = (player_2, player_1)

    turns = list()
    for x in range(1, 6):
        turns.append([x, players_turn])
    return turns


def initiatives(player_1, player_2):
    log("[REPORT][INITIATIVES] Deciding INITIATIVES for each PLAYER ----- ----- ----- ----- -----")
    player_1.roll_players_dice(number_of_dices=1, sides=6)
    player_2.roll_players_dice(number_of_dices=1, sides=6)

    while player_1.get_last_rolled_dice_values()[0] == player_2.get_last_rolled_dice_values()[0]:
        log("[ *] - And it's been a DRAW! Re-rolling dices")
        player_1.roll_players_dice()
        player_2.roll_players_dice()

    if player_1.get_last_rolled_dice_values()[0] > player_2.get_last_rolled_dice_values()[0]:
        log(f"[REPORT] {player_1.name} will go first!", True)
        players_turn = (player_1, player_2)
    else:
        log(f"[REPORT] {player_2.name} will go first!", True)
        players_turn = (player_2, player_1)

    turns = list()
    for x in range(1, 6):
        turns.append([x, players_turn])
    return turns


def place_army_into_boardgame(turns):
    log("[REPORT][DEPLOYMENT] Deploying ARMY into the BATTLEFIELD ----- ----- ----- ----- -----")
    player_count = 0
    players = turns[0][1]
    while players[0].has_units_to_deploy() or players[1].has_units_to_deploy():
        player = players[player_count % len(players)]
        if player.has_units_to_deploy():
            unit = player.get_unit_to_deploy()
            zone_to_deploy = player.get_deployment_zone()
            board.deploy_unit(zone_to_deploy, unit)
            unit.unit_deployed()
        player_count += 1


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
        # Army selection: will assign
        p1, p2 = load_players_army("Shuan", "Guarrià")
        # Players Handshake: configuration of factions, here will be selected which factions will fight
        # choosing which one will be the attacker and which one will be the defender
        turn_list = players_handshake(board, p1, p2)
        # Place all the army in the board
        place_army_into_boardgame(turn_list)
        # Print Boards configuration
        board.display_board()
        # Initiatives
        turn_list = initiatives(p1, p2)
        game_handler = GameHandler(turn_list, board)
        game_handler.run_game()
        board.display_board()
    except KeyboardInterrupt:
        pass
