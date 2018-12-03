class Mission:
    """ This class enables the documentation of a possible mission for an aircraft to be designed around. """

    def __init__(self, payload, length, length_type, speed, altitude, runway, climb, turn, phases):
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
        self.detail_phases(phases)

    def detail_phases(self, phases):
        for n in range(phases):
            pass # just added so that the code runs
            # User defined mission phase specifics including speed, altitude, climb/descend, accel/deccel


class Aircraft:
    """ This class serves as the beginning of a conceptual aircraft design based on mission requirements. """

    def __init__(self, mission, energy, propulsion):
            self.mission = mission
            self.energy = energy
            self.propulsion = propulsion

    def preliminary_estimate_takeoff_weight(self):
        guess_takeoff_weight = input("Guess a takeoff weight in kilograms.")
        self.energy_weight()
        self.historical_empty_weight()

    def energy_weight(self):
        return

    def historical_empty_weight(self):
        return


class Battery:
    """ The aircraft battery is sized to execute the provided mission with appropriate power and capacity. """

    def __init__(self):
        return

    def determine_number_in_series(self):
        return

    def determine_number_in_parallel(self):
        return

    def calculate_battery_cell_mass(self):
        return
