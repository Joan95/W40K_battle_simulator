from attack_handler import AttackHandler
from colorama import Fore
from enums import ChargePhase, CommandPhase, FightPhase, GamePhase, MovementPhase, RemainingCombats, ShootingPhase
from logging_handler import log
"""
    WARHAMMER 40K 10th edition:
    1 - COMMAND PHASE
    2 - MOVEMENT PHASE
    3 - SHOOTING PHASE
    4 - CHARGE PHASE
    5 - FIGHT PHASE
"""


class GameHandler:
    def __init__(self, turns, board):
        self.boardgame = board
        self.active_player = None
        self.inactive_player = None
        self.current_phase = None
        self.turns_list = turns
        self.game_turn = 0
        self.phases = dict()
        # Attack resolver handler
        self.resolve_attack = AttackHandler(self.boardgame)

        # If here all the Units have been displayed so the game can start!
        self.boardgame.start_game()

        # Load game phases and configuration
        self.load_game_phases_and_steps()

    def execute_all_phases(self):
        for count, phase_name in enumerate(self.phases, start=1):
            phase = self.phases[phase_name]
            feedback = self.execute_main_phases(phase_name, phase, count)

    def execute_main_phases(self, phase_name, phase_dict, phase_number, upper_phase=None):
        current_phase_function = phase_dict['main_function']
        phase_name = f'#{phase_number} {phase_name.replace("_", " ").title().upper()}'
        if upper_phase:
            phase_name = upper_phase + ' - ' + phase_name
        log(f"[REPORT][TURN #{self.game_turn}] ----- ----- ----- [{self.active_player.name}] "
            f"{phase_name} ----- ----- -----", True)

        feedback = current_phase_function()

        if 'sub_functions' in phase_dict:
            sub_phase_dict = phase_dict['sub_functions']
            sub_phase_loop_finished = False
            while not sub_phase_loop_finished:
                for count, sub_phase_name in enumerate(sub_phase_dict, start=1):
                    sub_phase = sub_phase_dict[sub_phase_name]
                    sub_phase_loop_finished = self.execute_main_phases(sub_phase_name, sub_phase, count)

        return feedback

    def run_game(self):
        for (self.game_turn, (attacker, defender)) in self.turns_list:
            log(f"[REPORT]\n\n\t\t----- ----- ----- ----- ----- Game TURN #{self.game_turn} "
                "----- ----- ----- ----- -----")
            print(f"\t{Fore.LIGHTYELLOW_EX}Game turn [#{self.game_turn}]{Fore.RESET}")

            # Execute Attacker phase
            self.active_player = attacker
            self.inactive_player = defender
            if len(self.active_player.get_units_alive()) > 0:
                log(f'[REPORT][{self.active_player.name}] Units left: {len(self.active_player.get_units_alive())}', True)
                log(f'[REPORT][{self.inactive_player.name}] Units left: {len(self.inactive_player.get_units_alive())}', True)
                log(f'[{self.active_player.name}] danger score of {self.active_player.get_army_threat_level()}', True)
                log(f'[{self.inactive_player.name}] danger score of {self.inactive_player.get_army_threat_level()}',
                    True)
                self.execute_all_phases()
            else:
                log(f"[REPORT] Player {self.active_player.raw_name} has not more units left. End of the game.")
                break

            # Execute Defender phase
            self.active_player = defender
            self.inactive_player = attacker
            if len(self.inactive_player.get_units_alive()) > 0:
                log(f'[REPORT][{self.inactive_player.name}] Units left: {len(self.inactive_player.get_units_alive())}', True)
                log(f'[REPORT][{self.active_player.name}] Units left: {len(self.active_player.get_units_alive())}', True)
                log(f'[{self.inactive_player.name}] danger score of {self.inactive_player.get_army_threat_level()}',
                    True)
                log(f'[{self.active_player.name}] danger score of {self.active_player.get_army_threat_level()}', True)
                self.execute_all_phases()
            else:
                log(f"[REPORT] Player {self.active_player.raw_name} has not more units left. End of the game.")
                break
            print()
        log(f'[{self.active_player.name}] danger score of {self.active_player.get_army_threat_level()}', True)
        log(f'[{self.inactive_player.name}] danger score of {self.inactive_player.get_army_threat_level()}', True)

    def load_game_phases_and_steps(self):
        phase_functions = {
            GamePhase.COMMAND_PHASE.name: self.command_phase,
            GamePhase.MOVEMENT_PHASE.name: self.movement_phase,
            GamePhase.SHOOTING_PHASE.name: self.shooting_phase,
            GamePhase.CHARGE_PHASE.name: self.charge_phase,
            GamePhase.FIGHT_PHASE.name: self.fight_phase
        }

        """
        1 - COMMAND PHASE
            1 - COMMAND
            2 - BATTLE-SHOCK
        """
        command_phase_functions = {
            CommandPhase.COMMAND_STEP.name: {
                'main_function': self.command
            },
            CommandPhase.BATTLE_SHOCK_STEP.name: {
                'main_function': self.battle_shock
            },
        }

        """
        2 - MOVEMENT PHASE
            1 - MOVE UNITS
            2 - REINFORCEMENTS
        """
        movement_phase_functions = {
            MovementPhase.MOVE_UNITS.name: {
                'main_function': self.move_units
            },
            MovementPhase.REINFORCEMENTS.name: {
                'main_function': self.reinforcements
            },
        }

        """
        3 - SHOOTING PHASE
            1 - SELECT ELIGIBLE UNIT
            2 - SELECT TARGETS
            3 - MAKE RANGED ATTACKS
            4 - REPEAT FOR NEXT ELIGIBLE UNIT
        """
        shooting_phase_functions = {
            ShootingPhase.SELECT_ELIGIBLE_UNIT.name: {
                'main_function': self.select_eligible_unit
            },
            ShootingPhase.SELECT_TARGETS.name: {
                'main_function': self.select_targets
            },
            ShootingPhase.MAKE_RANGED_ATTACKS.name: {
                'main_function': self.make_ranged_attacks
            },
            ShootingPhase.REPEAT_FOR_NEXT_ELIGIBLE_UNIT.name: {
                'main_function': self.repeat_for_next_eligible_unit
            },
        }

        """                
        4 - CHARGE PHASE
            1 - SELECT ELIGIBLE UNIT
            2 - SELECT TARGETS
            3 - MAKE CHARGE ROLL
            4 - MAKE CHARGE MOVE
            5 - REPEAT FOR NEXT ELIGIBLE UNIT
        """
        charge_phase_functions = {
            ChargePhase.SELECT_ELIGIBLE_UNIT.name: {
                'main_function': self.select_eligible_unit
            },
            ChargePhase.SELECT_TARGETS.name: {
                'main_function': self.select_targets
            },
            ChargePhase.MAKE_CHARGE_ROLL.name: {
                'main_function': self.make_charge_roll
            },
            ChargePhase.MAKE_CHARGE_MOVEMENT.name: {
                'main_function': self.make_charge_move
            },
            ChargePhase.REPEAT_FOR_NEXT_ELIGIBLE_UNIT.name: {
                'main_function': self.repeat_for_next_eligible_unit
            },
        }

        """
        5 - FIGHT PHASE
            1 - FIGHTS FIRST
            2 - REMAINING COMBATS
                1 - PILE IN
                2 - MAKE MELEE ATTACKS
                3 - CONSOLIDATE
        """
        fight_phase_functions = {
            FightPhase.FIGHTS_FIRST.name: {
                'main_function': self.fight_first
            },
            FightPhase.REMAINING_COMBATS.name: {
                'main_function': self.remaining_combats
            },
        }

        """
        5 - FIGHT PHASE
            1 - FIGHTS FIRST
            2 - REMAINING COMBATS
                1 - PILE IN
                2 - MAKE MELEE ATTACKS
                3 - CONSOLIDATE
        """
        remaining_combats_functions = {
            RemainingCombats.PILE_IN.name: {
                'main_function': self.pile_in
            },
            RemainingCombats.MAKE_MELEE_ATTACKS.name: {
                'main_function': self.make_melee_attacks
            },
            RemainingCombats.CONSOLIDATE.name: {
                'main_function': self.consolidate
            },
        }

        for phase_name, phase_function in phase_functions.items():
            self.phases[phase_name] = {
                'main_function': phase_function
            }

            if phase_name == GamePhase.COMMAND_PHASE.name:
                self.phases[phase_name]['sub_functions'] = command_phase_functions
            if phase_name == GamePhase.MOVEMENT_PHASE.name:
                self.phases[phase_name]['sub_functions'] = movement_phase_functions
            if phase_name == GamePhase.SHOOTING_PHASE.name:
                self.phases[phase_name]['sub_functions'] = shooting_phase_functions
            if phase_name == GamePhase.CHARGE_PHASE.name:
                self.phases[phase_name]['sub_functions'] = charge_phase_functions
            if phase_name == GamePhase.FIGHT_PHASE.name:
                self.phases[phase_name]['sub_functions'] = fight_phase_functions
                self.phases[phase_name]['sub_functions'][FightPhase.REMAINING_COMBATS.name]['sub_functions'] = \
                    remaining_combats_functions

    def command_phase(self):
        """
            1 - COMMAND PHASE
                1 - COMMAND
                2 - BATTLE-SHOCK
        """
        self.current_phase = GamePhase.COMMAND_PHASE.name
        self.active_player.new_turn()
        self.inactive_player.new_turn()
        log(f'[{self.active_player.name}] danger score of {self.active_player.get_army_threat_level()}')
        log(f'[{self.inactive_player.name}] danger score of {self.inactive_player.get_army_threat_level()}')

    def command(self):
        # Now increase command points for each one
        self.active_player.increment_command_points()
        self.inactive_player.increment_command_points()
        return True

    def battle_shock(self):
        for unit in self.active_player.get_units_alive():
            if len(unit.models) < unit.unit_initial_force / 2:
                log(f"[REPORT] Unit {unit.name} at half of its initial force, "
                    f"will have to throw the dices for checking its moral", True)
                self.active_player.roll_dice()
                unit.do_moral_check(self.active_player.last_roll_dice)
        return True

    def movement_phase(self):
        """
            2 - MOVEMENT PHASE
                1 - MOVE UNITS
                2 - REINFORCEMENTS
        """
        self.current_phase = GamePhase.MOVEMENT_PHASE.name
        # Get enemy's alive units
        enemy_units = self.inactive_player.get_units_alive()

        for unit in self.active_player.army.get_units_available_for_moving():
            # Force units to target enemies based on its score
            unit.chase_enemies(enemy_units)
        return True

    def move_units(self):
        for unit in self.active_player.get_units_alive():
            log(f"\t[REPORT][{self.active_player.name}] Moving unit [{unit.name}]")
            unit.move_towards_target(self.active_player.dices, self.boardgame)
        self.boardgame.display_board()
        return True

    def reinforcements(self):
        log(f'[REPORT][{self.active_player.name}] has no more units to be placed. '
            f'Not expecting further reinforcements')
        return True

    def shooting_phase(self):
        """
            3 - SHOOTING PHASE
                1 - SELECT ELIGIBLE UNIT
                2 - SELECT TARGETS
                3 - MAKE RANGED ATTACKS
                4 - REPEAT FOR NEXT ELIGIBLE UNIT
        """
        self.current_phase = GamePhase.SHOOTING_PHASE.name
        self.active_player.set_units_for_shooting()
        return True

    def select_eligible_unit(self):
        selected_unit = self.active_player.get_next_unit_for_shooting_or_charging()
        if self.current_phase == GamePhase.SHOOTING_PHASE.name:
            if selected_unit:
                log(f'[REPORT][{self.active_player.name}] resolving attack for selected unit: [{selected_unit.name}]')
            else:
                log(f'[REPORT][{self.active_player.name}] no more units eligible for shooting to proceed')
        elif self.current_phase == GamePhase.CHARGE_PHASE.name:
            if selected_unit:
                log(f'[REPORT][{self.active_player.name}] resolving charge for selected unit: [{selected_unit.name}]')
            else:
                log(f'[REPORT][{self.active_player.name}] no more units eligible for charging to proceed')
        return True

    def select_targets(self):
        if self.current_phase == GamePhase.SHOOTING_PHASE.name:
            if self.active_player.get_selected_unit():
                # Choose ranged targets for that unit
                enemy_units = self.inactive_player.get_units_alive()
                self.active_player.set_ranged_target_for_selected_unit(enemy_units)
                if not self.active_player.get_selected_unit().has_shoot:
                    log(f'[REPORT] [{self.active_player.get_selected_unit().name}] does not have any valid target '
                        f'near. It won\'t shoot this turn')
        elif self.current_phase == GamePhase.CHARGE_PHASE.name:
            if self.active_player.get_selected_unit():
                pass
        return True

    def make_ranged_attacks(self):
        selected_unit = self.active_player.get_selected_unit()
        # At least one model can shoot a target
        if selected_unit.has_shoot:
            attacks = selected_unit.get_models_ranged_attacks()

            for count, attack in enumerate(attacks, start=1):
                log(f'\t----- ----- ----- Resolving attack #{count} out of {len(attacks)} ----- ----- -----')
                self.resolve_attack.set_new_attack(self.active_player, self.inactive_player, attacks[attack])
                self.resolve_attack.do_attack()
        else:
            log(f'\t[PLAYER {self.active_player.name}] [{selected_unit.name}] will not shoot since '
                f'it does not see anything')

    def repeat_for_next_eligible_unit(self):
        # Check if there are more units to be selected
        if self.active_player.are_more_units_to_be_selected():
            # Keep on executing the main loop since there are more units to come!
            return False
        else:
            # We are done so far
            return True

    def charge_phase(self):
        """
            4 - CHARGE PHASE
                1 - SELECT ELIGIBLE UNIT
                2 - SELECT TARGETS
                3 - MAKE CHARGE ROLL
                4 - MAKE CHARGE MOVE
                5 - REPEAT FOR NEXT ELIGIBLE UNIT
        """
        self.current_phase = GamePhase.CHARGE_PHASE.name
        self.active_player.set_units_for_charge()
        return True

    def make_charge_roll(self):
        if self.active_player.get_selected_unit():
            # Roll for charging roll
            self.active_player.dices.roll_dices('2D6')
            pass
        return True

    def make_charge_move(self):
        return True

    def fight_phase(self):
        """
            5 - FIGHT PHASE
                1 - FIGHTS FIRST
                2 - REMAINING COMBATS
                    1 - PILE IN
                    2 - MAKE MELEE ATTACKS
                    3 - CONSOLIDATE
        """
        self.current_phase = GamePhase.FIGHT_PHASE.name
        return True

    def fight_first(self):
        return True

    def remaining_combats(self):
        return True

    def pile_in(self):
        return True

    def make_melee_attacks(self):
        return True

    def consolidate(self):
        return True
