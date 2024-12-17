import random
from colorama import Fore
from logging_handler import log
from model import Model
from shapely.geometry import Point, Polygon

# Constants for bold text
BOLD_ON = "\033[1m"
BOLD_OFF = "\033[0m"

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

    def clear_model(self, coord):
        self.boardgame[int(coord.y)][int(coord.x)] = "  "

    def display_board_game(self):
        # Print configuration for seeing how the map looks like
        log(f"\t\t{' '.join(['{:02}'.format(x) for x in range(self.large)])}", True)
        for count, row in enumerate(self.boardgame, start=0):
            row_to_print = f"\t{'{:02}'.format(count)}|"
            for cell in row:
                if type(cell) == str:
                    row_to_print += f' {str(cell):2}'
                elif type(cell) == Model:
                    if 'EPIC HERO' in cell.keywords:
                        row_to_print += f' {Fore.LIGHTMAGENTA_EX}{BOLD_ON}{cell.name[:2]}{BOLD_OFF}'
                    elif 'CHARACTER' in cell.keywords:
                        row_to_print += f' {Fore.MAGENTA}{BOLD_ON}{cell.name[:2]}{BOLD_OFF}'
                    else:
                        row_to_print += f' {cell.name[:2]}'
            log(f"{row_to_print}|", True)
        log(f"\t\t{' '.join(['{:02}'.format(x) for x in range(self.large)])}", True)

    def is_cell_empty(self, coord):
        x, y = int(coord.x), int(coord.y)
        try:
            return self.boardgame[y][x] in (' ', 'A', 'D')
        except IndexError:
            pass

    def set_objective(self, coord):
        self.boardgame[int(coord.y)][int(coord.x)] = f'{Fore.YELLOW}{BOLD_ON}OB{Fore.RESET}{BOLD_OFF}'

    def set_model(self, coord, model):
        self.boardgame[int(coord.y)][int(coord.x)] = model
        model.position = coord
        model.is_alive = True
        log(f'\t\t\tModel [{model.name}] set at position {model.position}')


def get_random_point_in_zone(zone):
    minx, miny, maxx, maxy = map(int, zone.bounds)

    while True:
        random_x = random.randint(minx, maxx)
        random_y = random.randint(miny, maxy)
        point = Point(random_x, random_y)
        if zone.contains(point) or zone.touches(point):
            return Point(random_x, random_y)


def get_adjacent_points(coord, distance=1):
    x, y = coord.x, coord.y
    adjacent_points = [
        Point(x + dx, y + dy) for dx in range(-distance, distance + 1)
        for dy in range(-distance, distance + 1) if (dx, dy) != (0, 0)
    ]
    return adjacent_points


def get_distance_between_two_points(point_a, point_b):
    return ((point_a.x - point_b.x) ** 2 + (point_a.y - point_b.y) ** 2) ** 0.5


class Battlefield:
    def __init__(self, configuration):
        self.map_configuration = configuration
        self.objectives = configuration.objectives
        self.has_game_started = False
        self.set_attacker()
        self.set_defender()

    def clamp_position_within_boundaries(self, position):
        clamped_x = max(0, min(position.x, self.map_configuration.wide - 1))
        clamped_y = max(0, min(position.y, self.map_configuration.large - 1))
        return Point(clamped_x, clamped_y)

    def deploy_unit(self, zone, unit):
        first_model_point = get_random_point_in_zone(zone)
        while not self.map_configuration.is_cell_empty(first_model_point) and \
                (zone.contains(first_model_point) or zone.touches(first_model_point)):
            # Place first model in a valid and available point inside its zone
            first_model_point = get_random_point_in_zone(zone)

        self.map_configuration.set_model(first_model_point, unit.models[0])

        # Now calculate adjacent points for the rest of the models in unit
        adjacent_points = get_adjacent_points(first_model_point)
        model_index = 1
        while model_index < len(unit.models) and adjacent_points:
            point = adjacent_points.pop(0)
            if 0 <= point.x < self.map_configuration.large and 0 <= point.y < self.map_configuration.wide:
                if self.map_configuration.is_cell_empty(point) and (zone.contains(point) or zone.touches(point)):
                    self.map_configuration.set_model(point, unit.models[model_index])
                    model_index += 1
                    adjacent_points.extend(get_adjacent_points(point))
        # self.display_board()

    def display_board(self):
        print()
        print("\tGame Board:")
        self.map_configuration.display_board_game()
        print()

    def is_cell_empty(self, coord):
        return self.map_configuration.is_cell_empty(coord)

    def kill_model(self, model):
        log(f'[BATTLEFIELD] Removing model [{model.name}] [{model.position}] from battlefield')
        self.map_configuration.clear_model(model.position)

    def mark_deployment_zone(self, zone, symbol):
        minx, miny, maxx, maxy = map(int, zone.bounds)
        for y in range(miny, maxy + 1):
            for x in range(minx, maxx + 1):
                if zone.intersects(Point(x, y)) and self.map_configuration.is_cell_empty(Point(x, y)):
                    self.map_configuration.boardgame[y][x] = symbol

    def move_model(self, model, new_position):
        self.map_configuration.clear_model(model.position)
        self.map_configuration.set_model(new_position, model)

    def place_objectives(self):
        for objective in self.objectives:
            coord = Point(objective.coord)
            try:
                self.map_configuration.set_objective(coord)
            except IndexError:
                print(f"Objective at point {coord} could not be set!")

    def remove_attacker_defender_zone(self):
        self.mark_deployment_zone(self.map_configuration.attacker_zone, ' ')
        self.mark_deployment_zone(self.map_configuration.defender_zone, ' ')

    def set_attacker(self):
        self.mark_deployment_zone(self.map_configuration.attacker_zone, 'A')

    def set_defender(self):
        self.mark_deployment_zone(self.map_configuration.defender_zone, 'D')

    def start_the_game(self):
        self.has_game_started = True
        print("\t\tLet the game begin! Destroy your anuses!")
