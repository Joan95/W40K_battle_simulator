from enums import AttackSteps
from logging_handler import log


class WeaponAbility:
    def __init__(self, name):
        self.name = name
        self.attack_step = None
        self.model = None
        self.weapon = None
        self.number_of_extra_attacks = None
        self.number_of_extra_hits = None
        self.attack_modifier = None
        self.impact_roll_modifier = None
        self.generate_critics = False
        self.can_be_applied = False

    def check_for_weapon_ability(self, weapon, attack_step, model, enemy_target, critics):
        self.attack_step = attack_step
        self.model = model
        self.weapon = weapon
        self.number_of_extra_attacks = 0
        self.number_of_extra_hits = 0
        self.impact_roll_modifier = 0
        self.generate_critics = False
        self.can_be_applied = False
        ability_name = self.name

        # Define a dictionary where keys are abilities and values are their handler functions
        ability_handlers = {
            'Anti-infantry 4': lambda: self.handle_anti_infantry_ability(4),
            'Anti-monster 4': lambda: self.handle_anti_monster_ability(4),
            'Anti-vehicle 3': lambda: self.handle_anti_vehicle_ability(3),
            'Anti-vehicle 4': lambda: self.handle_anti_vehicle_ability(4),
            'Blast': lambda: self.handle_blast_ability(enemy_target),
            'Devastating Wounds': lambda: self.handle_devastating_wounds_ability(),
            'Extra Attacks': lambda: self.handle_extra_attacks_ability(),
            'Heavy': lambda: self.handle_heavy_ability(),
            'Pistol': lambda: self.handle_pistol_ability(),
            'Precision': lambda: self.handle_precision_ability(),
            'Psychic': lambda: self.handle_psychic_ability(),
            'Rapid Fire 1': lambda: self.handle_rapid_fire_ability(1),
            'Rapid Fire 2': lambda: self.handle_rapid_fire_ability(2),
            'Sustained Hits 1': lambda: self.handle_sustained_hits_ability(1, critics),
            'Sustained Hits 2': lambda: self.handle_sustained_hits_ability(2, critics),
            'Twin-linked': lambda: self.handle_twin_linked_ability(),
        }

        # Get the corresponding handler function for the ability
        handler = ability_handlers.get(ability_name)

        if handler:
            # Execute the handler and get the modifier
            handler()
        else:
            log(f'[WARNING] Unknown weapon ability: {self.name}')

    def handle_anti_infantry_ability(self, x):
        pass

    def handle_anti_monster_ability(self, x):
        pass

    def handle_anti_vehicle_ability(self, x):
        log(f'[{self.model.name}] applies ANTI-VEHICLE ability: improved effectiveness against vehicles.')
        # Implement anti-vehicle logic here
        return None

    def handle_blast_ability(self, enemy_target):
        # Ability only applicable in HIT_ROLL step
        if self.attack_step == AttackSteps.HIT_ROLL.name:
            num_enemy_models_alive = len(enemy_target.get_models_alive())
            if len(enemy_target.get_models_alive()) >= 5:
                modifier = int(num_enemy_models_alive / 5)
                log(f'[{self.model.name}][{self.weapon.name}][{self.name}] ability: additional attacks against large '
                    f'units. [{enemy_target.name}] has {num_enemy_models_alive} models, '
                    f'number of attack(s) modifier +{modifier}')
                self.number_of_extra_attacks += modifier
                self.can_be_applied = True

    def handle_devastating_wounds_ability(self):
        pass

    def handle_extra_attacks_ability(self):
        pass

    def handle_heavy_ability(self):
        # Ability only applicable in HIT_ROLL step
        if self.attack_step == AttackSteps.HIT_ROLL.name:
            if not self.model.has_moved_this_turn():
                log(f'[{self.model.name}] did not move this turn, applying HEAVY ability: +1 to impact roll.')
                self.impact_roll_modifier += 1
                self.can_be_applied = True

    def handle_pistol_ability(self):
        pass

    def handle_precision_ability(self):
        pass

    def handle_psychic_ability(self):
        pass

    def handle_rapid_fire_ability(self, modifier):
        # Ability only applicable in HIT_ROLL step
        if self.attack_step == AttackSteps.HIT_ROLL.name:
            # Check for distance between model and enemy unit
            weapon_range = self.weapon.get_weapon_range_attack()
            distance_to_target = self.weapon.target_distance
            if weapon_range / 2 >= distance_to_target:
                log(f'[{self.model.name}][{self.weapon.name}][{self.name}] ability: weapon range {weapon_range}", '
                    f'distance to target {distance_to_target}". '
                    f'Applying [{self.name}] ability: +{modifier} attack(s).')
                self.number_of_extra_attacks += modifier
                self.can_be_applied = True

    def handle_sustained_hits_ability(self, x, num_of_critic_hits):
        # Ability only applicable in WOUND_ROLL step
        if self.attack_step == AttackSteps.WOUND_ROLL.name:
            if num_of_critic_hits:
                log(f'[{self.model.name}][{self.weapon.name}][{self.name}] ability: additional wounds when critical hit(s).'
                    f' Number of critical hits #{num_of_critic_hits} generated +{x * num_of_critic_hits} attack(s).')
                self.number_of_extra_hits += x * num_of_critic_hits
                self.can_be_applied = True

    def handle_twin_linked_ability(self):
        pass
