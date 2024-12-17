from battlefield import get_adjacent_points
from colorama import Fore
from logging_handler import log
from shapely.geometry import LineString, Polygon, Point

# Constants for bold text
BOLD_ON = "\033[1m"
BOLD_OFF = "\033[0m"


def update_model_position(board_map, model, new_position):
    """Update the model's position on the board."""
    if model.position:
        board_map.map_configuration.clear_model(model.position)
    board_map.map_configuration.set_model(new_position, model)
    model.move_to(new_position)


def is_position_occupied(board_map, position):
    return not board_map.is_cell_empty(position)


class Unit:
    def __init__(self, name, models):
        self.raw_name = name
        self.name = name
        self.models = models
        self.is_warlord_in_the_unit = self.check_if_warlord_in_unit()
        self.moral_check_passed = True
        self.is_destroyed = False
        self.is_engaged = False
        self.is_unit_visible = self.check_unit_visibility()
        self.has_been_deployed = False
        self.has_advanced = False
        self.has_moved = False
        self.has_shoot = False
        self.targeted_enemy_unit = None
        self.unit_centroid = None
        self.unit_initial_force = len(self.models)
        self.unit_leadership = None
        self.unit_polygon = None
        self.unit_potential_melee_damage = None
        self.unit_potential_ranged_damage = None
        self.unit_potential_salvation = None
        self.unit_objective_control = None
        self.unit_survivability = None
        self.unit_threat_level = None

        self.update_unit_total_score()

        if self.is_warlord_in_the_unit:
            self.name = f'{Fore.MAGENTA}{BOLD_ON}{self.raw_name} (WL){BOLD_OFF}'

    def calculate_unit_potential_damages(self):
        self.unit_potential_melee_damage = sum(model.model_potential_damage_melee_attack *
                                               model.model_impact_probability_melee_attack
                                               for model in self.get_models_alive()) / len(self.get_models_alive())
        self.unit_potential_ranged_damage = sum(model.model_potential_damage_ranged_attack *
                                                model.model_impact_probability_ranged_attack
                                                for model in self.get_models_alive()) / len(self.get_models_alive())

    def calculate_unit_salvation_chance(self):
        self.unit_potential_salvation = sum(model.model_potential_salvation for model in self.get_models_alive()) \
                                        / len(self.get_models_alive())

    def calculate_unit_leadership(self):
        self.unit_leadership = sum(model.leadership for model in self.get_models_alive()) / len(self.models)

    def calculate_unit_objective_control(self):
        # Unit only has some objective control if it has passed the moral check, performed when unit current
        # members are lower than half of its initial force
        if self.moral_check_passed:
            self.unit_objective_control = sum(model.objective_control for model in self.get_models_alive())
        else:
            self.unit_objective_control = 0

    def calculate_unit_survivability(self):
        self.unit_survivability = (
                                          sum(model.wounds for model in self.get_models_alive())
                                          / len(self.get_models_alive())
                                  ) * self.unit_potential_salvation

    def chase_enemies(self, enemy_units):
        if not enemy_units:
            return

        # Find the most appropriate enemy unit to target based on proximity and weakness
        target_candidates = [
            (enemy_unit, get_distance(self, enemy_unit), enemy_unit.unit_threat_level) for enemy_unit in
            enemy_units
        ]
        if target_candidates:
            # Optionally adjust the sorting criteria or add weights
            target_candidates.sort(key=lambda x: (x[1], x[2]))
            closest_and_weakest_enemy = target_candidates[0][0]
            self.set_unit_target(closest_and_weakest_enemy)

    def check_if_warlord_in_unit(self):
        return any(model.is_warlord for model in self.models)

    def check_unit_visibility(self):
        is_visible = True in [model.is_visible for model in self.models]
        return is_visible

    def deploy_unit_in_zone(self, board, zone_to_deploy):
        log(f'\t\t[UNIT] Deploying [{self.raw_name}]')
        board.deploy_unit(zone_to_deploy, self)
        self.has_been_deployed = True
        # Now that unit has been deployed, calculate its polygon
        self.calculate_unit_centroid()

    def do_moral_check(self, value):
        pass

    def find_nearest_free_position(self, board_map, position):
        # Breadth-first search to find the nearest free position
        from collections import deque
        visited = set()
        queue = deque([position])
        while queue:
            current_position = queue.popleft()
            if not is_position_occupied(board_map, current_position) and not self.is_within_engagement_range(
                    current_position):
                return current_position
            visited.add(current_position)
            adjacent_points = get_adjacent_points(current_position)
            for point in adjacent_points:
                if point not in visited and 0 <= point.x < board_map.map_configuration.wide and 0 <= point.y < board_map.map_configuration.large:
                    queue.append(point)
        return None

    def form_unit_polygon(self):
        # Creates unit's polygon from models' positions
        model_coordinates = [
            (model.position.x, model.position.y)
            for model in self.get_models_alive()
            if model.position is not None
        ]

        if len(model_coordinates) == 1:
            # Single model -> Point
            self.unit_polygon = Point(model_coordinates[0])
        elif len(model_coordinates) == 2:
            # Two models -> LineString
            self.unit_polygon = LineString(model_coordinates)
        elif len(model_coordinates) >= 3:
            # Three or more models -> Polygon
            try:
                self.unit_polygon = Polygon(model_coordinates)
            except ValueError:
                # Handle degenerate polygons (e.g., collinear points)
                self.unit_polygon = LineString(model_coordinates)
        else:
            # No models alive
            self.unit_polygon = None

    def get_next_model_to_die(self):
        # From list of Model in self.models get the Model which has the lowest Model.priority_to_die and Model.is_alive
        alive_models = self.get_models_alive()
        return min(alive_models, key=lambda model: model.priority_to_die)

    def get_models_alive(self):
        return [model for model in self.models if model.is_alive]

    def get_models_ranged_attacks(self):
        shooting_dict = dict()
        for model in self.get_models_alive():
            for weapon in model.get_model_weapons_ranged():
                if weapon.target_unit:
                    entry_name = model.name + ' - ' + weapon.target_unit.raw_name + ' - ' + weapon.name
                    if entry_name not in shooting_dict:
                        shooting_dict[entry_name] = {
                            'weapon': weapon,
                            'target': weapon.target_unit,
                            'count': 1,
                            'attacker': model
                        }
                    else:
                        # Entry already in dictionary just increase the counter of attacks
                        shooting_dict[entry_name]['count'] += 1
        return shooting_dict

    def calculate_unit_centroid(self):
        # Calculate the centroid of the unit's polygon or point
        self.form_unit_polygon()
        if self.unit_polygon and not self.unit_polygon.is_empty:
            # Shapely geometries (Point, LineString, Polygon) have a .centroid property
            self.unit_centroid = self.unit_polygon.centroid
        else:
            # No valid geometry, set centroid to None
            self.unit_centroid = None

    def get_unit_centroid(self):
        return self.unit_centroid

    def get_unit_models_available_for_shooting(self):
        models_available_for_shooting = list()
        for model in self.get_models_alive():
            models_available_for_shooting.append(model)
        return models_available_for_shooting

    def get_unit_movement(self):
        return int(self.models[0].movement.replace('"', ''))

    def get_unit_threat_level(self):
        return self.unit_threat_level

    def get_unit_toughness(self):
        log(f'\t\t[UNIT] Checking unit\'s toughness')
        return self.models[0].get_model_toughness()

    def has_unit_advanced(self):
        return self.has_advanced

    def has_unit_shoot(self):
        return self.has_shoot

    def is_unit_engaged(self):
        return self.is_engaged

    def is_within_engagement_range(self, position):
        # Define an engagement range (e.g., 1 unit)
        engagement_range = 1
        for enemy_model in self.targeted_enemy_unit.models:
            if enemy_model.is_alive and position.distance(enemy_model.position) < engagement_range:
                return True
        return False

    def move_towards_target(self, board_map):
        if not self.targeted_enemy_unit.is_destroyed:
            target_position = self.targeted_enemy_unit.get_unit_centroid()

            for model in self.get_models_alive():
                if model.position:
                    direction_x = target_position.x - model.position.x
                    direction_y = target_position.y - model.position.y
                    total_distance = Point(direction_x, direction_y).distance(Point(0, 0))
                    if total_distance > 0:
                        step = min(self.get_unit_movement(), total_distance)
                        movement_x = step * (direction_x / total_distance)
                        movement_y = step * (direction_y / total_distance)
                    else:
                        movement_x = 0
                        movement_y = 0

                    new_position = Point(model.position.x + movement_x, model.position.y + movement_y)
                    new_position = board_map.clamp_position_within_boundaries(new_position)

                    if not self.is_within_engagement_range(new_position) and not \
                            is_position_occupied(board_map, new_position):
                        update_model_position(board_map, model, new_position)
                    else:
                        # Find the nearest free position if the current one is occupied or within engagement range
                        nearest_free_position = self.find_nearest_free_position(board_map, new_position)
                        if nearest_free_position:
                            update_model_position(board_map, model, nearest_free_position)

            self.has_moved = True
            self.calculate_unit_centroid()

    def set_unit_target(self, enemy_unit):
        self.targeted_enemy_unit = enemy_unit

    def start_new_turn(self):
        self.has_advanced = False
        self.has_moved = False
        self.has_shoot = False
        self.moral_check_passed = True
        for model in self.models:
            model.start_new_turn()

    def update_unit_total_score(self):
        # Recalculate everything in case of model's fainted
        self.calculate_unit_potential_damages()
        self.calculate_unit_salvation_chance()
        self.calculate_unit_leadership()
        self.calculate_unit_objective_control()
        self.calculate_unit_survivability()
        # Formula for knowing how challenging a unit is by getting the potential damage it can deal and salvation
        self.unit_threat_level = (self.unit_potential_melee_damage * 0.25 +
                                  self.unit_potential_ranged_damage * 0.25 +
                                  self.unit_potential_salvation * 0.2 +
                                  self.unit_leadership * 0.1 +
                                  self.unit_objective_control * 0.1 +
                                  self.unit_survivability * 0.1)
        # Warlord multiplier
        warlord_multiplier = 1.5 if self.is_warlord_in_the_unit else 1.0

        # Set threat level
        self.unit_threat_level = self.unit_threat_level * warlord_multiplier


def get_distance(unit1, unit2):
    pos1 = unit1.models[0].position
    pos2 = unit2.models[0].position
    if pos1 and pos2:
        return ((pos1.x - pos2.x) ** 2 + (pos1.y - pos2.y) ** 2) ** 0.5
    return float('inf')
