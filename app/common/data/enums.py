import enum


class UserTokenType(enum.Enum):
    RESET_PASSWORD = 1


class ExperimentStatus(enum.Enum):
    INITIATED = 1
    RUNNING = 2
    COMPLETED = 3
