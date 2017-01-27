from unittest import TestCase
from Util.extensions import convert_int_to_degrees, convert_angle_to_compass_direction, \
    convert_compass_direction_to_angle, CompassDirections


class extensions(TestCase):
    def test_convert_int_to_degrees(self):
        normal_degree = 50
        ret_normal_degrees = convert_int_to_degrees(normal_degree)

        self.assertEquals(normal_degree, ret_normal_degrees)

        pos_degree = 362
        ret_pos_degrees = convert_int_to_degrees(pos_degree)

        self.assertEquals(ret_pos_degrees, 2)

        neg_degree = -5
        ret_neg_degrees = convert_int_to_degrees(neg_degree)

        self.assertEquals(ret_neg_degrees, 355)

        neg_degree = -1
        ret_neg_degrees = convert_int_to_degrees(neg_degree)

        self.assertEquals(ret_neg_degrees, 359)

    def test_convert_angle_to_compass_direction(self):
        input_angle = 0
        expected_output = CompassDirections.North
        ret_compass_direction = convert_angle_to_compass_direction(input_angle)

        self.assertEquals(ret_compass_direction, expected_output)

        input_angle = 180
        expected_output = CompassDirections.South
        ret_compass_direction = convert_angle_to_compass_direction(input_angle)

        self.assertEquals(ret_compass_direction, expected_output)

        input_angle = 90
        expected_output = CompassDirections.East
        ret_compass_direction = convert_angle_to_compass_direction(input_angle)

        self.assertEquals(ret_compass_direction, expected_output)

        input_angle = 270
        expected_output = CompassDirections.West
        ret_compass_direction = convert_angle_to_compass_direction(input_angle)

        self.assertEquals(ret_compass_direction, expected_output)

    def test_convert_compass_direction_to_angle(self):

        input_compass_direction = CompassDirections.North
        expected_output = 0
        ret_degrees = convert_compass_direction_to_angle(input_compass_direction)

        self.assertEquals(ret_degrees, expected_output)

        input_compass_direction = CompassDirections.South
        expected_output = 180
        ret_degrees = convert_compass_direction_to_angle(input_compass_direction)

        self.assertEquals(ret_degrees, expected_output)

        input_compass_direction = CompassDirections.East
        expected_output = 90
        ret_degrees = convert_compass_direction_to_angle(input_compass_direction)

        self.assertEquals(ret_degrees, expected_output)

        input_compass_direction = CompassDirections.West
        expected_output = 270
        ret_degrees = convert_compass_direction_to_angle(input_compass_direction)

        self.assertEquals(ret_degrees, expected_output)
