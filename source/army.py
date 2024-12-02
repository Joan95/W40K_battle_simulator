from enums import WeaponType
from map import *
from shapely.geometry import Polygon, Point

# Constants for bold text
bold_on = "\033[1m"
bold_off = "\033[0m"
MAX_THROW_D6 = 6


class Keywords:
    def __init__(self, name):
        self.name = name


class Model:
    def __init__(self, name, attributes_tuple, weapons, keywords, is_warlord=False):
        self.name = name
        self.movement = attributes_tuple[0]
        self.toughness = attributes_tuple[1]
        self.salvation = attributes_tuple[2]
        self.wounds = attributes_tuple[3]
        self.leadership = attributes_tuple[4]
        self.objective_control = attributes_tuple[5]
        self.invulnerable_save = attributes_tuple[6]
        self.feel_no_pain = attributes_tuple[7]
        self.position = None
        self.weapons = list(weapons)
        self.keywords = list(keywords)
        self.can_be_disengaged_from_unit = 'CHARACTER' in keywords
        self.is_warlord = is_warlord
        self.is_alive = True
        self.is_visible = True
        self.melee_attack_impact_probability = 0
        self.ranged_attack_impact_probability = 0
        self.melee_attack_potential_damage = 0
        self.ranged_attack_potential_damage = 0
        self.model_potential_attack_damage = None
        self.model_potential_salvation = self.calculate_model_defence_score()
        # Calculate its score
        self.calculate_model_danger_score()

    def move(self):
        print(f"{self.name} moving!")

    def calculate_model_defence_score(self):
        chance_of_defence = (MAX_THROW_D6 - (int(self.salvation) - 1)) / 6
        if self.feel_no_pain:
            chance_of_defence += (MAX_THROW_D6 - (int(self.feel_no_pain) - 1)) / 6
        return chance_of_defence

    def calculate_all_weapon_hit_probability_and_damage(self):
        for weapon in self.weapons:
            if weapon.type == WeaponType.RANGED.value:
                self.ranged_attack_impact_probability += weapon.weapon_hit_probability
                self.ranged_attack_potential_damage += weapon.weapon_potential_damage
            elif weapon.type == WeaponType.MELEE.value:
                self.melee_attack_impact_probability += weapon.weapon_hit_probability
                self.melee_attack_potential_damage += weapon.weapon_potential_damage
        self.ranged_attack_impact_probability /= len([x for x in self.weapons if x.type == WeaponType.RANGED.value])
        self.melee_attack_impact_probability /= len([x for x in self.weapons if x.type == WeaponType.MELEE.value])

    def calculate_model_danger_score(self):
        self.calculate_all_weapon_hit_probability_and_damage()
        # Attack score will be the average a model can deal counting both types of weapon melee and ranged
        self.model_potential_attack_damage = (self.melee_attack_potential_damage +
                                              self.ranged_attack_potential_damage) / 2


