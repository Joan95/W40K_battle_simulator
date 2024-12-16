import random
from army import Army
from battlefield import get_distance_between_two_points
from colorama import Fore
from dice import Dices
from enums import PlayerRol, WeaponType
from logging_handler import *
from model import Model
from source.enums import AttackStrength
from unit import Unit
from weapon import MeleeWeapon, RangedWeapon

# Constants for bold text
bold_on = "\033[1m"
bold_off = "\033[0m"

# List of adjectives for a six-roll dice
six_roll_dice_adjectives = [
    'Wonderful', 'Marvelous', 'Spectacular', 'Stunning', 'Glorious', 'Magnificent', 'Exquisite', 'Enchanting',
    'Dazzling', 'Breathtaking', 'Fabulous', 'Remarkable', 'Astounding', 'Astonishing', 'Phenomenal', 'Superb'
]

# List of available colors
colors_list = [Fore.RED, Fore.LIGHTRED_EX, Fore.GREEN, Fore.LIGHTGREEN_EX, Fore.YELLOW,
               Fore.BLUE, Fore.LIGHTBLUE_EX, Fore.MAGENTA, Fore.LIGHTMAGENTA_EX, Fore.CYAN,
               Fore.LIGHTCYAN_EX, Fore.LIGHTWHITE_EX]


def set_color(color_name):
    """Set faction color based on the name."""
    color_mapping = {
        "Red": Fore.RED,
        "Green": Fore.GREEN
    }
    return color_mapping.get(color_name, Fore.RESET)


