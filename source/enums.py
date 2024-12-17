from enum import Enum


class AttackStrength(Enum):
    DOUBLE_WEAK = 2
    WEAK = 3
    EQUAL = 4
    STRONG = 5
    DOUBLE_STRONG = 6


class CommandPhaseSteps(Enum):
    COMMAND_STEP = 1
    BATTLE_SHOCK_STEP = 2


class MovementPhaseSteps(Enum):
    MOVE_UNITS = 1
    REINFORCEMENTS = 2


class ShootingPhaseSteps(Enum):
    SELECT_UNIT_FOR_SHOOTING = 1
    SELECT_TARGETS = 2
    RESOLVE_ATTACKS = 3
    SELECT_NEXT_UNIT = 4


class ChargePhaseSteps(Enum):
    SELECT_UNIT_FOR_CHARGE = 1
    SELECT_TARGETS = 2
    CHARGE_ROLL = 3
    CHARGE_MOVEMENT = 4
    SELECT_NEXT_UNIT = 5


class FightPhaseSteps(Enum):
    PILE_IN = 1
    MAKE_MEELE_ATTACKS = 2
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


class Visibility(Enum):
    VISIBLE = 0
    INVISIBLE = 1


class WeaponType(Enum):
    MELEE = 0
    RANGED = 1
