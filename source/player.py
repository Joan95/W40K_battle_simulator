import random
from colorama import Fore
from model import Model
from weapon import Weapon, MeleeWeapon, RangedWeapon

ATTACKER = 0
DEFENDER = 1
bold_on = "\033[1m"
bold_off = "\033[0m"
six_roll_dice_adjectives = ['Wonderful', 'Marvelous', 'Spectacular', 'Stunning', 'Glorius', 'Magnificent', 'Exquisite'
                            'Enchanting', 'Dazzling', 'Breathtaking', 'Fabulous', 'Remarkable', 'Astounding',
                            'Astonishing', 'Phenomenal', 'Superb']
colors_list = [Fore.RED, Fore.LIGHTRED_EX, Fore.GREEN, Fore.LIGHTGREEN_EX, Fore.YELLOW,
               Fore.BLUE, Fore.LIGHTBLUE_EX, Fore.MAGENTA, Fore.LIGHTMAGENTA_EX, Fore.CYAN,
               Fore.LIGHTCYAN_EX, Fore.LIGHTWHITE_EX]


class Player:
    def __init__(self, database, name=None, army_cfg=None, faction_color=None):
        self.database = database
        self.user_color = colors_list[random.randint(0, len(colors_list) - 1)]
        self.factions_color = None
        self.name = f"{bold_on}{name}{bold_off}"
        self.army_cfg = army_cfg
        self.faction = None
        self.detachment = self.army_cfg['detachment']
        self.models = list()
        self.units = list()
        self.rol = None
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

    def increment_command_points(self):
        self.command_points += 1
        print(f"\t\t{self.user_color}{self.name}{Fore.RESET} has incremented its command points in 1, "
              f"there's a total of {self.command_points}")

    def set_roll(self, rol):
        if rol == ATTACKER:
            print(f"\t{self.user_color}{self.name}{Fore.RESET} will be the {Fore.RED}ATTACKER{Fore.RESET}")
        else:
            print(f"\t{self.user_color}{self.name}{Fore.RESET} will be the {Fore.BLUE}DEFENDER{Fore.RESET}")
        self.rol = rol

    def make_announcement(self):
        print(f"\t{self.user_color}{self.name}{Fore.RESET} will play with "
              f"{self.faction} \'{self.detachment}\'{Fore.RESET}")
        print(f"\t\t{', '.join(model.name for model in self.models)}")

    def set_faction(self, faction_cfg):
        self.faction = f"{bold_on}{self.factions_color}{faction_cfg}{Fore.RESET}{bold_off}"

    def set_detachment(self, detachment):
        self.detachment = f"{bold_on}{self.factions_color}{detachment}{Fore.RESET}{bold_off}"

    def load_army(self, army):
        for character in army['characters']:
            model = Model(character['name'], self.database.get_model_by_name(character['name'])[0])

            for weapon in character['weapons']['melee']:
                model.set_weapon(MeleeWeapon(weapon, self.database.get_melee_weapon_by_name(weapon)[0]))

            for weapon in character['weapons']['ranged']:
                model.set_weapon(RangedWeapon(weapon, self.database.get_ranged_weapon_by_name(weapon)[0]))

            # Append model
            self.models.append(model)

        for battleline in army['battleline']:
            pass

        for transports in army['dedicated_transports']:
            pass

        for others in army['other_datasheets']:
            pass

        print(f"Army has been loaded")

    def roll_players_dice(self, sides=6, show_trow=True):
        self.last_roll_dice = random.randint(1, sides)

        if show_trow:
            if self.last_roll_dice == 6:
                print(f"\t\t{bold_on}{Fore.LIGHTYELLOW_EX}{six_roll_dice_adjectives[random.randint(0, len(six_roll_dice_adjectives) -1 )].upper()}!{Fore.RESET}{bold_off} "
                      f"{self.user_color}{self.name}{Fore.RESET} rolled a "
                      f"{self.user_color}{self.last_roll_dice}{Fore.RESET}!")
            elif self.last_roll_dice == 1:
                print(f"\t\tOuch... {self.user_color}{self.name}{Fore.RESET} rolled a "
                      f"{self.user_color}{self.last_roll_dice}{Fore.RESET}")
            else:
                print(f"\t\t{self.user_color}{self.name}{Fore.RESET} rolled a "
                      f"{self.user_color}{self.last_roll_dice}{Fore.RESET}")
        return self.last_roll_dice

