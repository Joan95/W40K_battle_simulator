from enum import Enum


class GamePhase(Enum):
    COMMAND_PHASE = 1
    MOVEMENT_PHASE = 2
    SHOOTING_PHASE = 3
    CHARGE_PHASE = 4
    FIGHT_PHASE = 5


class ModelPriority(Enum):
    WARLORD = 5
    EPIC_HERO = 4
    CHARACTER = 3
    UNIT_BOSS = 2
    INFANTRY = 1


class ModelToughnessAgainstWeaponAttack(Enum):
    DOUBLE_WEAK = 2
    WEAK = 3
    EQUAL = 4
    STRONG = 5
    DOUBLE_STRONG = 6


class MovementType(Enum):
    NORMAL_MOVE = 1
    ADVANCE = 2
    CHARGE_MOVE = 3
    FALL_BACK = 4
    PILE_IN = 5
    CONSOLIDATE = 6


class PlayerRol(Enum):
    ATTACKER = 0
    DEFENDER = 1


class Visibility(Enum):
    VISIBLE = 0
    INVISIBLE = 1


class WeaponType(Enum):
    MELEE = 0
    RANGED = 1
