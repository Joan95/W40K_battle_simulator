from enum import Enum


class AttackStrength(Enum):
    DOUBLE_WEAK = 2
    WEAK = 3
    EQUAL = 4
    STRONG = 5
    DOUBLE_STRONG = 6


class CommandPhase(Enum):
    """
    1 - COMMAND PHASE
        1 - COMMAND
        2 - BATTLE-SHOCK
    """
    COMMAND_STEP = 1
    BATTLE_SHOCK_STEP = 2


class MovementPhase(Enum):
    """
    2 - MOVEMENT PHASE
        1 - MOVE UNITS
        2 - REINFORCEMENTS
    """
    MOVE_UNITS = 1
    REINFORCEMENTS = 2


class ShootingPhase(Enum):
    """
    3 - SHOOTING PHASE
        1 - SELECT ELIGIBLE UNIT
        2 - SELECT TARGETS
        3 - MAKE RANGED ATTACKS
        4 - REPEAT FOR NEXT ELIGIBLE UNIT
    """
    SELECT_ELIGIBLE_UNIT = 1
    SELECT_TARGETS = 2
    MAKE_RANGED_ATTACKS = 3
    REPEAT_FOR_NEXT_ELIGIBLE_UNIT = 4


class ChargePhase(Enum):
    """
    4 - CHARGE PHASE
        1 - SELECT ELIGIBLE UNIT
        2 - SELECT TARGETS
        3 - MAKE CHARGE ROLL
        4 - MAKE CHARGE MOVE
        5 - REPEAT FOR NEXT ELIGIBLE UNIT
    """
    SELECT_ELIGIBLE_UNIT = 1
    SELECT_TARGETS = 2
    MAKE_CHARGE_ROLL = 3
    MAKE_CHARGE_MOVEMENT = 4
    REPEAT_FOR_NEXT_ELIGIBLE_UNIT = 5


class FightPhase(Enum):
    """
    5 - FIGHT PHASE
        1 - FIGHTS FIRST
        2 - REMAINING COMBATS
            1 - PILE IN
            2 - MAKE MELEE ATTACKS
            3 - CONSOLIDATE
    """
    FIGHTS_FIRST = 1
    REMAINING_COMBATS = 2


class RemainingCombats(Enum):
    """
    5 - FIGHT PHASE
        1 - FIGHTS FIRST
        2 - REMAINING COMBATS
            1 - PILE IN
            2 - MAKE MELEE ATTACKS
            3 - CONSOLIDATE
    """
    PILE_IN = 1
    MAKE_MELEE_ATTACKS = 2
    CONSOLIDATE = 3


class GamePhase(Enum):
    COMMAND_PHASE = 1
    MOVEMENT_PHASE = 2
    SHOOTING_PHASE = 3
    CHARGE_PHASE = 4
    FIGHT_PHASE = 5


class ModelPreferredStyle(Enum):
    MELEE_ATTACK = 0
    RANGED_ATTACK = 1
    BALANCED_ATTACK = 2


class ModelPriority(Enum):
    WARLORD = 5
    EPIC_HERO = 4
    CHARACTER = 3
    UNIT_BOSS = 2
    INFANTRY = 1


class PlayerRol(Enum):
    ATTACKER = 0
    DEFENDER = 1


class AttackSteps(Enum):
    """
        1 - HIT ROLL
        2 - WOUND ROLL
        3 - ALLOCATE ATTACK
        4 - SAVING THROW
        5 - INFLICT DAMAGE
    """
    HIT_ROLL = 1
    WOUND_ROLL = 2
    ALLOCATE_ATTACK = 3
    SAVING_THROW = 4
    INFLICT_DAMAGE = 5


class Visibility(Enum):
    VISIBLE = 0
    INVISIBLE = 1


class WeaponType(Enum):
    MELEE = 0
    RANGED = 1
