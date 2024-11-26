import random
from mailcap import show

from colorama import init, Fore, Back, Style

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
    def __init__(self, name=None):
        self.user_color = colors_list[random.randint(0, len(colors_list) - 1)]
        self.factions_color = None
        self.name = f"{bold_on}{name}{bold_off}"
        self.faction = None
        self.rol = None
        self.last_roll_dice = None
        self.command_points = 0
        self.players_turn = 0

    def increment_command_points(self):
        self.command_points += 1
        print(f"\t\t{self.user_color}{self.name}{Fore.RESET} has incremented its command points in 1, there's a total of {self.command_points}")

    def set_roll(self, rol):
        if rol == ATTACKER:
            print(f"\t{self.user_color}{self.name}{Fore.RESET} will be the {Fore.RED}ATTACKER{Fore.RESET}")
        else:
            print(f"\t{self.user_color}{self.name}{Fore.RESET} will be the {Fore.BLUE}DEFENDER{Fore.RESET}")
        self.rol = rol

    def set_faction(self, faction_cfg):
        self.faction = f"{bold_on}{faction_cfg[0]}{bold_off}"
        if faction_cfg[1] == "Green":
            self.factions_color = Fore.GREEN
        elif faction_cfg[1] == "Red":
            self.factions_color = Fore.RED
        print(f"\t{self.user_color}{self.name}{Fore.RESET} will play with {self.factions_color}{self.faction}{Fore.RESET}")

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

