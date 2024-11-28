from colorama import Fore
from random import random
from shapely.geometry import Point, Polygon

# Constants for bold text
bold_on = "\033[1m"
bold_off = "\033[0m"

board_configurations = list()


class Objective:
    def __init__(self, coord):
        self.coord = coord
        self.is_available = True  # Set it by default, once consumed or burned just disable it
        self.nobody_area = True
        self.unit_controlling_it = None


class BoardHandle:
    def __init__(self, name, wide, large, attacker_zone, defender_zone, objectives):
        self.name = name
        self.wide = wide
        self.large = large
        # Create a 60x44 matrix filled with zeros
        self.boardgame = [[" " for _ in range(self.large)] for _ in range(self.wide)]
        self.attacker_zone = Polygon(attacker_zone)
        self.defender_zone = Polygon(defender_zone)
        self.objectives = objectives

    def set_objective(self, coord):
        self.boardgame[int(coord.y)][int(coord.x)] = f'{Fore.YELLOW}{bold_on}OB{Fore.RESET}{bold_off}'

    def display_board_game(self, has_game_started):
        if has_game_started:
            # Do not print attackers nor defenders zone, just print units on the field
            pass
        else:
            # Print configuration for seeing how the map looks like
            print(f"\t   {' '.join(['{:02}'.format(x) for x in range(self.large)])}")
            for count, row in enumerate(self.boardgame, start=0):
                print(f"\t{'{:02}'.format(count)}|{' '.join(f'{str(cell):2}' for cell in row)}|")
            print(f"\t   {' '.join(['{:02}'.format(x) for x in range(self.large)])}")

    def get_random_point_within_attacker_zone(self):
        zone = self.attacker_zone
        minx, miny, maxx, maxy = map(int, zone.bounds)

        while True:
            random_x = random.randint(minx, maxx)
            random_y = random.randint(miny, maxy)
            point = Point(random_x, random_y)
            if zone.contains(point) or zone.touches(point):
                return random_x, random_y

    def get_random_point_within_defender_zone(self):
        zone = self.defender_zone
        minx, miny, maxx, maxy = map(int, zone.bounds)

        while True:
            random_x = random.randint(minx, maxx)
            random_y = random.randint(miny, maxy)
            point = Point(random_x, random_y)
            if zone.contains(point) or zone.touches(point):
                return random_x, random_y


class Map:
    def __init__(self, configuration):
        self.map = configuration
        self.attacker = None
        self.defender = None
        self.objectives = configuration.objectives
        self.has_game_started = False

    def set_attacker(self, attacker):
        self.attacker = attacker
        self.mark_deployment_zone(self.map.attacker_zone, 'A')

    def set_defender(self, defender):
        self.defender = defender
        self.mark_deployment_zone(self.map.defender_zone, 'D')

    def mark_deployment_zone(self, zone, symbol):
        minx, miny, maxx, maxy = map(int, zone.bounds)
        for y in range(miny, maxy + 1):
            for x in range(minx, maxx + 1):
                if zone.intersects(Point(x, y)) and self.map.boardgame[y][x] == " ":
                    self.map.boardgame[y][x] = symbol

    def place_objectives(self):
        for objective in self.objectives:
            coord = Point(objective.coord)
            try:
                self.map.set_objective(coord)
            except IndexError:
                print(f"Objective at point {coord} could not be set!")

    def place_unit(self, unit):
        pass

    def display_board(self):
        if not self.has_game_started:
            print("Map configuration:")
        else:
            print("Game Board:")
        self.map.display_board_game(self.has_game_started)


mapConfig1 = BoardHandle(
    name="Map 1",
    wide=44,
    large=60,
    attacker_zone=[Point(0, 0), Point(17, 0), Point(17, 43), Point(0, 43)],     # Rectangle
    defender_zone=[Point(42, 0), Point(59, 0), Point(59, 43), Point(42, 43)],   # Rectangle
    objectives=[Objective(coord=(9, 21)), Objective(coord=(49, 21)), Objective(coord=(21, 9)),
                Objective(coord=(37, 9)), Objective(coord=(21, 33)), Objective(coord=(37, 33))]
)
