import random
from army import Army
from colorama import Fore
from dice import Dices
from enums import PlayerRol, WeaponType
from logging_handler import log
from model import Model
from unit import Unit
from weapon import MeleeWeapon, RangedWeapon

# Constants for bold text
BOLD_ON = "\033[1m"
BOLD_OFF = "\033[0m"

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
        self.deployment_zone = None
        self.database = database
        self.detachment = None
        self.dices = Dices(name)
        self.faction = None
        self.factions_color = set_color(faction_color)
        self.rol = None
        self.user_color = random.choice(colors_list)
        self.raw_name = name
        self.name = f"{self.user_color}{BOLD_ON}{self.raw_name}{BOLD_OFF}{Fore.RESET}"

        """
            1 - COMMAND PHASE
        """
        self.command_points = 0
        """
            2 - MOVEMENT PHASE
        """
        """
            3 - SHOOTING PHASE
        """
        self.units_selection_list = None
        self.unit_idx = 0
        self.selected_unit = None

        self.set_faction(army_cfg.get('faction'))
        self.set_detachment(army_cfg.get('detachment'))
        self.load_army(army_cfg.get('army'))
        self.make_announcement()

    def allocate_damage(self, model, damage):
        log(f'\t[PLAYER {self.name}] is allocating {damage} wound(s) to {model.name}')
        if model.has_feel_no_pain():
            damage = model.do_feel_no_pain(self.dices, damage)

        return model.receive_damage(damage)

    def are_more_units_to_be_selected(self):
        if self.units_selection_list and self.unit_idx < len(self.units_selection_list):
            log(f'\t[PLAYER {self.name}] there are still units left to be selected')
            return True
        log(f'\t[PLAYER {self.name}] no more units left to be selected')
        return False

    def calculate_model_salvation(self, model_attacked, weapon_armour_penetration):
        raw_salvation = model_attacked.get_model_salvation()
        salvation = raw_salvation - weapon_armour_penetration
        invulnerable_save = model_attacked.get_invulnerable_save()

        if raw_salvation > 6 and invulnerable_save:
            log(f'\t[PLAYER {self.name}] reports that [{model_attacked.name}] will save at it\'s '
                f'invulnerable save of {invulnerable_save} instead of having to save at {salvation} '
                f'(SV {raw_salvation}+  AP {weapon_armour_penetration})')
            return invulnerable_save

        if invulnerable_save and invulnerable_save < salvation:
            log(f'\t[PLAYER {self.name}] reports that [{model_attacked.name}] will save at it\'s '
                f'invulnerable save of {invulnerable_save} instead of having to save at {salvation} '
                f'(SV {raw_salvation}+  AP {weapon_armour_penetration})')
            return invulnerable_save
        else:
            log(f'\t[PLAYER {self.name}] reports that [{model_attacked.name}] will save at it\'s '
                f'own salvation of {salvation} (SV {raw_salvation}+  AP {weapon_armour_penetration})')
            return salvation

    def get_army_threat_level(self):
        return self.army.get_threat_level()

    def get_deployment_zone(self):
        return self.deployment_zone

    def get_last_rolled_dice_values(self):
        return self.dices.last_roll_dice_values

    def get_next_unit_for_shooting_or_charging(self):
        self.selected_unit = None
        if self.units_selection_list and self.units_selection_list[self.unit_idx]:
            self.selected_unit = self.units_selection_list[self.unit_idx]
            self.unit_idx += 1
        return self.selected_unit

    def get_selected_unit(self):
        return self.selected_unit

    def get_unit_to_deploy(self):
        return self.army.get_unit_to_deploy()

    def get_units_alive(self):
        """Return a list of alive units."""
        return self.army.get_units_alive()

    def get_units_available_for_moving(self):
        return self.army.get_units_available_for_moving()

    def get_units_for_battle_shock(self):
        return self.army.get_units_for_battle_shock()

    def has_units_to_deploy(self):
        """Check if there are units left to deploy."""
        return self.army.are_there_units_still_to_be_deployed()

    def increment_command_points(self):
        """Increase command points and notify the player."""
        self.command_points += 1
        log(f"\t[PLAYER {self.name}] has gained a command point, total: {self.command_points}", True)

    def load_army(self, army_cfg):
        """Load the player's army based on the provided configuration."""
        log(f'Loading army from player {self.name}')
        if not army_cfg:
            log(f"\t[PLAYER {self.name}] has no army configuration provided.")
            return
        for unit in army_cfg.get('units', []):
            self.load_unit(unit)
        log(f"\t[PLAYER {self.name}]'s army has been loaded!")

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
            log(f'\t[PLAYER {self.name}] Model [{models_cfg["name"]}] has not been found in Data Base')
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
                        log(f'\t[PLAYER {self.name}] Weapon {weapon_name} has no abilities')
                else:
                    weapon_cls = RangedWeapon
                    weapon_data = self.database.get_ranged_weapon_by_name(weapon_name, model_id)[0]
                    weapon_abilities = self.database.get_weapon_abilities(model_name, weapon_name, WeaponType.RANGED)
                weapon_list.append(weapon_cls(weapon_name, weapon_data, weapon_abilities))
        return weapon_list

    def make_announcement(self):
        """Announce the player's faction and detachment."""
        log(f"\t[PLAYER {self.name}] will play with {self.faction} '{self.detachment}'")
        log(f"\t[PLAYER {self.name}] Units used: [{', '.join(unit.name for unit in self.army.units)}]")

    def new_turn(self):
        # Update danger score
        self.army.calculate_danger_score()
        for unit in self.army.units:
            unit.start_new_turn()

    def roll_players_dice(self, number_of_dices=1, sides=6, show_throw=True):
        """Roll a dice and display the result."""
        self.dices.roll_dices(number_of_dices=number_of_dices, sides=sides)

        if show_throw:
            log_text = f'\t[PLAYER {self.name}] rolled {self.dices.last_roll_dice_count}D{sides} getting a: '

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
        self.detachment = f"{BOLD_ON}{self.factions_color}{detachment}{Fore.RESET}{BOLD_OFF}"

    def set_faction(self, faction_cfg):
        """Set the player's faction."""
        self.faction = f"{BOLD_ON}{self.factions_color}{faction_cfg}{Fore.RESET}{BOLD_OFF}"

    def set_rol(self, rol):
        """Set the player's role (attacker or defender)."""
        role_colors = {
            PlayerRol.ATTACKER.value: Fore.RED,
            PlayerRol.DEFENDER.value: Fore.BLUE,
        }
        role_color = role_colors.get(rol, Fore.RESET)
        role_name = "ATTACKER" if rol == PlayerRol.ATTACKER.value else "DEFENDER"
        log(f"\t[PLAYER {self.name}] will be the {role_color}{role_name}{Fore.RESET}", True)
        self.rol = rol

    def set_ranged_target_for_selected_unit(self, enemy_units_list):
        for model in self.selected_unit.get_unit_models_available_for_shooting():
            if model.set_ranged_target_for_model(enemy_units_list):
                self.selected_unit.has_shoot = True

    def set_units_for_charge(self):
        self.unit_idx = 0
        self.units_selection_list = self.army.get_units_available_for_charging()
        if self.units_selection_list:
            log(f'\t[PLAYER {self.name}] units available (alive and not engaged) for charging are: '
                f'{", ".join([unit.name for unit in self.units_selection_list])}')
        else:
            log(f'\t[PLAYER {self.name}] no units available for charging')

    def set_units_for_shooting(self):
        self.unit_idx = 0
        self.units_selection_list = self.army.get_units_available_for_shooting()
        log(f'\t[PLAYER {self.name}] units available (alive and not engaged) for shooting are: '
            f'{", ".join([unit.name for unit in self.units_selection_list])}')
