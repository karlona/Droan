import math


class Shape:
    """ This class receives airfield pattern specific variables and determines possible configurations the pattern can
    be shaped around.

    Documentation:
    Federal Aviation Administration. Non-Towered Airport Flight Operations. 2018. Advisory Circular 90-66B,
    www.faa.gov/documentLibrary/media/Advisory_Circular/AC_90-66B.pdf. Accessed 28 Nov. 2018.

    """

    def __init__(self, field_length, glide_slope, pattern_altitude, climb_rate, turn_radius, approach_speed, headwind):
        """ Aircraft and airfield specifics are used to determine characteristics about the shape of the pattern that
        the aircraft can successfully maneuver.

        Inputs: field_length is the total runway length in meters, glide slope is the airfield's approach glide slope
        in degrees, pattern_altitude is the airfield's pattern altitude in meters, climb_rate is the aircraft's climb
        rate in meters per second, turn_radius is the aircraft's minimum turn radius in meters, approach_speed is the
        pattern and approach speed of the aircraft in meters per second, and headwind is the headwind at the airfield in
        meters per second. """

        self.check_for_exceptions(approach_speed, headwind)

        self.a = self.a_calculator(field_length, glide_slope)
        self.b = self.b_calculator(field_length)
        self.c = self.c_calculator(field_length)
        self.d = self.d_calculator(headwind, pattern_altitude, climb_rate, approach_speed, field_length)
        self.j = self.j_calculator(approach_speed, headwind, glide_slope, field_length, turn_radius, pattern_altitude)
        self.i = self.i_calculator(glide_slope)
        self.h = self.h_calculator(pattern_altitude, glide_slope, field_length)
        self.g = self.g_calculator(pattern_altitude)
        self.f = self.f_calculator()
        #  self.e = self.e_calculator() Not needed

        self.initial_climb_length = self.straight_climb_length_calculator()
        self.descent_length = self.descent_length_calculator()
        self.final_length = self.final_length_calculator()
        self.downwind_length = self.downwind_length_calculator()
        self.pattern_diameter = self.pattern_diameter_calculator()
        self.before_runway_length = self.before_runway_length_calculator()
        self.after_runway_length = self.after_runway_length_calculator()

    def check_for_exceptions(self, approach_speed, headwind):
        self.excessive_headwind(approach_speed, headwind)

    def excessive_headwind(self, approach_speed, headwind):
        if headwind >= approach_speed:
            raise ValueError("headwind cannot equal or exceed approach_speed")
        else:
            pass

    def a_calculator(self, field_length, glide_slope):
        glide_slope_radians = glide_slope * math.pi / 180
        return [0, 0, 0.25 * field_length * math.tan(glide_slope_radians)]  # Assumed touchdown at 1/4 runway length

    def b_calculator(self, field_length):
        return [0.25 * field_length, 0, 0]

    def c_calculator(self, field_length):
        return [0.5 * field_length, 0, 0]

    def d_calculator(self, headwind, pattern_altitude, climb_rate, approach_speed, field_length):
        climb_time = 0.7 * pattern_altitude / climb_rate
        horizontal_ground_speed = (approach_speed ** 2 - climb_rate ** 2) ** 0.5 - headwind
        return [climb_time * horizontal_ground_speed + 0.5 * field_length, 0, 0.7 * pattern_altitude]

    def j_calculator(self, approach_speed, headwind, glide_slope, field_length, turn_radius, pattern_altitude):
        glide_slope_radians = glide_slope * math.pi / 180
        runway_threshold_height = self.a[2]
        x_15 = 15 * approach_speed * math.cos(glide_slope_radians) - headwind  # 15 second final length
        z_15 = runway_threshold_height + math.tan(glide_slope_radians) * x_15  # 15 second final, altitude drop
        descent_length = pattern_altitude / math.tan(glide_slope_radians)

        #  Notice that there are two different variants of h2i nested below.
        if x_15 / 2 >= turn_radius:  # if half the 15 second final length is greater than the minimum turning radius
            #  h2i is the horizontal distance between point h and i in the pattern
            h2i = descent_length - (0.25 * field_length) - x_15 - (math.pi * x_15 / 2)  # radius is half of final leg
            if x_15 >= h2i:  # x >= h2i so descent doesn't begin before past runway threshold, G
                return [-x_15, 0, z_15]  # 15 second final leg from beginning of final leg until runway threshold
            else:  # final must be the length of h2i so that descent doesn't begin before point G
                h2i_z = runway_threshold_height + math.tan(glide_slope_radians) * h2i
                return [-h2i, 0, h2i_z]  # final is longer than 15 seconds
        else:  # final is too short,  minimum turning radius won't allow this short of a final while maintaining 45 deg
            h2i = descent_length - (0.25 * field_length) - x_15 - (math.pi * turn_radius)  # radius is min radius
            if 2 * turn_radius >= h2i:  # x >= h2i so descent doesn't begin before past runway threshold, G
                two_turn_radius_z = runway_threshold_height + math.tan(glide_slope_radians) * 2 * turn_radius
                return [-2 * turn_radius, 0, two_turn_radius_z]
            else:
                h2i_z = runway_threshold_height + math.tan(glide_slope_radians) * h2i
                return [-h2i, 0, h2i_z]

    def i_calculator(self, glide_slope):
        glide_slope_radians = glide_slope * math.pi / 180
        radius = -self.j[0] / 2  # The pattern's turn radius is half the final leg due to 45 degree geometry
        i_z = math.pi * radius * math.tan(glide_slope_radians) + self.j[2]  # i_z = j_z + half circumference glide slope
        return [self.j[0], -self.j[0], i_z]

    def h_calculator(self, pattern_altitude, glide_slope, field_length):
        glide_slope_radians = glide_slope * math.pi / 180
        descent_length = pattern_altitude / math.tan(glide_slope_radians)
        final_x = self.j[0]
        radius = -self.j[0] / 2
        h2i_x = descent_length - 0.25 * field_length + final_x - radius
        return [self.i[0] + h2i_x, self.i[1], pattern_altitude]

    def g_calculator(self, pattern_altitude):
        return [0, self.h[1], pattern_altitude]

    def f_calculator(self):
        return [self.d[0], self.g[1], self.g[2]]

    #  def e_calculator(self, ):
        #  return [, , self.f[2]]

    def straight_climb_length_calculator(self):
        return self.d[0] - self.c[0]

    def descent_length_calculator(self):
        return (self.h[0] - self.i[0]) + (math.pi * self.i[1] / 2) + (-self.j[0]) + (self.b[0])

    def final_length_calculator(self):
        return -self.j[0]

    def downwind_length_calculator(self):
        return self.f[0] - self.i[0]

    def pattern_diameter_calculator(self):
        return self.i[1]

    def before_runway_length_calculator(self):
        return -1.5 * self.j[0]

    def after_runway_length_calculator(self):
        return self.d[0] - self.j[0] / 2


East_Bay = Shape(163, 3, 30, 2.54, 75, 13.4, 0)
print("Final leg is {0:1.0f} meters".format(East_Bay.final_length))
print("Straight climb distance is {0:1.0f} meters".format(East_Bay.initial_climb_length))
print("Pattern width is {0:1.0f} meters".format(East_Bay.pattern_diameter))
print("Downwind distance is {0:1.0f} meters".format(East_Bay.downwind_length))
print("Available distance needed before runway is {0:1.0f} meters.".format(East_Bay.before_runway_length))
print("Available distance needed after runway is {0:1.0f} meters.".format(East_Bay.after_runway_length))
