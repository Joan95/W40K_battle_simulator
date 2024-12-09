import random
from army import Army
from colorama import Fore
from enums import PlayerRol
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
        self.last_roll_dice = None
        self.command_points = 0
        self.players_turn = 0

        self.set_faction(army_cfg.get('faction'))
        self.set_detachment(army_cfg.get('detachment'))
        self.load_army(army_cfg.get('army'))
        self.make_announcement()

    def deploy_unit(self):
        """Deploy a unit into the player's zone."""
        unit_to_place = self.army.get_unit_to_place()
        if unit_to_place:
            log(f"{self.name} is placing unit {unit_to_place.name}")
            unit_to_place.deploy_unit_in_zone(self.battlefield, self.deployment_zone)
        else:
            log(f"{self.name} has no units left to deploy!")

    def get_alive_units(self):
        """Return a list of alive units."""
        return [unit for unit in self.army.units if not unit.is_destroyed]

    def has_units_to_deploy(self):
        """Check if there are units left to deploy."""
        return self.army.are_there_units_still_to_be_deployed()

    def increment_command_points(self):
        """Increase command points and notify the player."""
        self.command_points += 1
        log(f"{self.name} has gained a command point, total: {self.command_points}", True)

    def load_army(self, army_cfg):
        """Load the player's army based on the provided configuration."""
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
            for _ in range(amount):
                models_list.append(self.load_model(models_cfg['name'], model_attributes, models_cfg['weapons'], is_warlord))
            return models_list
        except IndexError:
            log(f"Model {models_cfg['name']} not found in the database!")
            raise IndexError

    def load_model(self, model_name, model_attributes, model_weapons_cfg, is_warlord=False):
        """Load a single model with its attributes and weapons."""
        weapon_list = []
        for weapon_type, weapon_list_cfg in model_weapons_cfg.items():
            for weapon_name in weapon_list_cfg:
                try:
                    weapon_cls = MeleeWeapon if weapon_type == "melee" else RangedWeapon
                    weapon_data = self.database.get_melee_weapon_by_name(
                        weapon_name, self.database.get_model_id_by_name(model_name)[0][0]
                    )[0] if weapon_type == "melee" else self.database.get_ranged_weapon_by_name(
                        weapon_name, self.database.get_model_id_by_name(model_name)[0][0]
                    )[0]
                    weapon_list.append(weapon_cls(weapon_name, weapon_data))
                except IndexError:
                    log(f"Weapon {weapon_name} not found in the database!")
                    raise IndexError
        model_keywords = self.database.get_model_keywords(model_name)
        return Model(model_name, model_attributes, weapon_list, model_keywords, is_warlord)

    def load_unit(self, unit_cfg):
        """Load a unit and its models."""
        models_list = [model for models_cfg in unit_cfg.get('models', []) for model in self.load_models(models_cfg)]
        if models_list:
            tmp_unit = Unit(unit_cfg['unit_name'], models_list)
            self.army.add_unit_into_army(tmp_unit)

    def make_announcement(self):
        """Announce the player's faction and detachment."""
        log(f"{self.name} will play with {self.faction} '{self.detachment}'")
        log(f"Units: {', '.join(unit.name for unit in self.army.units)}")

    def move_units(self):
        """Move units towards their targets."""
        for unit in self.get_alive_units():
            log(f"Moving {unit.name}")
            unit.move_towards_target(self.battlefield)

    def roll_players_dice(self, sides=6, show_throw=True):
        """Roll a dice and display the result."""
        self.last_roll_dice = random.randint(1, sides)
        if show_throw:
            adjective = random.choice(six_roll_dice_adjectives).upper() + " " if self.last_roll_dice == 6 else ""
            log(f"{self.name} rolled a {adjective}{self.user_color}{self.last_roll_dice}{Fore.RESET}", show_throw)
        return self.last_roll_dice

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
