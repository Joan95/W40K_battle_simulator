import random
from colorama import Fore
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

    def set_model(self, coord, model):
        self.boardgame[int(coord.y)][int(coord.x)] = f'{bold_on}{model.name[0:2]}{bold_off}'
        model.position = coord
        model.is_alive = True

    def display_board_game(self):
        # Print configuration for seeing how the map looks like
        print(f"\t   {' '.join(['{:02}'.format(x) for x in range(self.large)])}")
        for count, row in enumerate(self.boardgame, start=0):
            print(f"\t{'{:02}'.format(count)}|{' '.join(f'{str(cell):2}' for cell in row)}|")
        print(f"\t   {' '.join(['{:02}'.format(x) for x in range(self.large)])}")

    def get_random_point_in_zone(self, zone):
        minx, miny, maxx, maxy = map(int, zone.bounds)

        while True:
            random_x = random.randint(minx, maxx)
            random_y = random.randint(miny, maxy)
            point = Point(random_x, random_y)
            if zone.contains(point) or zone.touches(point):
                return Point(random_x, random_y)

    def is_cell_empty(self, coord):
        x, y = int(coord.x), int(coord.y)
        if self.boardgame[y][x] != ' ' and self.boardgame[y][x] != 'A' and self.boardgame[y][x] != 'D':
            return False
        else:
            return True

    def get_adjacent_points(self, coord, distance=1):
        x, y = coord.x, coord.y
        adjacent_points = [
            Point(x + dx, y + dy) for dx in range(-distance, distance + 1)
            for dy in range(-distance, distance + 1) if (dx, dy) != (0, 0)
        ]
        return adjacent_points


class Map:
    def __init__(self, configuration):
        self.map_configuration = configuration
        self.attacker = None
        self.defender = None
        self.objectives = configuration.objectives
        self.has_game_started = False

    def set_attacker(self, attacker):
        self.attacker = attacker
        self.mark_deployment_zone(self.map_configuration.attacker_zone, 'A')

    def set_defender(self, defender):
        self.defender = defender
        self.mark_deployment_zone(self.map_configuration.defender_zone, 'D')

    def start_the_game(self):
        self.has_game_started = True
        print("\t\tLet the game begin! Destroy your anuses!")

    def mark_deployment_zone(self, zone, symbol):
        minx, miny, maxx, maxy = map(int, zone.bounds)
        for y in range(miny, maxy + 1):
            for x in range(minx, maxx + 1):
                if zone.intersects(Point(x, y)) and self.map_configuration.is_cell_empty(Point(x, y)):
                    self.map_configuration.boardgame[y][x] = symbol

    def remove_attacker_defender_zone(self):
        self.mark_deployment_zone(self.map_configuration.attacker_zone, ' ')
        self.mark_deployment_zone(self.map_configuration.defender_zone, ' ')

    def place_objectives(self):
        for objective in self.objectives:
            coord = Point(objective.coord)
            try:
                self.map_configuration.set_objective(coord)
            except IndexError:
                print(f"Objective at point {coord} could not be set!")

    def place_unit(self, zone, unit):
        first_model_point = self.map_configuration.get_random_point_in_zone(zone)
        self.map_configuration.set_model(first_model_point, unit.models[0])
        adjacent_points = self.map_configuration.get_adjacent_points(first_model_point)
        model_index = 1
        while model_index < len(unit.models) and adjacent_points:
            point = adjacent_points.pop(0)
            if 0 <= point.x < self.map_configuration.large and 0 <= point.y < self.map_configuration.wide:
                if self.map_configuration.is_cell_empty(point) and (zone.contains(point) or zone.touches(point)):
                    self.map_configuration.set_model(point, unit.models[model_index])
                    model_index += 1
                    adjacent_points.extend(self.map_configuration.get_adjacent_points(point))
        # self.display_board()

    def display_board(self):
        print()
        print("\tGame Board:")
        self.map_configuration.display_board_game()
        print()


mapConfig1 = BoardHandle(
    name="Map 1",
    wide=44,
    large=60,
    attacker_zone=[Point(0, 0), Point(17, 0), Point(17, 43), Point(0, 43)],     # Rectangle
    defender_zone=[Point(42, 0), Point(59, 0), Point(59, 43), Point(42, 43)],   # Rectangle
    objectives=[Objective(coord=(9, 21)), Objective(coord=(49, 21)), Objective(coord=(21, 9)),
                Objective(coord=(37, 9)), Objective(coord=(21, 33)), Objective(coord=(37, 33))]
)
