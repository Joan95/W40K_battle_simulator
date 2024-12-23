import battlefield
from enums import AttackStyle, ModelPriority, WeaponType
from logging_handler import *
from shapely.geometry import Point

MAX_THROW_D6 = 6
# Constants for bold text
BOLD_ON = "\033[1m"
BOLD_OFF = "\033[0m"


def is_model_within_engagement_range(target_enemy, position):
    # Define an engagement range (e.g., 1 unit)
    engagement_range = 1
    for enemy_model in target_enemy.models:
        if enemy_model.is_alive and position.distance(enemy_model.position) < engagement_range:
            return True
    return False


def find_nearest_free_position(board_map, target_enemy, position):
    from collections import deque

    visited = set()  # Track visited cells
    queue = deque([position])  # Initialize queue with the starting position

    while queue:
        current_position = queue.popleft()

        # Check if the current position is valid
        if board_map.is_cell_empty(current_position) and \
                not is_model_within_engagement_range(target_enemy, current_position):
            return current_position

        visited.add(current_position)

        # Get adjacent points and filter out invalid ones
        adjacent_points = [
            point for point in battlefield.get_adjacent_points(current_position)
            if point not in visited and
               0 <= point.x < board_map.map_configuration.wide and
               0 <= point.y < board_map.map_configuration.large
        ]

        queue.extend(adjacent_points)

    # If no free position is found, return None
    return None


def update_model_position(board_map, model, new_position):
    """Update the model's position on the board."""
    if model.position:
        board_map.map_configuration.clear_model(model.position)
    board_map.map_configuration.set_model(new_position, model)


class ModelKeywords:
    def __init__(self, name):
        self.name = name


