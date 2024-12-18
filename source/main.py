import os.path
from battlefield import Battlefield, BoardHandle, Objective
from colorama import init
from database_handler import DatabaseHandler
from enums import AttackStrength, PlayerRol
from game_handler import GameHandler
from logging_handler import *
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
    log("[REPORT]\n\t\t----- ----- ----- ----- ----- Setting up the ATTACKER and the DEFENDER "
        "----- ----- ----- ----- -----")
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
    log("[REPORT]\n\t\t----- ----- ----- ----- ----- Deciding INITIATIVES for each PLAYER "
        "----- ----- ----- ----- -----")
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
    log("[REPORT]\n\t\t----- ----- ----- ----- ----- Deploying ARMY into the BATTLEFIELD "
        "----- ----- ----- ----- -----")
    player_count = 0
    players = turns[0][1]
    while players[0].has_units_to_deploy() or players[1].has_units_to_deploy():
        player = players[player_count % len(players)]
        if player.has_units_to_deploy():
            player.deploy_units()
        player_count += 1


def resolve_impact_roll(active_player, weapon, num_shoots):
    log(f'\t\t----- ----- ----- IMPACT ROLL(s) ----- ----- -----')

    # Get weapon number of attacks to do
    log(f'[PLAYER {active_player.name}] there are #{num_shoots} [{weapon.name}] being shoot')
    weapon_num_attacks, weapon_ballistic_skill = weapon.get_num_attacks(active_player.dices)
    total_attacks = num_shoots * weapon_num_attacks

    log(f'[PLAYER {active_player.name}] [{weapon.name}] #{total_attacks} attack(s) will success at '
        f'{weapon_ballistic_skill}\'s')
    active_player.dices.roll_dices(number_of_dices='{}D6'.format(total_attacks))
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
    log(f'\t\t----- ----- ----- WOUND ROLL(s) ----- ----- -----')
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
    log(f'\t\t----- ----- ----- ASSIGNING ATTACKS ----- ----- -----')
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
    log(f'\t\t----- ----- ----- ALLOCATING DAMAGE ----- ----- -----')
    damage = weapon.get_damage(active_player.dices)
    return inactive_player.allocate_damage(enemy_model, damage)


def resolve_player_attack(active_player, inactive_player, attack_dict):
    killed_models = list()
    model = attack_dict['attacker']
    weapon = attack_dict['weapon']
    num_shoots = attack_dict['count']
    enemy_target = attack_dict["target"]

    num_shoots_increment = weapon.handle_weapon_abilities(model, enemy_target)

    log(f'[PLAYER {active_player.name}] resolving #{num_shoots} impact roll(s) made by '
        f'[{model.name}] with [{weapon.name}]'
        f'[{", ".join([ability.name[0] for ability in weapon.get_abilities()])}] against unit '
        f'[{enemy_target.raw_name}]')

    # 1 - Impact Roll
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
