import math


class MissionSpecifications:
    """ This class enables the documentation of a possible mission for an aircraft to be designed around. """

    def __init__(self, payload, length, length_type, speed, altitude, runway, climb, turn, unique_phases):
        """ Mission requirements are the inputs for a conceptual aircraft design.

        Inputs: payload is the payload mass in kilograms, length is either the mission range in kilometers or the
        mission endurance in minutes, length_type is either the string 'range' or 'endurance' based on length, speed
        is the cruise speed in meters per second, altitude is the cruise altitude in meters, runway is the runway
        length in meters, climb is the climb rate in meters per second, turn is the turn radius in meters, phases is
        an integer detailing the number of phases in the mission profile. """

        # Create Class Variables
        self.payload = payload
        if length_type == 'range':
            self.range = length
        elif length_type == 'endurance':
            self.endurance = length
        else:
            raise NameError('Length type {} not found.  Accepted length types are \'range\' and \'endurance.\'')
        self.speed_cruise = speed
        self.altitude_cruise = altitude
        self.field_length = runway
        self.climb = climb
        self.turn_radius = turn

        # Detail specifics of each mission phase
        self.phases = []
        for n in range(unique_phases):
            self.phase_details = input("Input mission phase details as a list with the following values: "
                                       "[final speed (m/s), L/D, time (s), vertical speed (m/s), speed change (m/s)]")

    def detail_phases(self):
        """ Specify mission phase specifications for mission phase energy requirement calculations. """
        self.phases.append(self.phase_details)


class TakeoffWeightGuess:  # This should not be a class, but I'm leaving it for now...
    """ This class serves as the beginning of a conceptual aircraft design based on mission requirements. """

    def __init__(self):
            self.takeoff_weight_guess = self.estimate_takeoff_weight()

    def import_historically_similar_aircraft(self):
        return

    def estimate_takeoff_weight(self):
        return input("Initial guess of the takeoff weight, in kilograms.")


class MaximumPower(MissionSpecifications):
    """Determine the mission phase that has the maximum power requirements."""

    def __init__(self):
        return


class TakeoffPower:
    """ An analysis of the power requirements for the takeoff mission phase is performed. """

    def __init__(self, ground_roll_length, takeoff_mass, takeoff_speed):
        self.ground_roll_length = ground_roll_length
        self.takeoff_mass = takeoff_mass
        self.takeoff_speed = takeoff_speed

        self.ground_roll_kinetic_energy = self.calculate_kinetic_energy()
        self.takeoff_acceleration = self.calculate_takeoff_acceleration()
        self.ground_roll_time = self.calculate_takeoff_ground_roll_time()

        self.takeoff_power = self.calculate_takeoff_power()

    def calculate_kinetic_energy(self):
        return self.takeoff_mass * self.takeoff_speed ** 2 / 2

    def calculate_takeoff_acceleration(self):
        return self.takeoff_speed ** 2 / (2 * self.ground_roll_length)  # (Nicolai, p. 264 eq. 10.4a)

    def calculate_takeoff_ground_roll_time(self):
        return self.takeoff_speed / self.takeoff_acceleration  # (Nicolai, p. 267 section 10.3.5 Time During Takeoff)

    def calculate_takeoff_power(self):
        return self.ground_roll_kinetic_energy / self.ground_roll_time


class MotorSpecifications:
    """ User inputs specifications for the electric motor chosen. """

    def __init__(self, input_voltage, whole_chain_efficiency, max_continuous_power):
        self.input_voltage = input_voltage
        self.whole_chain_efficiency = whole_chain_efficiency
        self.max_continuous_power = max_continuous_power


class BatterySpecifications:
    """ User inputs specifications for the battery chemistry chosen. """

    def __init__(self, nominal_cell_voltage, c_rate, cell_capacity):
        self.nominal_cell_voltage = nominal_cell_voltage
        self.c_rate = c_rate
        self.cell_capacity = cell_capacity


class BatteryWeight(TakeoffPower, MotorSpecifications, MissionSpecifications, BatterySpecifications):
    """ The aircraft battery is sized to execute the provided mission with appropriate power and capacity. """

    def __init__(self, takeoff_power, motor_specifications, mission_specifications, battery_specifications):
        self.number_in_series = self.size_number_in_series(motor_specifications, battery_specifications)

    def size_number_in_series(self, motor_specifications, battery_specifications):
        return math.ceil(motor_specifications.input_voltage / battery_specifications.nominal_cell_voltage)

    def size_number_in_parallel(self):
        return

    def size_parallel_for_endurance(self):
        return

    def size_parallel_for_power(self):
        return

    def calculate_battery_cell_mass(self):
        return


class EmptyWeight:
    def __init__(self):
        return


class TakeoffWeight:
    def __init__(self):
        return
