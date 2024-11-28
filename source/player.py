import random
from army import Army, Model, Unit, MeleeWeapon, RangedWeapon
from colorama import Fore
from enums import PlayerRol

# Constants for bold text
bold_on = "\033[1m"
bold_off = "\033[0m"

# List of adjectives for a six roll dice
six_roll_dice_adjectives = ['Wonderful', 'Marvelous', 'Spectacular', 'Stunning', 'Glorius', 'Magnificent', 'Exquisite'
                            'Enchanting', 'Dazzling', 'Breathtaking', 'Fabulous', 'Remarkable', 'Astounding',
                            'Astonishing', 'Phenomenal', 'Superb']

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

    def has_units_to_deploy(self):
        if self.army.are_there_units_still_to_be_deployed():
            return True
        else:
            return False

    def place_unit(self):
        print(f"\t\t{self.name} is placing a unit")
        self.army.place_unit()

    def units_left_to_deploy(self):
        return self.army.units_left_to_deploy

    def increment_command_points(self):
        self.command_points += 1
        print(f"\t\t{self.name} has incremented its command points in 1, "
              f"there's a total of {self.command_points}")

    def set_up_the_map(self, board_map):
        self.board_map = board_map

    def set_rol(self, rol):
        if rol == PlayerRol.ATTACKER.value:
            print(f"\t{self.name} will be the {Fore.RED}ATTACKER{Fore.RESET}")
        else:
            print(f"\t{self.name} will be the {Fore.BLUE}DEFENDER{Fore.RESET}")
        self.rol = rol

    def set_deployment_zone(self, zone):
        self.deployment_zone = zone

    def make_announcement(self):
        print(f"\t{self.name} will play with "
              f"{self.faction} \'{self.detachment}\'{Fore.RESET}")
        print(f"\t\t{', '.join(unit.name for unit in self.army.units)}")

    def set_faction(self, faction_cfg):
        self.faction = f"{bold_on}{self.factions_color}{faction_cfg}{Fore.RESET}{bold_off}"

    def set_detachment(self, detachment):
        self.detachment = f"{bold_on}{self.factions_color}{detachment}{Fore.RESET}{bold_off}"

    def load_army(self, army_cfg):
        for unit in army_cfg['units']:
            tmp_models = list()

            for model in unit['models']:
                is_warlord = False
                if 'warlord' in model:
                    is_warlord = True

                if 'amount' in model:
                    amount = model['amount']
                else:
                    amount = 1

                for x in range(amount):
                    try:
                        model_cfg = self.database.get_model_by_name(model['name'])[0]
                    except IndexError:
                        print(f"Model {model['name']} not found!")
                        continue
                    model_keywords = self.database.get_model_keywords(model['name'])
                    tmp_model = Model(model['name'], model_cfg, model_keywords, is_warlord)

                    for weapon in model['weapons']['melee']:
                        try:
                            tmp_model.set_weapon(MeleeWeapon(weapon, self.database.get_melee_weapon_by_name(weapon)[0]))
                        except IndexError:
                            print(f"Couldn't find {weapon} in database")

                    for weapon in model['weapons']['ranged']:
                        try:
                            tmp_model.set_weapon(RangedWeapon(weapon, self.database.get_ranged_weapon_by_name(weapon)[0]))
                        except IndexError:
                            print(f"Couldn't find {weapon} in database")

                    tmp_models.append(tmp_model)
            # Create Unit with models list
            tmp_unit = Unit(unit['unit_name'], tmp_models)
            self.army.add_unit_into_army(tmp_unit)

        print(f"\t{self.name} army has been loaded!")

    def roll_players_dice(self, sides=6, show_trow=True):
        self.last_roll_dice = random.randint(1, sides)

        if show_trow:
            if self.last_roll_dice == 6:
                print(f"\t\t{bold_on}{Fore.LIGHTYELLOW_EX}"
                      f"{six_roll_dice_adjectives[random.randint(0, len(six_roll_dice_adjectives) -1 )].upper()}!"
                      f"{Fore.RESET}{bold_off} "
                      f"{self.name} rolled a {self.user_color}{self.last_roll_dice}{Fore.RESET}!")
            elif self.last_roll_dice == 1:
                print(f"\t\tOuch... {self.name} rolled a {self.user_color}{self.last_roll_dice}{Fore.RESET}")
            else:
                print(f"\t\t{self.name} rolled a {self.user_color}{self.last_roll_dice}{Fore.RESET}")
        return self.last_roll_dice

