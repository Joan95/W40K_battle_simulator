from enums import AttackSteps, AttackStrength
from logging_handler import log

"""
    1 - HIT ROLL
    2 - WOUND ROLL
    3 - ALLOCATE ATTACK
    4 - SAVING THROW
    5 - INFLICT DAMAGE
"""


class AttackHandler:
    def __init__(self, boardgame):
        self.attacker = None
        self.attacking_model = None
        self.attacking_weapon = None
        self.boardgame = boardgame
        self.current_attack_function = None
        self.current_step = None
        self.defender = None
        self.defender_unit = None
        self.defender_model = None
        self.num_attacks = None
        self.attack_steps = dict()

        # Load attack steps
        self.load_attack_steps()

    def load_attack_steps(self):
        attack_steps = {
            AttackSteps.HIT_ROLL.name: self.hit_roll,
            AttackSteps.WOUND_ROLL.name: self.wound_roll,
            AttackSteps.ALLOCATE_ATTACK.name: self.allocate_attack,
            AttackSteps.SAVING_THROW.name: self.saving_throw,
            AttackSteps.INFLICT_DAMAGE.name: self.inflict_damage,
        }
        for step_name, function in attack_steps.items():
            self.attack_steps[step_name] = {
                'main_function': function
            }

    def do_attack(self):
        attacks_for_next_step = self.num_attacks
        critical_ones = 0
        for self.current_step in self.attack_steps:
            if self.defender_unit.is_alive:
                self.current_attack_function = self.attack_steps[self.current_step]['main_function']
                attacks_for_next_step, critical_ones = self.execute_attack_step(attacks_for_next_step, critical_ones)
                if not attacks_for_next_step + critical_ones:
                    # There is not a single hit, just stop
                    break
            else:
                log(f'All models in unit {self.defender_unit.name} have died honorably, there are no '
                    f'more models left to allocate more damage')
                break

    def execute_attack_step(self, attacks_for_next_step, critical_ones):
        log(f'\t\t----- ----- ----- {self.current_step.replace("_", " ").title().upper()}(s) ----- ----- -----',
            True)

        attacks_for_next_step, critical_ones = self.current_attack_function(attacks_for_next_step, critical_ones)
        return attacks_for_next_step, critical_ones

    def set_new_attack(self, attacker, defender, attacks):
        self.attacker = attacker
        self.attacking_model = attacks['attacker']
        self.attacking_weapon = attacks['weapon']
        self.defender = defender
        self.defender_unit = attacks['target']
        self.num_attacks = attacks['count']

    def hit_roll(self, num_shoots, critical_attacks):
        # Get weapon number of attacks to do
        log(f'[HIT ROLL(s)] there are #{num_shoots} [{self.attacking_weapon.name}] being shoot. Attack(s) '
            f'{self.attacking_weapon.get_raw_num_attacks()}')

        # At this point, just calculate which weapons might have some abilities
        self.attacking_weapon.handle_weapon_abilities(self.current_step, self.attacking_model,
                                                      self.defender_unit, critical_attacks)

        # Handle num_attacks_modifier: Blast, Rapid Fire X, Heavy ...
        abilities_to_be_applied = list()
        number_of_extra_attacks = 0
        for ability in self.attacking_weapon.abilities:
            if ability.can_be_applied:
                abilities_to_be_applied.append(ability.name)
                number_of_extra_attacks += ability.number_of_extra_attacks

        weapon_num_attacks, weapon_ballistic_skill = self.attacking_weapon.get_num_attacks(self.attacker.dices)
        total_attacks = num_shoots * (weapon_num_attacks + number_of_extra_attacks)

        if abilities_to_be_applied:
            log(f'[HIT ROLL(s)][{self.attacking_weapon.name}][Weapons #{num_shoots} x '
                f'(Attack(s) per Weapon {weapon_num_attacks} + '
                f'([{", ".join(ability for ability in abilities_to_be_applied)}] +{number_of_extra_attacks}))] '
                f'generated a total of #{total_attacks} attack(s) that will success at {weapon_ballistic_skill}+ ')
        else:
            log(f'[HIT ROLL(s)][{self.attacking_weapon.name}][Weapons #{num_shoots} x '
                f'Attack(s) per Weapon {weapon_num_attacks}] generated a total of #{total_attacks} attack(s) that '
                f'will success at {weapon_ballistic_skill}+ ')

        self.attacker.dices.roll_dices(number_of_dices='{}D6'.format(total_attacks))
        hits = self.attacker.dices.last_roll_dice_values
        successful_hits = list()
        critical_hits = 0
        for hit in hits:
            if hit == 6:
                critical_hits += 1
            elif hit >= weapon_ballistic_skill:
                successful_hits.append(hit)
        log(f'[HIT ROLL(s)][{self.attacking_weapon.name}] Basic hit(s) [{len(successful_hits)}], '
            f'Critical hit(s) [{critical_hits}] -> Total hit(s) [{len(successful_hits) + critical_hits}]')
        return len(successful_hits), critical_hits

    def wound_roll(self, successful_hits, critical_hits):
        num_hits = successful_hits + critical_hits
        if num_hits:
            # At this point, just calculate which weapons might have some abilities
            self.attacking_weapon.handle_weapon_abilities(self.current_step, self.attacking_model,
                                                          self.defender_unit, critical_hits)

            # Handle num_attacks_modifier: Blast, Rapid Fire X, Heavy ...
            abilities_to_be_applied = list()
            number_of_extra_hits = 0
            for ability in self.attacking_weapon.abilities:
                if ability.can_be_applied:
                    abilities_to_be_applied.append(ability.name)
                    number_of_extra_hits += ability.number_of_extra_hits

            weapon_strength = self.attacking_weapon.get_strength()

            # Get the enemy unit toughness who will suffer this attack
            enemy_toughness = self.defender_unit.get_unit_toughness()

            if weapon_strength == enemy_toughness:
                weapon_attack_strength = AttackStrength.EQUAL.value
            else:
                if weapon_strength > enemy_toughness:
                    weapon_attack_strength = AttackStrength.WEAK.value
                    if weapon_strength >= enemy_toughness * 2:
                        weapon_attack_strength = AttackStrength.DOUBLE_WEAK.value
                else:
                    weapon_attack_strength = AttackStrength.STRONG.value
                    if weapon_strength * 2 <= enemy_toughness:
                        weapon_attack_strength = AttackStrength.DOUBLE_STRONG.value

            if abilities_to_be_applied:
                log(f'[WOUND ROLL(s)][{self.attacking_weapon.name}] Basic hit(s) #{num_hits} '
                    f'(+{number_of_extra_hits} [{", ".join(ability for ability in abilities_to_be_applied)}]) that '
                    f'will success at {weapon_attack_strength}\'s')
            else:
                log(f'[WOUND ROLL(s)][{self.attacking_weapon.name}] #{num_hits} hit(s) that will success at '
                f'{weapon_attack_strength}\'s')

            self.attacker.dices.roll_dices(number_of_dices='{}D6'.format(num_hits + number_of_extra_hits))
            wounds = self.attacker.dices.last_roll_dice_values
            successful_wounds = list()
            critical_wounds = 0
            for wound in wounds:
                if wound == 6:
                    critical_wounds += 1
                elif wound >= weapon_attack_strength:
                    successful_wounds.append(wound)
            log(f'[WOUND ROLL(s)][{self.attacking_weapon.name}] #{len(successful_wounds)} wound(s), '
                f'#{critical_wounds} critical wounds(s) -> total wound(s) #{len(successful_wounds) + critical_wounds}')
            return len(successful_wounds), critical_wounds
        else:
            log(f'[WOUND ROLL(s)][{self.attacking_weapon.name}] And there\'s no successful hit to be done... [F]')
            return successful_hits, critical_hits

    def allocate_attack(self, successful_wounds, critical_wounds):
        num_wounds = successful_wounds + critical_wounds
        if num_wounds:
            # 3 - Assign attack
            self.defender_model = self.defender_unit.get_next_model_to_die()
            log(f'[ALLOCATE DAMAGE][{self.defender.name}] first model to die will be [{self.defender_model.name}] '
                f'from unit [{self.defender_unit.name}]')
            return successful_wounds, critical_wounds
        else:
            log(f'[WOUND ROLL(s)][{self.attacking_weapon.name}] And there\'s no successful wound to be performed... '
                f'[F]')
            return successful_wounds, critical_wounds

    def saving_throw(self, successful_wounds, critical_wounds):
        model_salvation = self.defender.calculate_model_salvation(self.defender_model,
                                                                  self.attacking_weapon.get_armour_penetration())
        num_wounds = successful_wounds + critical_wounds
        damage = 0
        defended = 0
        self.defender.dices.roll_dices('{}D6'.format(num_wounds))
        for throw in self.defender.dices.last_roll_dice_values:
            if throw < model_salvation:
                damage += 1
            else:
                defended += 1
        log(f'[SAVING THROW(s)][{self.defender_model.name}] has successfully defended #{defended} '
            f'receiving a total of #{damage} damage')
        return damage, 0

    def inflict_damage(self, successful_attacks, critical_attacks):
        # 5 - Allocate damage
        num_wounds = successful_attacks + critical_attacks
        if num_wounds:
            killed_models = list()
            damage = self.attacking_weapon.get_damage(self.attacker.dices)
            for _ in range(num_wounds):
                if self.defender.allocate_damage(self.defender_model, damage):
                    # Model has died remove it from boardgame
                    self.boardgame.kill_model(self.defender_model)
                    killed_models.append(self.defender_model)
                    # Get the very next one to receive damage
                    self.defender_model = self.defender_unit.get_next_model_to_die()
                    if not self.defender_model:
                        log(f'All models in unit {self.defender_unit.name} have died honorably, there are no '
                            f'more models left to allocate more damage')
                        break
            if killed_models:
                self.boardgame.display_board()
        return 0, 0
