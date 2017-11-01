# *****************************************************************************
# scheduler/enums.py
# *****************************************************************************

from enum import IntEnum, unique


# *****************************************************************************
# Weekday
# *****************************************************************************

@unique
class Weekday(IntEnum):

    """
    an IntEnum of weekday integer values

    """

    monday = 0
    tuesday = 1
    wednesday = 2
    thursday = 3
    friday = 4
    saturday = 5
    sunday = 6
