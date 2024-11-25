import os.path

from database_handler import DatabaseHandler
from player import Player
from player import ATTACKER, DEFENDER

database = DatabaseHandler(os.path.join('..', 'database', 'database.db'))
player_1 = Player("Warrià")
player_2 = Player("Shuan")

turn_list = list()


def choose_players_faction(player_obj, rand=False):
    print(f"\t{player_obj.name} is choosing a faction... ")
    factions = database.get_factions()

    if rand:
        player_obj.set_faction(database.get_faction((player_obj.roll_players_dice() % len(factions)) + 1)[0][0])
    else:
        for (faction_id, faction) in factions:
            print(f"\t>> {faction}")
        pass


def handshake():
    choose_players_faction(player_1, True)
    choose_players_faction(player_2, True)

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
        turn_list.append((player_1, player_2))
    else:
        player_1.set_roll(DEFENDER)
        player_2.set_roll(ATTACKER)
        turn_list.append((player_2, player_1))


if __name__ == '__main__':
    print("Weeeelcome to WARHAMMER 40K BATTLE SIMULATOR!")
    # Handshake: configuration of factions, here will be selected which factions will fight
    # choosing which one will be the attacker and which one will be the defender
    handshake()
    pass
