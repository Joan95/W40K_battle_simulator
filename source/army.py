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
        # Units are considered available for charging when:
        # 1 - Unit has not advanced this turn
        # 2 - Unit has not fell-back this turn
        # 3 - Unit is not engaged
        # 4 - Unit is 12" or less from an enemy unit
        available_charge_units = list()
        available_units = [unit for unit in self.get_units_alive()
                           if not unit.is_unit_engaged() and not unit.has_unit_advanced()]
        for unit in available_units:
            distance_to_target = unit.get_distance_to_target()
            if distance_to_target <= 12:
                available_charge_units.append(unit)
        return available_charge_units

    def get_units_available_for_moving(self):
        return [unit for unit in self.get_units_alive() if not unit.is_unit_engaged()]

    def get_units_available_for_shooting(self):
        # Do not take unit.has_advanced as a parameter for Assault weapons, they can be shoot even if model has
        # advanced this turn
        return [unit for unit in self.get_units_alive() if not unit.is_unit_engaged()]

    def get_threat_level(self):
        return self.army_threat_level
