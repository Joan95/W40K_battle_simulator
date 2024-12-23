from colorama import Fore
from enums import AttackStyle
from logging_handler import log
from shapely.geometry import LineString, Polygon, Point

# Constants for bold text
BOLD_ON = "\033[1m"
BOLD_OFF = "\033[0m"



class Unit:
    def __init__(self, name, models):
        self.raw_name = name
        self.name = name

        self.battle_shock_passed = True
        self.is_alive = True
        self.is_engaged = False
        self.is_unit_visible = True
        self.is_warlord_in_the_unit = False
        self.has_been_deployed = False
        self.has_advanced = False
        self.has_moved = False
        self.has_shoot = False
        self.models = models
        self.targeted_enemy_unit = None
        self.unit_centroid = None
        self.unit_initial_force = len(self.models)
        self.unit_leadership = None
        self.unit_preferred_attack_style = None
        self.unit_polygon = None
        self.unit_potential_melee_damage = None
        self.unit_potential_ranged_damage = None
        self.unit_potential_salvation = None
        self.unit_objective_control = None
        self.unit_survivability = None
        self.unit_threat_level = None

        # Calculate its score
        self.check_if_warlord_in_unit()
        self.set_unit_preferred_attack_style()
        self.update_unit_total_score()

        if self.is_warlord_in_the_unit:
            self.name = f'{Fore.MAGENTA}{BOLD_ON}{self.raw_name} (WL){BOLD_OFF}'

    def calculate_unit_potential_damages(self):
        if self.get_models_alive():
            self.unit_potential_melee_damage = sum(model.model_potential_damage_melee_attack *
                                                   model.model_impact_probability_melee_attack
                                                   for model in self.get_models_alive()) / len(self.get_models_alive())
            self.unit_potential_ranged_damage = sum(model.model_potential_damage_ranged_attack *
                                                    model.model_impact_probability_ranged_attack
                                                    for model in self.get_models_alive()) / len(self.get_models_alive())
        else:
            self.unit_potential_melee_damage = 0
            self.unit_potential_ranged_damage = 0

    def calculate_unit_salvation_chance(self):
        self.unit_potential_salvation = sum(model.model_potential_salvation for model in self.get_models_alive()) \
                                        / len(self.get_models_alive())

    def calculate_unit_leadership(self):
        self.unit_leadership = sum(model.leadership for model in self.get_models_alive()) / len(self.models)

    def calculate_unit_objective_control(self):
        # Unit only has some objective control if it has passed the moral check, performed when unit current
        # members are lower than half of its initial force
        if self.battle_shock_passed:
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
        self.is_warlord_in_the_unit = any(model.is_warlord for model in self.models)

    def do_moral_check(self, value):
        pass

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
        if alive_models:
            return min(alive_models, key=lambda model: model.priority_to_die)
        else:
            return None

    def get_models_alive(self):
        models_left = [model for model in self.models if model.is_alive]
        if not models_left:
            log(f'[UNIT][{self.name}] has been completely destroyed')
            self.is_alive = False
        return models_left

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

    def move_towards_target(self, board_map):
        if self.targeted_enemy_unit.is_alive:
            if self.unit_preferred_attack_style == AttackStyle.ONLY_MELEE_ATTACK.name:
                # Unit is worth to lose shoot phase for advancing
                if (get_distance(self, self.targeted_enemy_unit) > 12):
                    pass

            for model in self.get_models_alive():
                model.move_towards_target(board_map, self.targeted_enemy_unit)

            self.has_moved = True
            self.calculate_unit_centroid()

    def set_unit_preferred_attack_style(self):
        """
        Sets the unit's preferred attack style based on the distribution of model preferences.
        Determines the style as MELEE, RANGED, or BALANCED based on percentage thresholds.
        """
        # Initialize counts for each attack style
        preferred_attack_style_count = {
            AttackStyle.ONLY_MELEE_ATTACK.name: 0,
            AttackStyle.MELEE_ATTACK.name: 0,
            AttackStyle.BALANCED_ATTACK.name: 0,
            AttackStyle.RANGED_ATTACK.name: 0,
            AttackStyle.ONLY_RANGED_ATTACK.name: 0,
        }

        # Count each model's preferred attack style
        for model in self.models:
            if model.model_preferred_attack_style in preferred_attack_style_count:
                preferred_attack_style_count[model.model_preferred_attack_style] += 1

        # Calculate percentages
        total_models = len(self.models)
        style_percentages = {
            style: (count / total_models) * 100
            for style, count in preferred_attack_style_count.items()
        }

        # Determine the unit's preferred attack style based on thresholds
        only_melee_percent = style_percentages[AttackStyle.ONLY_MELEE_ATTACK.name]
        melee_percent = style_percentages[AttackStyle.MELEE_ATTACK.name]
        balanced_percent = style_percentages[AttackStyle.BALANCED_ATTACK.name]
        ranged_percent = style_percentages[AttackStyle.RANGED_ATTACK.name]
        only_ranged_percent = style_percentages[AttackStyle.ONLY_RANGED_ATTACK.name]

        if only_melee_percent > 80:
            self.unit_preferred_attack_style = AttackStyle.ONLY_MELEE_ATTACK.name
        elif only_ranged_percent > 80:
            self.unit_preferred_attack_style = AttackStyle.ONLY_RANGED_ATTACK.name
        elif melee_percent > 60:
            self.unit_preferred_attack_style = AttackStyle.MELEE_ATTACK.name
        elif ranged_percent > 60:
            self.unit_preferred_attack_style = AttackStyle.RANGED_ATTACK.name
        else:
            self.unit_preferred_attack_style = AttackStyle.BALANCED_ATTACK.name

        # Log the result for debugging
        log(f"[UNIT][{self.name}] Preferred Attack Style: {self.unit_preferred_attack_style} "
            f"(Only Melee: {only_melee_percent:.2f}%, Melee: {melee_percent:.2f}%, "
            f"Balanced: {balanced_percent:.2f}%, "
            f"Ranged: {ranged_percent:.2f}%, Only Ranged: {only_ranged_percent:.2f}%)")

    def set_unit_target(self, enemy_unit):
        self.targeted_enemy_unit = enemy_unit

    def start_new_turn(self):
        self.has_advanced = False
        self.has_moved = False
        self.has_shoot = False
        self.battle_shock_passed = True
        for model in self.models:
            model.start_new_turn()

    def unit_deployed(self):
        log(f'\t\t[UNIT] [{self.raw_name}] deployed!')
        self.has_been_deployed = True
        # Now that unit has been deployed, calculate its polygon
        self.calculate_unit_centroid()

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

        # To apply calculation for models left in the unit,
        # it is not the same to have the initial force than having its half
        remaining_models = len(self.get_models_alive()) / self.unit_initial_force

        # Set threat level
        self.unit_threat_level = self.unit_threat_level * warlord_multiplier * remaining_models


def get_distance(unit1, unit2):
    pos1 = unit1.models[0].position
    pos2 = unit2.models[0].position
    if pos1 and pos2:
        return ((pos1.x - pos2.x) ** 2 + (pos1.y - pos2.y) ** 2) ** 0.5
    return float('inf')
