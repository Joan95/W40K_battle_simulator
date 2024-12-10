# Constants for bold text
BOLD_ON = "\033[1m"
BOLD_OFF = "\033[0m"


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
        self.army_total_score = 0
        for unit in self.get_units_alive():
            unit.update_unit_total_score()
            self.army_total_score += unit.unit_total_score

    def check_units_left_to_deploy(self):
        """Check and count units left to be deployed."""
        return sum(1 for unit in self.units if not unit.has_been_deployed)

    def get_units_alive(self):
        return [unit for unit in self.units if not unit.is_destroyed]

    def get_unit_to_place(self):
        if self.check_units_left_to_deploy() > 0:
            for unit in self.units:
                if not unit.has_been_deployed:
                    return unit

    def target_enemies(self, enemy_units):
        if not enemy_units:
            return

        for unit in self.units:
            if not unit.is_destroyed:
                # Find the most appropriate enemy unit to target based on proximity and weakness
                target_candidates = [
                    (enemy_unit, get_distance(unit, enemy_unit), enemy_unit.unit_total_score) for enemy_unit in
                    enemy_units
                ]
                if target_candidates:
                    # Optionally adjust the sorting criteria or add weights
                    target_candidates.sort(key=lambda x: (x[1], x[2]))
                    closest_and_weakest_enemy = target_candidates[0][0]
                    unit.set_target(closest_and_weakest_enemy)


def get_distance(unit1, unit2):
    pos1 = unit1.models[0].position
    pos2 = unit2.models[0].position
    if pos1 and pos2:
        return ((pos1.x - pos2.x) ** 2 + (pos1.y - pos2.y) ** 2) ** 0.5
    return float('inf')
