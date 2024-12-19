from colorama import Fore
from enums import ChargePhase, CommandPhase, FightPhase, GamePhase, MovementPhase, RemainingCombats, ShootingPhase
from game_phases_handler import *
from logging_handler import log


class GameHandler:
    def __init__(self, turns, board):
        self.boardgame = board
        self.active_player = None
        self.inactive_player = None
        self.turns_list = turns
        self.game_turn = 0
        self.phases = dict()

        # If here all the Units have been displayed so the game can start!
        self.boardgame.start_game()

        # Load game phases and configuration
        self.load_game_phases_and_steps()

    def execute_all_phases(self):
        for count, phase_name in enumerate(self.phases, start=1):
            phase = self.phases[phase_name]
            feedback = self.execute_main_phases(phase_name, phase, count)

    def execute_main_phases(self, phase_name, phase_dict, phase_number, upper_phase=None):
        current_phase = phase_dict['main_function']
        phase_name = f'#{phase_number} {phase_name.replace("_", " ").title().upper()}'
        if upper_phase:
            phase_name = upper_phase + ' - ' + phase_name
        log(f"[REPORT] [TURN #{self.game_turn}] ----- ----- ----- [{self.active_player.name}] "
            f"{phase_name} ----- ----- -----", True)

        feedback = current_phase(self.active_player, self.inactive_player, self.boardgame)

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
            self.execute_all_phases()

            # Execute Defender phase
            self.active_player = defender
            self.inactive_player = attacker
            self.execute_all_phases()
            print()

    def load_game_phases_and_steps(self):
        phase_functions = {
            GamePhase.COMMAND_PHASE.name: command_phase,
            GamePhase.MOVEMENT_PHASE.name: movement_phase,
            GamePhase.SHOOTING_PHASE.name: shooting_phase,
            GamePhase.CHARGE_PHASE.name: charge_phase,
            GamePhase.FIGHT_PHASE.name: fight_phase
        }

        """
        1 - COMMAND PHASE
            1 - COMMAND
            2 - BATTLE-SHOCK
        """
        command_phase_functions = {
            CommandPhase.COMMAND_STEP.name: {
                'main_function': command
            },
            CommandPhase.BATTLE_SHOCK_STEP.name: {
                'main_function': battle_shock
            },
        }

        """
        2 - MOVEMENT PHASE
            1 - MOVE UNITS
            2 - REINFORCEMENTS
        """
        movement_phase_functions = {
            MovementPhase.MOVE_UNITS.name: {
                'main_function': move_units
            },
            MovementPhase.REINFORCEMENTS.name: {
                'main_function': reinforcements
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
                'main_function': select_eligible_unit
            },
            ShootingPhase.SELECT_TARGETS.name: {
                'main_function': select_targets
            },
            ShootingPhase.MAKE_RANGED_ATTACKS.name: {
                'main_function': make_ranged_attacks
            },
            ShootingPhase.REPEAT_FOR_NEXT_ELIGIBLE_UNIT.name: {
                'main_function': repeat_for_next_eligible_unit
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
                'main_function': select_eligible_unit
            },
            ChargePhase.SELECT_TARGETS.name: {
                'main_function': select_targets
            },
            ChargePhase.MAKE_CHARGE_ROLL.name: {
                'main_function': make_charge_roll
            },
            ChargePhase.REPEAT_FOR_NEXT_ELIGIBLE_UNIT.name: {
                'main_function': repeat_for_next_eligible_unit
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
                'main_function': fight_first
            },
            FightPhase.REMAINING_COMBATS.name: {
                'main_function': remaining_combats
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
                'main_function': pile_in
            },
            RemainingCombats.MAKE_MELEE_ATTACKS.name: {
                'main_function': make_melee_attacks
            },
            RemainingCombats.CONSOLIDATE.name: {
                'main_function': consolidate
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