class Model:
    def __init__(self, name, attributes_tuple, weapons, keywords, is_warlord=False, more_than_one=False):
        self.name = name
        self.movement = attributes_tuple[0]
        self.toughness = attributes_tuple[1]
        self.salvation = attributes_tuple[2]
        self.wounds = attributes_tuple[3]
        self.leadership = attributes_tuple[4]
        self.objective_control = attributes_tuple[5]
        self.invulnerable_save = attributes_tuple[6]
        self.feel_no_pain = attributes_tuple[7]

        self.keywords = list(keywords)
        self.weapons = list(weapons)

        self.can_be_disengaged_from_unit = 'CHARACTER' in keywords
        self.has_moved = False
        self.is_warlord = is_warlord
        self.is_alive = True
        self.is_visible = True
        self.is_wounded = False
        self.model_impact_probability_melee_attack = 0
        self.model_impact_probability_ranged_attack = 0
        self.model_melee_score = 0
        self.model_potential_damage_melee_attack = 0
        self.model_potential_damage_ranged_attack = 0
        self.model_potential_salvation = self.calculate_model_defence_score()
        self.model_preferred_attack_style = None
        self.model_ranged_score = 0
        self.position = None
        self.priority_to_die = self.set_model_priority_to_die(more_than_one)

        # Calculate its score
        self.set_model_preferred_attack_style()
        self.description = self.set_description()

    def calculate_model_defence_score(self):
        base_chance_of_defence = (MAX_THROW_D6 - (int(self.salvation) - 1)) / 6
        chance_of_defence = base_chance_of_defence
        if self.feel_no_pain:
            # If there's a chance to ignore damage with "Feel No Pain"
            chance_of_defence += (1 - base_chance_of_defence) * (MAX_THROW_D6 - (int(self.feel_no_pain) - 1)) / 6
        return chance_of_defence

    def do_feel_no_pain(self, dices, wounds):
        log(f'[MODEL][{self.name}] has feel no pain at {self.feel_no_pain}+')
        dices.roll_dices('{}D6'.format(wounds))
        saved_wounds = 0
        for dice in dices.last_roll_dice_values:
            if dice >= self.feel_no_pain:
                saved_wounds += 1
        if saved_wounds:
            log(f'[MODEL][{self.name}] saved {saved_wounds}')
        else:
            log(f'[MODEL][{self.name}] has not saved anything, will receive entire attack')
        return wounds - saved_wounds

    def get_description(self):
        return self.description

    def get_invulnerable_save(self):
        return self.invulnerable_save

    def get_model_melee_weapons_hit_probability_and_damage(self):
        melee_weapons = self.get_model_weapons_melee()
        total_melee_hit_probability = 0
        total_melee_damage = 0

        if not melee_weapons:
            self.model_impact_probability_melee_attack = 0
            self.model_potential_damage_melee_attack = 0
            return

        for weapon in melee_weapons:
            num_attacks = weapon.get_weapon_max_num_attacks()
            # Cumulative hit probability: Chance of at least one hit over num_attacks
            total_melee_hit_probability += 1 - (1 - weapon.weapon_hit_probability) ** num_attacks
            # Cumulative damage: number of attacks * average damage per attack
            total_melee_damage += weapon.weapon_potential_damage_per_attack * num_attacks

        # Average the cumulative hit probability across all weapons
        self.model_impact_probability_melee_attack = total_melee_hit_probability / len(melee_weapons)
        # Average the total damage across all weapons
        self.model_potential_damage_melee_attack = total_melee_damage / len(melee_weapons)

    def get_model_ranged_weapons_hit_probability_and_damage(self):
        ranged_weapons = self.get_model_weapons_ranged()
        total_ranged_hit_probability = 0
        total_ranged_damage = 0

        if not ranged_weapons:
            self.model_impact_probability_ranged_attack = 0
            self.model_potential_damage_ranged_attack = 0
            return

        for weapon in ranged_weapons:
            num_attacks = weapon.get_weapon_max_num_attacks()
            # Cumulative hit probability: Chance of at least one hit over num_attacks
            total_ranged_hit_probability += 1 - (1 - weapon.weapon_hit_probability) ** num_attacks
            # Cumulative damage: number of attacks * average damage per attack
            total_ranged_damage += weapon.weapon_potential_damage_per_attack * num_attacks

        # Average the cumulative hit probability across all ranged weapons
        self.model_impact_probability_ranged_attack = total_ranged_hit_probability / len(ranged_weapons)
        # Average the total damage across all ranged weapons
        self.model_potential_damage_ranged_attack = total_ranged_damage / len(ranged_weapons)

    def get_model_priority_to_die(self):
        return self.priority_to_die

    def get_model_salvation(self):
        log(f'\t\t[MODEL][{self.name}] has salvation of {self.salvation}+ ')
        return self.salvation

    def get_model_toughness(self):
        log(f'\t\t[MODEL][{self.name}] has toughness of {self.toughness}')
        return self.toughness

    def get_model_weapons_hit_probability_and_damage(self):
        self.get_model_melee_weapons_hit_probability_and_damage()
        self.get_model_ranged_weapons_hit_probability_and_damage()

    def get_model_weapons_melee(self):
        return [weapon for weapon in self.weapons if weapon.type == WeaponType.MELEE.name]

    def get_model_weapons_ranged(self):
        return [weapon for weapon in self.weapons if weapon.type == WeaponType.RANGED.name]

    def has_feel_no_pain(self):
        if self.feel_no_pain:
            return True
        else:
            return False

    def has_moved_this_turn(self):
        return self.has_moved

    def move_to(self, position):
        log(f'\t\t\tModel [{self.name}] set at position {int(self.position.x), int(self.position.y)}')
        self.position = position
        self.has_moved = True

    def move_towards_target(self, board_map, target_enemy, advance_move):
        # Get target position and current position
        target_position = target_enemy.get_unit_centroid()
        if self.position:
            # Calculate direction vector
            direction_x = target_position.x - self.position.x
            direction_y = target_position.y - self.position.y
            total_distance = Point(direction_x, direction_y).distance(Point(0, 0))

            # Calculate movement range (account for advance move if applicable)
            movement_range = int(self.movement.replace('"', '')) + (advance_move if advance_move else 0)
            if total_distance > 0:
                step = min(movement_range, int(total_distance))
                movement_x = step * (direction_x / total_distance)
                movement_y = step * (direction_y / total_distance)
            else:
                movement_x = movement_y = 0

            # Calculate new position
            new_position = Point(round(self.position.x + movement_x), round(self.position.y + movement_y))
            new_position = board_map.clamp_position_within_boundaries(new_position)

            # Check if the new position is valid
            if not is_model_within_engagement_range(target_enemy, new_position) and \
                    board_map.is_cell_empty(new_position):
                # Move to the new position directly
                board_map.map_configuration.clear_model(self.position)
                board_map.map_configuration.set_model(new_position, self)
                self.move_to(new_position)
            else:
                # Find the nearest valid free position
                nearest_free_position = find_nearest_free_position(board_map, target_enemy, new_position)
                if nearest_free_position:
                    board_map.map_configuration.clear_model(self.position)
                    board_map.map_configuration.set_model(nearest_free_position, self)
                    self.move_to(nearest_free_position)
                else:
                    # Stay in the current position if no valid position is found
                    log(f"[MOVEMENT] Model {self.name} cannot move towards target at {target_position} from {self.position}.")

    def receive_damage(self, wounds):
        if wounds:
            self.is_wounded = True
            self.wounds -= wounds
            if self.wounds <= 0:
                self.is_alive = False
                log(f'[MODEL][{self.name}] receives {wounds} wound(s) and dies honorably')
                return True
            else:
                log(f'[MODEL][{self.name}] receives {wounds} wound(s). Remaining wound(s) {self.wounds}')
        return False

    def set_description(self):
        lines = [
            f"----- ----- ----- ----- ----- ----- ----- ----- -----",
            f"\t[{self.name.upper()}]",
            f"\tAttack profile: {self.model_preferred_attack_style}",
            f"\tM\tT\tSV\tW\tLD\tOC",
            f"\t{self.movement}\t{self.toughness}\t{self.salvation}\t"
            f"{self.wounds}\t{self.leadership}\t{self.objective_control}",
        ]
        if self.invulnerable_save:
            lines.append(f"\tINVULNERABLE SAVE\t{self.invulnerable_save}")
        lines.append(f"\tKEYWORDS:\n\t\t[{', '.join(self.keywords)}]")
        lines.extend(weapon.get_description() for weapon in self.weapons)
        description = "\n".join(lines)
        log(description)
        return description

    def set_model_preferred_attack_style(self):
        # First, calculate the hit probability and potential damage for all the weapons
        self.get_model_weapons_hit_probability_and_damage()

        # Calculate scores for melee and ranged attacks
        self.model_melee_score = self.model_impact_probability_melee_attack * self.model_potential_damage_melee_attack
        self.model_ranged_score = \
            self.model_impact_probability_ranged_attack * self.model_potential_damage_ranged_attack

        # Define thresholds
        dominance_threshold = 4  # Minimum difference for a style to dominate
        balanced_threshold = 0.75  # Threshold for scores being close enough to be balanced

        # Determine preferred attack style
        if self.model_melee_score >= self.model_ranged_score + dominance_threshold:
            self.model_preferred_attack_style = AttackStyle.ONLY_MELEE_ATTACK.name
        elif self.model_ranged_score >= self.model_melee_score + dominance_threshold:
            self.model_preferred_attack_style = AttackStyle.ONLY_RANGED_ATTACK.name
        elif abs(self.model_melee_score - self.model_ranged_score) <= balanced_threshold:
            self.model_preferred_attack_style = AttackStyle.BALANCED_ATTACK.name
        elif self.model_melee_score > self.model_ranged_score:
            self.model_preferred_attack_style = AttackStyle.MELEE_ATTACK.name
        else:
            self.model_preferred_attack_style = AttackStyle.RANGED_ATTACK.name

        # Log the result for debugging
        log(f'[MODEL][{self.name}] has a melee_score of [{self.model_melee_score}] '
            f'and ranged_score of [{self.model_ranged_score}]. Preferred attack style: '
            f'{self.model_preferred_attack_style}')

    def set_model_priority_to_die(self, more_than_one):
        if self.is_warlord:
            return ModelPriority.WARLORD.value
        elif 'EPIC HERO' in self.keywords:
            return ModelPriority.EPIC_HERO.value
        elif 'CHARACTER' in self.keywords:
            return ModelPriority.CHARACTER.value
        else:
            if more_than_one:
                # This is unit basic model
                return ModelPriority.UNIT_MODEL.value
            else:
                # This is boss unit basic model
                return ModelPriority.UNIT_BOSS.value

    def start_new_turn(self):
        self.has_moved = False
