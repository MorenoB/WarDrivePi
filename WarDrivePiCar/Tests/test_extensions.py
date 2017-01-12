from unittest import TestCase
from Util.extensions import *


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
