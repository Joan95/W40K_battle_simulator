# Constants for bold text
BOLD_ON = "\033[1m"
BOLD_OFF = "\033[0m"


class Army:
    def __init__(self):
        self.warlord = None
        self.units = list()
        self.army_threat_level = None

    def add_unit_into_army(self, unit):
        self.units.append(unit)

    def are_there_units_still_to_be_deployed(self):
        return self.check_units_left_to_deploy() > 0

    def calculate_danger_score(self):
        self.army_threat_level = 0
        for unit in self.get_units_alive():
            unit.update_unit_total_score()
            self.army_threat_level += unit.get_unit_threat_level()

    def check_units_left_to_deploy(self):
        """Check and count units left to be deployed."""
        return sum(1 for unit in self.units if not unit.has_been_deployed)

    def get_unit_to_deploy(self):
        if self.check_units_left_to_deploy() > 0:
            for unit in self.units:
                if not unit.has_been_deployed:
                    return unit

    def get_units_alive(self):
        return [unit for unit in self.units if unit.is_alive]

    def get_units_available_for_advancing(self):
        return [unit for unit in self.get_units_alive() if not unit.is_unit_engaged()]

    def get_units_available_for_charging(self):
        return [unit for unit in self.get_units_alive() if not unit.is_unit_engaged() and not unit.has_unit_advanced()]

    def get_units_available_for_moving(self):
        return [unit for unit in self.get_units_alive() if not unit.is_unit_engaged()]

    def get_units_available_for_shooting(self):
        return [unit for unit in self.get_units_alive() if not unit.is_unit_engaged() and not unit.has_unit_advanced()]

    def get_threat_level(self):
        return self.army_threat_level
