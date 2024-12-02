import random
from army import Army, Model, Unit, MeleeWeapon, RangedWeapon
from colorama import Fore
from enums import PlayerRol

# Constants for bold text
bold_on = "\033[1m"
bold_off = "\033[0m"

# List of adjectives for a six roll dice
six_roll_dice_adjectives = [
    'Wonderful', 'Marvelous', 'Spectacular', 'Stunning', 'Glorius', 'Magnificent', 'Exquisite', 'Enchanting',
    'Dazzling', 'Breathtaking', 'Fabulous', 'Remarkable', 'Astounding', 'Astonishing', 'Phenomenal', 'Superb']

# List of available colors
colors_list = [Fore.RED, Fore.LIGHTRED_EX, Fore.GREEN, Fore.LIGHTGREEN_EX, Fore.YELLOW,
               Fore.BLUE, Fore.LIGHTBLUE_EX, Fore.MAGENTA, Fore.LIGHTMAGENTA_EX, Fore.CYAN,
               Fore.LIGHTCYAN_EX, Fore.LIGHTWHITE_EX]


class Player:
    def __init__(self, database, name=None, army_cfg=None, faction_color=None):
        self.database = database
        self.board_map = None
        self.user_color = colors_list[random.randint(0, len(colors_list) - 1)]
        self.factions_color = None
        self.name = f"{self.user_color}{bold_on}{name}{bold_off}{Fore.RESET}"
        self.army_cfg = army_cfg
        self.army = Army()
        self.faction = None
        self.detachment = self.army_cfg['detachment']
        self.rol = None
        self.deployment_zone = None
        self.last_roll_dice = None
        self.command_points = 0
        self.players_turn = 0

        if faction_color == 'Red':
            self.factions_color = Fore.RED
        elif faction_color == 'Green':
            self.factions_color = Fore.GREEN

        self.set_faction(self.army_cfg['faction'])
        self.set_detachment(self.army_cfg['detachment'])
        self.load_army(self.army_cfg['army'])
        self.make_announcement()

    def get_units_alive(self):
        return [unit for unit in self.army.units if not unit.is_destroyed]

    def has_units_to_deploy(self):
        return self.army.are_there_units_still_to_be_deployed()

    def increment_command_points(self):
        self.command_points += 1
        print(f"\t\t{self.name} has incremented its command points by 1, "
              f"bringing the total to {self.command_points}")

    def load_army(self, army_cfg):
        for unit in army_cfg['units']:
            self.load_unit(unit)
        print(f"\t{self.name} army has been loaded!")

    def load_unit(self, unit_cfg):
        models_list = []

        for models in unit_cfg['models']:
            models_list.extend(self.load_models(models))

        # Create Unit with models list
        tmp_unit = Unit(unit_cfg['unit_name'], models_list)
        self.army.add_unit_into_army(tmp_unit)

    def load_models(self, models_cfg):
        is_warlord = 'warlord' in models_cfg
        amount = models_cfg.get('amount', 1)
        models_list = []

        try:
            model_attributes = self.database.get_model_by_name(models_cfg['name'])[0]
            for _ in range(amount):
                models_list.append(self.load_model(models_cfg['name'], model_attributes, models_cfg['weapons'],
                                                   is_warlord))
            return models_list
        except IndexError:
            print(f"Model {models_cfg['name']} not found!")

    def load_model(self, model_name, model_attributes, model_weapons_cfg, is_warlord=False):
        weapon_list = []
        for weapon in model_weapons_cfg['melee']:
            try:
                melee_weapon = MeleeWeapon(weapon,
                                           self.database.get_melee_weapon_by_name(
                                               weapon, self.database.get_model_id_by_name(model_name)[0][0])[0]
                                           )
                weapon_list.append(melee_weapon)
            except IndexError:
                print(f"Couldn't find {weapon} in the database")

        for weapon in model_weapons_cfg['ranged']:
            try:
                ranged_weapon = RangedWeapon(weapon,
                                             self.database.get_ranged_weapon_by_name(
                                                 weapon, self.database.get_model_id_by_name(model_name)[0][0])[0])
                weapon_list.append(ranged_weapon)
            except IndexError:
                print(f"Couldn't find {weapon} in database")

        model_keywords = self.database.get_model_keywords(model_name)
        tmp_model = Model(model_name, model_attributes, weapon_list, model_keywords, is_warlord)
        return tmp_model

    def make_announcement(self):
        print(f"\t{self.name} will play with "
              f"{self.faction} \'{self.detachment}\'{Fore.RESET}")
        print(f"\t\t{', '.join(unit.name for unit in self.army.units)}")

    def move_units(self):
        self.army.move_units()

    def place_unit(self):
        unit_to_place = self.army.get_unit_to_place()
        print(f"\t\t{self.name} is placing unit {unit_to_place.name}")
        self.board_map.place_unit(self.deployment_zone, unit_to_place)
        unit_to_place.has_been_deployed = True

    def set_deployment_zone(self, zone):
        self.deployment_zone = zone

    def set_detachment(self, detachment):
        self.detachment = f"{bold_on}{self.factions_color}{detachment}{Fore.RESET}{bold_off}"

    def set_faction(self, faction_cfg):
        self.faction = f"{bold_on}{self.factions_color}{faction_cfg}{Fore.RESET}{bold_off}"

    def set_rol(self, rol):
        if rol == PlayerRol.ATTACKER.value:
            print(f"\t{self.name} will be the {Fore.RED}ATTACKER{Fore.RESET}")
        else:
            print(f"\t{self.name} will be the {Fore.BLUE}DEFENDER{Fore.RESET}")
        self.rol = rol

    def set_up_the_map(self, board_map):
        self.board_map = board_map

    def roll_players_dice(self, sides=6, show_throw=True):
        self.last_roll_dice = random.randint(1, sides)

        if show_throw:
            if self.last_roll_dice == 6:
                print(f"\t\t{bold_on}{Fore.LIGHTYELLOW_EX}"
                      f"{six_roll_dice_adjectives[random.randint(0, len(six_roll_dice_adjectives) -1)].upper()}!"
                      f"{Fore.RESET}{bold_off} "
                      f"{self.name} rolled a {self.user_color}{self.last_roll_dice}{Fore.RESET}!")
            elif self.last_roll_dice == 1:
                print(f"\t\tOuch... {self.name} rolled a {self.user_color}{self.last_roll_dice}{Fore.RESET}")
            else:
                print(f"\t\t{self.name} rolled a {self.user_color}{self.last_roll_dice}{Fore.RESET}")
        return self.last_roll_dice
