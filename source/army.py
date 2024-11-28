
class Army:
    def __init__(self):
        self.warlord = None
        self.units = list()
        self.models = list()

    def add_unit_into_army(self, unit):
        self.units.append(unit)

    def add_model_into_army(self, model):
        self.models.append(model)

    def set_warlord(self, warlord):
        self.warlord = warlord

    def move_unit(self, position):
        pass
