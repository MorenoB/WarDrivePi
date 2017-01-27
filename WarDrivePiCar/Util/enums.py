
class MovementType(object):
    Idle, Forward, Reverse, Turn_Left, Turn_Right, Spin_Left, Spin_Right = range(7)


class TurnModeType(object):
    Turning, Spinning = range(2)


class CompassDirections(object):
    North, South, East, West = range(4)
