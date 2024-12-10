import random
from army import Army
from battlefield import get_distance_between_two_points
from colorama import Fore
from enums import PlayerRol, WeaponType
from logging_handler import *
from model import Model
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
        self.database = database
        self.battlefield = None
        self.user_color = random.choice(colors_list)
        self.factions_color = set_color(faction_color)
        self.name = f"{self.user_color}{bold_on}{name}{bold_off}{Fore.RESET}"
        self.army_cfg = army_cfg
        self.army = Army()
        self.faction = None
        self.detachment = None
        self.rol = None
        self.deployment_zone = None
        self.last_roll_number_of_dices = 0
        self.last_roll_dice_values = 0
        self.command_points = 0
        self.players_turn = 0

        self.set_faction(army_cfg.get('faction'))
        self.set_detachment(army_cfg.get('detachment'))
        self.load_army(army_cfg.get('army'))
        self.make_announcement()

    def allocate_players_ranged_attacks(self, enemy_units):
        log(f'{self.name} allocating ranged attacks for all the army')
        # Firs of all get all the allocatable ranged attacks from our army
        allocatable_ranged_attacks = self.army.get_allocatable_army_ranged_attacks()
        # For each allocatable ranged attack perform by unit we need to check whether it can be placed to
        # unit's targeted enemy, otherwise we might want to change the target for that concrete attack in order to
        # not lose the range attack for that current phase

        for unit in allocatable_ranged_attacks:
            for model in allocatable_ranged_attacks[unit]:
                for weapon in allocatable_ranged_attacks[unit][model]:
                    if not allocatable_ranged_attacks[unit][model][weapon]['enemy_to_shot']:
                        # There is no target, let's see if we reach our main target
                        for enemy_model in unit.targeted_enemy_unit_to_chase.get_models_alive():
                            distance_to_enemy = get_distance_between_two_points(model.position, enemy_model.position)
                            if weapon.get_weapon_range_attack() >= distance_to_enemy:
                                # The enemy is reachable!
                                allocatable_ranged_attacks[unit][model][weapon]['enemy_to_shot'] = \
                                    unit.targeted_enemy_unit_to_chase
                                log(f'Enemy reachable! '
                                    f'Model {model.name} [{model.position}] can shoot {weapon.name} '
                                    f'[{weapon.range_attack}] to enemy {enemy_model.name} [{enemy_model.position}]. '
                                    f'Distance to enemy {distance_to_enemy}"')
                                break
                        pass

    def deploy_units(self):
        """Deploy a unit into the player's zone."""
        log(f"{self.name} is deploying a unit")
        self.army.deploy_unit(self.battlefield, self.deployment_zone)

    def get_units_alive(self):
        """Return a list of alive units."""
        return self.army.get_units_alive()

    def has_units_to_deploy(self):
        """Check if there are units left to deploy."""
        return self.army.are_there_units_still_to_be_deployed()

    def increment_command_points(self):
        """Increase command points and notify the player."""
        self.command_points += 1
        log(f"{self.name} has gained a command point, total: {self.command_points}", True)

    def load_army(self, army_cfg):
        """Load the player's army based on the provided configuration."""
        log(f'Loading army from player {self.name}')
        if not army_cfg:
            log(f"{self.name} has no army configuration provided.")
            return
        for unit in army_cfg.get('units', []):
            self.load_unit(unit)
        log(f"{self.name}'s army has been loaded!")

    def load_models(self, models_cfg):
        """Load models for a unit."""
        is_warlord = 'warlord' in models_cfg
        amount = models_cfg.get('amount', 1)
        models_list = []
        try:
            model_attributes = self.database.get_model_by_name(models_cfg['name'])[0]
        except IndexError:
            log(f'Model [{models_cfg["name"]}] has not been found in Data Base')
            raise IndexError
        for _ in range(amount):
            models_list.append(self.load_model(models_cfg['name'], model_attributes, models_cfg['weapons'],
                                               is_warlord))
        return models_list

    def load_model(self, model_name, model_attributes, model_weapons_cfg, is_warlord=False):
        """Load a single model with its attributes and weapons."""
        model_id = self.database.get_model_id_by_name(model_name)[0][0]
        weapon_list = self.load_weapons(model_name, model_id, model_weapons_cfg)
        model_keywords = self.database.get_model_keywords(model_name)
        return Model(model_name, model_attributes, weapon_list, model_keywords, is_warlord)

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
                        log(f'Weapon {weapon_name} has no abilities')
                else:
                    weapon_cls = RangedWeapon
                    weapon_data = self.database.get_ranged_weapon_by_name(weapon_name, model_id)[0]
                    weapon_abilities = self.database.get_weapon_abilities(model_name, weapon_name, WeaponType.RANGED)
                weapon_list.append(weapon_cls(weapon_name, weapon_data, weapon_abilities))
        return weapon_list

    def make_announcement(self):
        """Announce the player's faction and detachment."""
        log(f"{self.name} will play with {self.faction} '{self.detachment}'")
        log(f"Units: {', '.join(unit.name for unit in self.army.units)}")

    def move_units(self):
        """Move units towards their targets."""
        for unit in self.get_units_alive():
            log(f"Moving {unit.name}")
            unit.move_towards_target(self.battlefield)

    def roll_players_dice(self, number_of_dices=1, sides=6, show_throw=True):
        """Roll a dice and display the result."""
        self.last_roll_number_of_dices = number_of_dices
        self.last_roll_dice_values = list()
        for _ in range(self.last_roll_number_of_dices):
            self.last_roll_dice_values.append(random.randint(1, sides))

        if show_throw:
            log_text = f'{self.name} rolled #{self.last_roll_number_of_dices} dice(s) getting: '

            for dice in self.last_roll_dice_values:
                adjective = random.choice(six_roll_dice_adjectives).upper() + " " if dice == 6 else ""
                log_text += f"{adjective}{self.user_color}{dice}{Fore.RESET}"
            log(log_text, show_throw)
        return self.last_roll_dice_values

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
        log(f"{self.name} will be the {role_color}{role_name}{Fore.RESET}", True)
        self.rol = rol