class Unit:
    def __init__(self, name, models):
        self.name = name
        self.models = models
        self.is_warlord_in_the_unit = self.is_warlord_in_the_unit()
        self.is_destroyed = False
        self.is_engaged = False
        self.is_unit_visible = self.check_unit_visibility()
        self.has_been_deployed = False
        self.targeted_enemy_unit_to_chase = None
        self.unit_initial_force = len(self.models)
        self.unit_potential_damage = None
        self.unit_potential_salvation = None
        self.unit_leadership = None
        self.unit_objective_control = None
        self.unit_survivability = None
        self.unit_total_score = None
        self.unit_polygon = None
        self.unit_centroid = None
        # Calculate all the unit attributes
        self.update_unit_total_score()

        if self.is_warlord_in_the_unit:
            self.name = f'{Fore.MAGENTA}{bold_on}{self.name} (WL){bold_off}'

    def get_unit_centroid(self):
        # Get the centroid of the unit's polygon or the position of the single model
        self.form_unit_polygon()
        polygon_or_point = self.unit_polygon
        if isinstance(polygon_or_point, Polygon) and not polygon_or_point.is_empty:
            centroid = polygon_or_point.centroid
            self.unit_centroid = centroid
        elif isinstance(polygon_or_point, Point):
            self.unit_centroid = polygon_or_point
        else:
            self.unit_centroid = None

    def calculate_unit_potential_attack_damage(self):
        self.unit_potential_damage = sum(model.model_potential_attack_damage for model in self.models if model.is_alive)

    def calculate_salvation_chance(self):
        self.unit_potential_salvation = sum(model.model_potential_salvation for model in self.models if model.is_alive)

    def calculate_unit_leadership(self):
        self.unit_leadership = sum(model.leadership for model in self.models if model.is_alive) / len(self.models)

    def calculate_unit_objective_control(self):
        self.unit_objective_control = sum(model.objective_control for model in self.models if model.is_alive)

    def calculate_unit_survivability(self):
        self.unit_survivability = sum(model.wounds * model.model_potential_salvation for model in self.models
                                      if model.is_alive)

    def check_unit_visibility(self):
        is_visible = True in [model.is_visible for model in self.models]
        return is_visible

    def deploy_unit_in_zone(self, board, zone_to_deploy):
        board.place_unit(zone_to_deploy, self)
        self.has_been_deployed = True
        # Now that unit has been deployed, calculate its polygon
        self.get_unit_centroid()

    def form_unit_polygon(self):
        # Creates unit's polygon from models position
        model_coordinates = [model.position for model in self.models if model.is_alive]
        if len(model_coordinates) == 1:
            # There is only 1 model in the unit, return its position
            self.unit_polygon = Point(model_coordinates[0])
        elif model_coordinates:
            self.unit_polygon = Polygon([(point.x, point.y) for point in model_coordinates])
        else:
            self.unit_polygon = None

    def get_unit_movement(self):
        return int(self.models[0].movement.replace('"', ''))

    def is_warlord_in_the_unit(self):
        is_warlord = True in [model.is_warlord for model in self.models]
        return is_warlord

    def is_within_engagement_range(self, position):
        # Define an engagement range (e.g., 1 unit)
        engagement_range = 1
        for enemy_model in self.targeted_enemy_unit_to_chase.models:
            if enemy_model.is_alive and position.distance(enemy_model.position) < engagement_range:
                return True
        return False

    def is_position_occupied(self, board_map, position):
        return not board_map.is_cell_empty(position)

    def move_towards_target(self, board_map):
        if not self.targeted_enemy_unit_to_chase.is_destroyed:
            target_position = self.targeted_enemy_unit_to_chase.unit_centroid

            for model in self.models:
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

                    if not self.is_within_engagement_range(new_position) and not self.is_position_occupied(board_map,
                                                                                                           new_position):
                        self.update_model_position(board_map, model, new_position)
                    else:
                        # Find nearest free position if the current one is occupied or within engagement range
                        nearest_free_position = self.find_nearest_free_position(board_map, new_position)
                        if nearest_free_position:
                            self.update_model_position(board_map, model, nearest_free_position)

            self.get_unit_centroid()
        else:
            print("No targeted enemy...")

    def find_nearest_free_position(self, board_map, position):
        # Breadth-first search to find the nearest free position
        from collections import deque
        visited = set()
        queue = deque([position])
        while queue:
            current_position = queue.popleft()
            if not self.is_position_occupied(board_map, current_position) and not self.is_within_engagement_range(
                    current_position):
                return current_position
            visited.add(current_position)
            adjacent_points = get_adjacent_points(current_position)
            for point in adjacent_points:
                if point not in visited and 0 <= point.x < board_map.map_configuration.wide and 0 <= point.y < board_map.map_configuration.large:
                    queue.append(point)
        return None

    def update_model_position(self, board_map, model, new_position):
        board_map.map_configuration.clear_model(model.position)
        model.position = new_position
        board_map.map_configuration.set_model(new_position, model)

    def set_target(self, enemy_unit):
        self.targeted_enemy_unit_to_chase = enemy_unit

    def update_unit_total_score(self):
        # Recalculate everything in case of model's fainted
        self.calculate_unit_potential_attack_damage()
        self.calculate_salvation_chance()
        self.calculate_unit_leadership()
        self.calculate_unit_objective_control()
        self.calculate_unit_survivability()
        # Formula for knowing how challenging a unit is by getting the potential damage it can deal and salvation
        self.unit_total_score = (self.unit_potential_damage * 0.4 +
                                 self.unit_potential_salvation * 0.25 +
                                 self.unit_leadership * 0.1 +
                                 self.unit_objective_control * 0.1 +
                                 self.unit_survivability * 0.15)


class Army:
    def __init__(self):
        self.warlord = None
        self.units = list()
        self.army_total_score = None

    def add_unit_into_army(self, unit):
        self.units.append(unit)

    def are_there_units_still_to_be_deployed(self):
        return self.check_units_left_to_deploy() > 0

    def calculate_danger_score(self):
        self.army_total_score = sum(unit.unit_total_score for unit in self.units if not unit.is_destroyed)

    def check_units_left_to_deploy(self):
        units_left_to_deploy = 0
        for unit in self.units:
            if not unit.has_been_deployed:
                units_left_to_deploy += 1
        return units_left_to_deploy

    def get_unit_to_place(self):
        if self.check_units_left_to_deploy() > 0:
            for unit in self.units:
                if not unit.has_been_deployed:
                    return unit

    def move_units(self, position):
        for unit in self.units:
            if not unit.is_destroyed:
                unit.move_towards_target()

    def set_warlord(self, warlord):
        self.warlord = warlord

    def target_enemies(self, enemy_units):
        for unit in self.units:
            if not unit.is_destroyed and enemy_units:
                # Find the most appropriate enemy unit to target based on proximity and weakness
                target_candidates = [
                    (enemy_unit, get_distance(unit, enemy_unit), enemy_unit.unit_total_score) for enemy_unit in enemy_units
                ]
                if target_candidates:
                    target_candidates.sort(key=lambda x: (x[1], x[2]))
                    closest_and_weakest_enemy = target_candidates[0][0]
                    unit.set_target(closest_and_weakest_enemy)


def get_distance(unit1, unit2):
    pos1 = unit1.models[0].position
    pos2 = unit2.models[0].position
    if pos1 and pos2:
        return ((pos1.x - pos2.x) ** 2 + (pos1.y - pos2.y) ** 2) ** 0.5
    return float('inf')
