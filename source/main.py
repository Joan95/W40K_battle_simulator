import os.path
import random
from colorama import init, Fore
from players_army_configuration import players_army_configuration as players_cfg
from database_handler import DatabaseHandler
from player import Player
from player import ATTACKER, DEFENDER

init()

database = DatabaseHandler(os.path.join('..', 'database', 'database.db'))
players_list = list()
player_1 = None
player_2 = None
turn_list = list()
phases = dict()


def load_game_configuration():
    global phases
    local_phases = database.get_phases()
    for phase_name, phase_sequence in local_phases:
        phases[phase_sequence] = {'phase_name': phase_name, 'phase_function': None}

    phases[1]['phase_function'] = command_phase
    phases[2]['phase_function'] = movement_phase
    phases[3]['phase_function'] = shooting_phase
    phases[4]['phase_function'] = charge_phase
    phases[5]['phase_function'] = fight_phase


def army_players_configuration(random_player1=False, random_player2=False):
    global player_1, player_2, players_list

    players = list(players_cfg.keys())
    if random_player1:
        player = players[players.index('default')]
        while player == 'default':
            player = players[random.randint(0, len(players) - 1)]
            player_1 = Player(database, player, players_cfg[player])
    else:
        player = players[players.index('Warrià')]
        player_1 = Player(database, player, players_cfg[player],
                          database.get_faction_by_name(players_cfg[player]['faction'])[0][1])

    if random_player2:
        player = players[players.index('default')]
        while player == 'default':
            player = players[random.randint(0, len(players) - 1)]
            player_2 = Player(database, player, players_cfg[player])
    else:
        player = players[players.index('Shuan')]
        player_2 = Player(database, player, players_cfg[player],
                          database.get_faction_by_name(players_cfg[player]['faction'])[0][1])

    players_list.append(player_1)
    players_list.append(player_2)


def players_handshake():
    global turn_list

    # Roll for set up the attacker and the defender
    print("Rolling dices for setting up the attacker and the defender...")
    player_1.roll_players_dice()
    player_2.roll_players_dice()

    while player_1.last_roll_dice == player_2.last_roll_dice:
        print("\tAnd it's been a DRAW! Re-rolling dices")
        player_1.roll_players_dice()
        player_2.roll_players_dice()

    if player_1.last_roll_dice > player_2.last_roll_dice:
        player_1.set_roll(ATTACKER)
        player_2.set_roll(DEFENDER)
        players_turn = (player_1, player_2)
    else:
        player_1.set_roll(DEFENDER)
        player_2.set_roll(ATTACKER)
        players_turn = (player_2, player_1)

    for x in range(1, 6):
        turn_list.append([x, players_turn])


def command_phase():
    for player in players_list:
        player.increment_command_points()


def movement_phase():
    pass


def shooting_phase():
    pass


def charge_phase():
    pass


def fight_phase():
    pass


def execute_phase(player):
    for phase_sequence in phases:
        phase = phases[phase_sequence]
        print(f"\t[{player.players_turn}] >> {player.name} {phase['phase_name']}")
        phase['phase_function']()


if __name__ == '__main__':
    try:
        print("Weeeelcome to WARHAMMER 40K BATTLE SIMULATOR!")

        load_game_configuration()

        # Army selection: will assign
        army_players_configuration(random_player1=False, random_player2=False)

        # Players Handshake: configuration of factions, here will be selected which factions will fight
        # choosing which one will be the attacker and which one will be the defender
        players_handshake()

        print()
        for (game_turn, (attacker, defender)) in turn_list:
            print(f"\t{Fore.LIGHTYELLOW_EX}Game turn [{game_turn}]{Fore.RESET}")
            attacker.players_turn = game_turn
            defender.players_turn = game_turn

            # Execute Attacker phase
            execute_phase(attacker)
            # Execute Defender phase
            execute_phase(defender)
            print()

    except KeyboardInterrupt:
        pass
