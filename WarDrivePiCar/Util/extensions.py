from Util.enums import CompassDirections


# Will make sure the given number 'number' wont be bigger than max-number and not smaller than minimum number
def clamp(number, minimum_number, max_number):
    return max(min(max_number, number), minimum_number)


def convert_compass_direction_to_angle(direction):
    if direction == CompassDirections.North:
        return 0
    elif direction == CompassDirections.South:
        return 180
    elif direction == CompassDirections.East:
        return 90
    elif direction == CompassDirections.West:
        return 270
    else:
        return 0


def convert_int_to_degrees(value):
    if value >= 360:
        return convert_int_to_degrees(value - 360)
    elif value < 0:
        return convert_int_to_degrees(360 + value)
    return value


def convert_angle_to_compass_direction(angle):
    rounded_angle = round(angle)

    if rounded_angle == 0 or rounded_angle == 360:
        return CompassDirections.North

    elif rounded_angle == 180:
        return CompassDirections.South

    elif rounded_angle == 90:
        return CompassDirections.East

    elif rounded_angle == 270:
        return CompassDirections.West
    else:
        return None


# Will find a given string string between two other strings
# For example find_between("123abc456", "123, "456") will return "abc"
def find_between(input_string, first_string, last_string):
    try:
        start = input_string.index(first_string) + len(first_string)
        end = input_string.index(last_string, start)
        return input_string[start:end]
    except ValueError:
        return ""
