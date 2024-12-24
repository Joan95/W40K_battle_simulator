
class KillingReportHandler:
    def __init__(self):
        self.report = dict()

    def add_attacking_unit(self, game_turn, attacking_unit):
        if game_turn not in self.report:
            self.report[game_turn] = dict()

        self.report[game_turn][attacking_unit] = dict()

    def set_new_attack(self):
        pass
