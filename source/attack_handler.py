from enums import ResolveAttackSteps
from game_attack_handler import allocate_attack, inflict_damage, hit_roll, saving_throw, wound_roll
from logging_handler import log

"""
    1 - HIT ROLL
    2 - WOUND ROLL
    3 - ALLOCATE ATTACK
    4 - SAVING THROW
    5 - INFLICT DAMAGE
"""


class AttackHandler:
    def __init__(self):
        self.attacker = None
        self.attacking_model = None
        self.attacking_weapon = None
        self.defender = None
        self.defender_unit = None
        self.num_attacks = None
        self.attack_steps = dict()

        # Load attack steps
        self.load_attack_steps()

    def load_attack_steps(self):
        attack_steps = {
            ResolveAttackSteps.HIT_ROLL.name: hit_roll,
            ResolveAttackSteps.WOUND_ROLL.name: wound_roll,
            ResolveAttackSteps.ALLOCATE_ATTACK.name: allocate_attack,
            ResolveAttackSteps.SAVING_THROW.name: saving_throw,
            ResolveAttackSteps.INFLICT_DAMAGE.name: inflict_damage,
        }
        for step_name, function in attack_steps.items():
            self.attack_steps[step_name] = {
                'main_function': function
            }

    def do_attack(self):
        attacks_for_next_step = self.num_attacks
        critical_ones = 0
        for step_name in self.attack_steps:
            attack_step = self.attack_steps[step_name]
            attacks_for_next_step, critical_ones = self.execute_attack_step(step_name, attack_step,
                                                                            attacks_for_next_step, critical_ones)
            if not attacks_for_next_step + critical_ones:
                # There is not a single hit, just stop
                break

    def execute_attack_step(self, step_name, attack_step, num_attacks, critical):
        current_step = attack_step['main_function']
        step_name = step_name.replace("_", " ").title().upper()
        log(f"\t\t----- ----- ----- {step_name}(s) ----- ----- -----",
            True)

        attacks_for_next_step, critical_ones = current_step(self.attacker, self.defender, self.attacking_model,
                                                            self.defender_unit, self.attacking_weapon, num_attacks,
                                                            critical)
        return attacks_for_next_step, critical_ones

    def set_new_attack(self, attacker, defender, attacks):
        self.attacker = attacker
        self.attacking_model = attacks['attacker']
        self.attacking_weapon = attacks['weapon']
        self.defender = defender
        self.defender_unit = attacks['target']
        self.num_attacks = attacks['count']