class Player:
    def __init__(self, database, name=None, army_cfg=None, faction_color=None):
        self.army_cfg = army_cfg
        self.army = Army()
        self.battlefield = None
        self.command_points = 0
        self.deployment_zone = None
        self.database = database
        self.detachment = None
        self.dices = Dices(name)
        self.faction = None
        self.factions_color = set_color(faction_color)
        self.players_turn = 0
        self.rol = None
        self.user_color = random.choice(colors_list)
        self.name = f"{self.user_color}{bold_on}{name}{bold_off}{Fore.RESET}"

        self.set_faction(army_cfg.get('faction'))
        self.set_detachment(army_cfg.get('detachment'))
        self.load_army(army_cfg.get('army'))
        self.make_announcement()

    def allocate_damages(self, damages_list):
        log(f'[PLAYER {self.name}] is allocating the damages {damages_list} received in last attack')
        pass

    def get_available_units_for_shooting(self):
        units_available_for_shooting = self.army.get_units_available_for_shooting()
        log(f'[PLAYER {self.name}] units available (alive and not engaged) for shooting are: '
            f'{", ".join([unit.name for unit in units_available_for_shooting])}')
        return units_available_for_shooting

    def get_model_salvation(self, model_attacked, weapon_armour_penetration):
        raw_salvation = model_attacked.get_model_salvation()
        salvation = raw_salvation - weapon_armour_penetration
        invulnerable_save = model_attacked.get_invulnerable_save()

        if raw_salvation > 6 and invulnerable_save:
            log(f'[PLAYER {self.name}] reports that [{model_attacked.name}] will save at it\'s '
                f'invulnerable save of {invulnerable_save} instead of having to save at {salvation} '
                f'(SV {raw_salvation}+  AP {weapon_armour_penetration})')
            return invulnerable_save

        if invulnerable_save < salvation:
            log(f'[PLAYER {self.name}] reports that [{model_attacked.name}] will save at it\'s '
                f'invulnerable save of {invulnerable_save} instead of having to save at {salvation} '
                f'(SV {raw_salvation}+  AP {weapon_armour_penetration})')
            return invulnerable_save
        else:
            log(f'[PLAYER {self.name}] reports that [{model_attacked.name}] will save at it\'s '
                f'own salvation of {salvation} (SV {raw_salvation}+  AP {weapon_armour_penetration})')
            return salvation

    def deploy_units(self):
        """Deploy a unit into the player's zone."""
        log(f"[PLAYER {self.name}] is deploying a unit")
        self.army.deploy_unit(self.battlefield, self.deployment_zone)

    def get_first_model_to_die_from_unit(self, unit):
        model_to_be_shot = unit.get_first_model_to_die()
        log(f'[PLAYER {self.name}] Sets [{model_to_be_shot.name}] from [{unit.name}] as first model to '
            f'receive the shots')
        return model_to_be_shot

    def get_last_rolled_dice_values(self):
        return self.dices.last_roll_dice_values

    def get_units_alive(self):
        """Return a list of alive units."""
        return self.army.get_units_alive()

    def has_units_to_deploy(self):
        """Check if there are units left to deploy."""
        return self.army.are_there_units_still_to_be_deployed()

    def increment_command_points(self):
        """Increase command points and notify the player."""
        self.command_points += 1
        log(f"[PLAYER {self.name}] has gained a command point, total: {self.command_points}", True)

    def load_army(self, army_cfg):
        """Load the player's army based on the provided configuration."""
        log(f'Loading army from player {self.name}')
        if not army_cfg:
            log(f"[PLAYER {self.name}] has no army configuration provided.")
            return
        for unit in army_cfg.get('units', []):
            self.load_unit(unit)
        log(f"[PLAYER {self.name}]'s army has been loaded!")

    def load_models(self, models_cfg):
        """Load models for a unit."""
        is_warlord = 'warlord' in models_cfg
        amount = models_cfg.get('amount', 1)
        more_than_one = False
        if amount > 1:
            more_than_one = True
        models_list = []
        try:
            model_attributes = self.database.get_model_by_name(models_cfg['name'])[0]
        except IndexError:
            log(f'[PLAYER {self.name}] Model [{models_cfg["name"]}] has not been found in Data Base')
            raise IndexError
        for _ in range(amount):
            models_list.append(self.load_model(models_cfg['name'], model_attributes, models_cfg['weapons'],
                                               is_warlord, more_than_one))
        return models_list

    def load_model(self, model_name, model_attributes, model_weapons_cfg, is_warlord=False, more_than_one=False):
        """Load a single model with its attributes and weapons."""
        model_id = self.database.get_model_id_by_name(model_name)[0][0]
        weapon_list = self.load_weapons(model_name, model_id, model_weapons_cfg)
        model_keywords = self.database.get_model_keywords(model_name)
        return Model(model_name, model_attributes, weapon_list, model_keywords, is_warlord, more_than_one)

    def load_unit(self, unit_cfg):
        """Load a unit and its models."""
        models_list = [model for models_cfg in unit_cfg.get('models', []) for model in self.load_models(models_cfg)]
        if models_list:
            tmp_unit = Unit(unit_cfg['unit_name'], models_list)
            self.army.add_unit_into_army(tmp_unit)

    def load_weapons(self, model_name, model_id, model_weapons_cfg):
        weapon_list = []
        for weapon_type, weapon_list_cfg in model_weapons_cfg.items():
            for weapon_name in weapon_list_cfg:
                weapon_abilities = None
                if weapon_type == WeaponType.MELEE.name:
                    weapon_cls = MeleeWeapon
                    weapon_data = self.database.get_melee_weapon_by_name(weapon_name, model_id)[0]
                    try:
                        weapon_abilities = self.database.get_weapon_abilities(model_name, weapon_name,
                                                                              WeaponType.MELEE)
                    except IndexError:
                        log(f'[PLAYER {self.name}] Weapon {weapon_name} has no abilities')
                else:
                    weapon_cls = RangedWeapon
                    weapon_data = self.database.get_ranged_weapon_by_name(weapon_name, model_id)[0]
                    weapon_abilities = self.database.get_weapon_abilities(model_name, weapon_name, WeaponType.RANGED)
                weapon_list.append(weapon_cls(weapon_name, weapon_data, weapon_abilities))
        return weapon_list

    def make_announcement(self):
        """Announce the player's faction and detachment."""
        log(f"[PLAYER {self.name}] will play with {self.faction} '{self.detachment}'")
        log(f"Units: {', '.join(unit.name for unit in self.army.units)}")

    def move_units(self):
        """Move units towards their targets."""
        for unit in self.get_units_alive():
            log(f"[PLAYER {self.name}] Moving {unit.name}")
            unit.move_towards_target(self.battlefield)

    def roll_players_dice(self, number_of_dices=1, sides=6, show_throw=True):
        """Roll a dice and display the result."""
        self.dices.roll_dices(number_of_dices=number_of_dices, sides=sides)

        if show_throw:
            log_text = f'[PLAYER {self.name}] rolled #{self.dices.last_roll_dice_count} dice(s) getting a: '

            for dice in self.dices.last_roll_dice_values:
                adjective = random.choice(six_roll_dice_adjectives).upper() + " " if dice == 6 else ""
                log_text += f"{adjective}{self.user_color}{dice}{Fore.RESET}"
            log(log_text, show_throw)
        return self.dices.last_roll_dice_values

    def set_battlefield(self, board_map):
        """Set the player's board map."""
        self.battlefield = board_map

    def set_deployment_zone(self, zone):
        """Set the player's deployment zone."""
        self.deployment_zone = zone

    def set_detachment(self, detachment):
        """Set the player's detachment."""
        self.detachment = f"{bold_on}{self.factions_color}{detachment}{Fore.RESET}{bold_off}"

    def set_faction(self, faction_cfg):
        """Set the player's faction."""
        self.faction = f"{bold_on}{self.factions_color}{faction_cfg}{Fore.RESET}{bold_off}"

    def set_rol(self, rol):
        """Set the player's role (attacker or defender)."""
        role_colors = {
            PlayerRol.ATTACKER.value: Fore.RED,
            PlayerRol.DEFENDER.value: Fore.BLUE,
        }
        role_color = role_colors.get(rol, Fore.RESET)
        role_name = "ATTACKER" if rol == PlayerRol.ATTACKER.value else "DEFENDER"
        log(f"[PLAYER {self.name}] will be the {role_color}{role_name}{Fore.RESET}", True)
        self.rol = rol

    def set_target_for_model(self, model, enemy_units_list):
        at_least_one_shot_is_available = False

        # Clean current target unit for that model
        model.current_target_unit = None

        target_candidates = list()
        # Find the most appropriate enemy unit to target based on proximity and weakness
        for enemy_unit in enemy_units_list:
            target_candidates.extend([
                (enemy_unit, enemy_model, get_distance_between_models(model, enemy_model), enemy_unit.unit_total_score) for
                enemy_model in enemy_unit.get_models_alive()
            ])

        if target_candidates:
            # Optionally adjust the sorting criteria or add weights
            target_candidates.sort(key=lambda x: (x[2], x[3]))

        # Let's see if target unit is reachable, otherwise we might want to allocate the shoots to another unit
        for weapon in model.get_model_weapons_ranged():
            for enemy_unit, enemy_model, distance_to_enemy, enemy_unit_total_score in target_candidates:
                if weapon.get_weapon_range_attack() >= distance_to_enemy:
                    at_least_one_shot_is_available = True
                    model.current_target_unit = enemy_unit
                    # The main enemy unit is reachable!
                    log(f'[PLAYER {self.name}] declares:\n\t\t>> {model.name} [{model.position}] '
                        f'will shoot {weapon.name} [{weapon.range_attack}]. '
                        f'Target unit [{model.current_target_unit.name}]. '
                        f'Model seen [{enemy_model.name}] at [{enemy_model.position}]. '
                        f'Distance to target {distance_to_enemy}"')
                    break
        return at_least_one_shot_is_available

    def set_target_for_unit(self, unit, enemy_units_list):
        log(f'[PLAYER {self.name}] setting targets for unit {unit.name}')
        unit_has_a_shot = False
        for model in unit.get_unit_models_available_for_shooting():
            if self.set_target_for_model(model, enemy_units_list):
                unit_has_a_shot = True
        if not unit_has_a_shot:
            log(f'[PLAYER {self.name}] [{unit.name}] will not shoot since it does not see anything')
        return unit_has_a_shot

    def shoot_ranged_attacks(self):
        killed_models = list()
        if shots:
            log(f'[PLAYER {self.name}] --- --- --- SHOOTING! --- --- ---')
            for unit_shooting in shots:
                weapon = shots[unit_shooting]['weapon']
                attacker = shots[unit_shooting]['attacker']
                for target in shots[unit_shooting]['targets']:
                    log(f'[PLAYER {self.name}] [{attacker.name}] shooting [#{target["count"]}] {weapon.name} to '
                        f'{target["unit"].name}')
                    log(f'[PLAYER {self.name}] Weapon attacks {weapon.num_attacks}')
                    # Get weapon number of attacks to do
                    weapon_num_attacks, weapon_strength = weapon.get_num_attacks(self.dices)
                    # Retrieve the enemy who will suffer this attack
                    enemy_model_to_attack = inactive_player.get_first_model_to_die_from_unit(target['unit'])
                    enemy_toughness = enemy_model_to_attack.get_model_toughness()

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

                    log(f'[PLAYER {self.name}] [{attacker.name}] attack will success at {weapon_attack_strength}\'s')
                    self.dices.roll_dices(number_of_dices='{}D6'.format(weapon_num_attacks))
                    attacks = self.dices.last_roll_dice_values
                    successful_attacks = list()
                    for count, attack in enumerate(attacks, start=1):
                        if attack >= weapon_attack_strength:
                            successful_attacks.append(attack)

                    if successful_attacks:
                        log(f'[PLAYER {self.name}] And there\'s a total of #{len(successful_attacks)} successful '
                            f'attack(s) from {attacks}')

                        hits = list()
                        enemy_salvation = inactive_player.get_model_salvation(enemy_model_to_attack,
                                                                              weapon.armour_penetration)
                        for count in range(len(successful_attacks)):
                            if inactive_player.dices.roll_dices() < enemy_salvation:
                                hits.append(inactive_player.dices.last_roll_dice_value)
                        if hits:
                            log(f'[PLAYER {self.name}] It\'s been #{len(hits)} successful hits(s)')
                            damages = list()
                            for _ in hits:
                                damages.append(weapon.get_damage(self.dices))
                            log(f'Attack damages are {damages}')
                            killed_models = inactive_player.allocate_damages(damages)
                        else:
                            log(f'[PLAYER {self.name}] Attack has been fully defended by [{enemy_model_to_attack}]')
                    else:
                        log(f'[PLAYER {self.name}] Attack entire attack fails {attacks}... [F]')

            return killed_models
        else:
            log(f'[PLAYER {self.name}] army has not been able to target any enemy this turn')


def get_distance_between_models(model1, model2):
    pos1 = model1.position
    pos2 = model2.position
    if pos1 and pos2:
        return ((pos1.x - pos2.x) ** 2 + (pos1.y - pos2.y) ** 2) ** 0.5
    return float('inf')
