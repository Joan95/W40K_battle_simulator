from enum import Enum


class GamePhase(Enum):
    COMMAND_PHASE = 1
    MOVEMENT_PHASE = 2
    SHOOTING_PHASE = 3
    CHARGE_PHASE = 4
    FIGHT_PHASE = 5


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
