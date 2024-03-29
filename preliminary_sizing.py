import math
import matplotlib.pyplot as plt


class Phase:
    """ Definitely a class
    This class details the various phases associated with the mission. """

    def __init__(self, name, final_speed, lift_over_drag, time, vertical_speed, speed_change, final_altitude):
        """
        name is a string naming the mission phase
        final_speed in m/s
        lift_over_drag no units
        time in seconds
        vertical_speed in m/s
        speed_change in m/s
        """
        self.name = name
        self.final_speed = final_speed
        self.lift_over_drag = lift_over_drag
        self.time = time
        self.vertical_speed = vertical_speed
        self.speed_change = speed_change
        self.final_altitude = final_altitude
        self.maximum_power = None

    def add_maximum_power(self, power):
        self.maximum_power = power

    def __str__(self):
        return "Name: {},  Final Speed: {},  LoD: {},  Time: {},  Vert Speed: {},  Speed Change: {},  Max Power: {}" \
               "".format(self.name, self.final_speed, self.lift_over_drag, self.time, self.vertical_speed,
                         self.speed_change, self.maximum_power)

    #  This is so Mission.compile_unique_phases actually works
    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class Mission:
    """ Definitely a class
    All the phases are combined into a mission. """

    def __init__(self, takeoff_mass_guess, payload, cruise_altitude, lowest_voltage_max_power_ratio=0.8):
        self.all_phases = []
        self.unique_phases = []
        self.takeoff_mass_guess = takeoff_mass_guess
        self.payload = payload
        self.cruise_altitude = cruise_altitude
        # Lowest voltage ratio at which you still want to execute max power, i.e. 0.8 is 80% of full charge !voltage!
        self.lowest_voltage_maximum_power_ratio = lowest_voltage_max_power_ratio
        self.maximum_power = None

    def add_all_phases(self, phases):
        [self.all_phases.append(phase) for phase in phases]
        self.compile_unique_phases()

    def compile_unique_phases(self):  # Unsure how to not use a for loop here
        [self.unique_phases.append(phase) for phase in self.all_phases if phase not in self.unique_phases]

    def add_maximum_power(self):
        power = []
        [power.append(phase.maximum_power) for phase in self.unique_phases]
        self.maximum_power = max(power)


class Motor:
    """ Definitely a class
    User inputs specifications for the electric motor chosen. """

    def __init__(self, input_voltage, whole_chain_efficiency, max_continuous_power):
        """
        input_voltage in volts
        whole chain efficiency no units as a decimal less than or equal to 1 and greater than 0
        max_continuous_power in watts
        """
        self.input_voltage = input_voltage
        self.whole_chain_efficiency = whole_chain_efficiency
        self.max_continuous_power = max_continuous_power


class Battery:
    """ Definitely a class
    User inputs specifications for the battery chemistry chosen. """

    def __init__(self, nominal_cell_voltage, c_max, cell_capacity, specific_energy_density):
        """
        nominal_cell_voltage in volts
        c_max in Amps per Amp - hour (current / battery capacity)
        cell_capacity in ampere hours
        specific_energy_density in watt hours per kilogram
        """
        self.nominal_cell_voltage = nominal_cell_voltage
        self.c_max = c_max / 3600  # Convert 1/hours to 1/seconds
        self.cell_capacity = cell_capacity * 3600  # Convert ampere hours to ampere seconds
        self.specific_energy_density = specific_energy_density * 3600  # Convert W-h/kg to W-s/kg
        self.battery_cell_mass = self.cell_capacity * self.nominal_cell_voltage / self.specific_energy_density


class PhasePower:
    """ Not a class, per se, but could be depending on the interpretation of the single responsibility principle
    Calculate maximum power required for each phase. This seems like a large function lol, but whatever. We'll
    talk about next time we talk."""

    def __init__(self, mission):
        [self.calculate_power(phase, mission.takeoff_mass_guess) for phase in mission.unique_phases]
        mission.add_maximum_power()

    def calculate_power(self, phase, mass):
        power = self.calculate_energy_delta_power(phase, mass) \
                + self.calculate_aerodynamic_power(phase.final_speed, phase.speed_change, phase.lift_over_drag, mass)
        if power > 0:  # Assuming that energy recovery is not an option
            phase.add_maximum_power(power)
        else:
            phase.add_maximum_power(0)

    def calculate_energy_delta_power(self, phase, mass):
        total_energy_delta = self.calculate_kinetic_delta(phase.final_speed, phase.speed_change, mass) \
                             + self.calculate_potential_delta(phase.time, phase.vertical_speed, mass)
        return total_energy_delta / phase.time

    def calculate_kinetic_delta(self, final_speed, speed_change, mass):
        initial_velocity = final_speed - speed_change
        square_velocity_difference = final_speed ** 2 - initial_velocity ** 2
        return (mass / 2) * square_velocity_difference

    def calculate_potential_delta(self, time, vertical_speed, mass):
        altitude_delta = time * vertical_speed
        return 9.80665 * mass * altitude_delta

    def calculate_aerodynamic_power(self, final_speed, speed_change, lift_over_drag, mass):
        maximum_speed = self.calculate_maximum_speed(final_speed, speed_change)
        weight = 9.80665 * mass
        return weight * maximum_speed / lift_over_drag

    def calculate_maximum_speed(self, final_speed, speed_change):
        initial_speed = final_speed - speed_change
        if final_speed == initial_speed:
            return final_speed
        else:
            return max(final_speed, initial_speed)


class BatteryPackMass:
    """ Not a class, per se, but could be depending on the interpretation of the single responsibility principle
    The aircraft battery is sized to execute the provided mission with appropriate power and capacity.
    Could this be inside of MassIteration? IDK, probably not."""

    def __init__(self, motor, mission, battery):
        self.number_in_series = self.size_number_in_series(motor.input_voltage, battery.nominal_cell_voltage)
        self.number_in_parallel_power = None
        self.number_in_parallel_endurance = None
        self.number_in_parallel = self.size_number_in_parallel(battery, motor.whole_chain_efficiency,
                                                               mission.all_phases, mission.maximum_power,
                                                               mission.lowest_voltage_maximum_power_ratio)
        self.number_of_cells = self.number_in_series * self.number_in_parallel
        self.battery_pack_mass = self.number_of_cells * battery.battery_cell_mass

    def size_number_in_series(self, input_voltage, nominal_cell_voltage):
        return math.ceil(input_voltage / nominal_cell_voltage)

    def size_number_in_parallel(self, battery, efficiency, all_phases, max_power, low_voltage_ratio):
        parallel_power = self.size_parallel_for_power(max_power, battery.nominal_cell_voltage, efficiency,
                                                      battery.c_max, battery.cell_capacity, low_voltage_ratio)
        parallel_endurance = self.size_parallel_for_endurance(battery.nominal_cell_voltage, battery.cell_capacity,
                                                              efficiency, all_phases)
        return math.ceil(max(parallel_power, parallel_endurance))

    def size_parallel_for_endurance(self, cell_voltage, cell_capacity, efficiency, phases):
        phase_energy = [specific_phase.maximum_power * specific_phase.time for specific_phase in phases]
        cell_energy_capacity = cell_voltage * cell_capacity * efficiency
        self.number_in_parallel_endurance = math.ceil(sum(phase_energy) / cell_energy_capacity)
        return math.ceil(sum(phase_energy) / cell_energy_capacity)

    def size_parallel_for_power(self, max_power, cell_voltage, efficiency, c_max, cell_capacity, low_voltage_ratio):
        battery_pack_voltage = self.number_in_series * cell_voltage * low_voltage_ratio
        self.number_in_parallel_power = math.ceil(max_power / (c_max * cell_capacity * efficiency
                                                               * battery_pack_voltage))
        return math.ceil(max_power / (c_max * cell_capacity * efficiency * battery_pack_voltage))

    #  Everything above is ready to be reviewed for cohesion and verified as clean code


class SimilarPlane:
    """ Definitely a class
    Similar planes to plane being designed."""

    def __init__(self, takeoff_mass, empty_mass):
        self.takeoff_mass = takeoff_mass
        self.empty_mass = empty_mass
        self.log_takeoff_mass = math.log10(takeoff_mass)
        self.log_empty_mass = math.log10(empty_mass)


class HistoricalTrend:
    """ Definitely a class
    Calculate historical trend data in order to calculate required empty mass of aircraft to be designed. """

    def __init__(self):
        self.similar_planes = []
        self.trend_slope = None
        self.trend_y_intercept = None
        self.empty_mass_required = None

    def add_similar_planes(self, similar_planes):
        [self.similar_planes.append(plane) for plane in similar_planes]

    def calculate_empty_mass_required(self, takeoff_mass_guess):
        errors = self.populate_errors()
        squared_errors = self.calculate_squared_errors(errors)
        y_intercept_derivative = self.calculate_y_intercept_derivative(squared_errors)
        slope_derivative = self.calculate_slope_derivative(squared_errors)
        self.calculate_slope_and_y_intercept(y_intercept_derivative, slope_derivative)
        self.empty_mass_required = 10 ** (math.log10(takeoff_mass_guess) * self.trend_slope + self.trend_y_intercept)
        return self.empty_mass_required

    def populate_errors(self):
        errors = []
        [errors.append([plane.log_empty_mass, -1, -1 * plane.log_takeoff_mass]) for plane in self.similar_planes]
        return errors

    def calculate_squared_errors(self, populated_errors):
        not_summed = []
        [not_summed.append([1, error[2] ** 2, 2 * error[1] * error[2], 2 * error[0] * error[1],
                            2 * error[0] * error[2], error[0] ** 2]) for error in populated_errors]
        squared_errors = []
        for i in range(6):
            summation = 0
            for j in range(len(not_summed)):
                summation += not_summed[j][i]
            squared_errors.append(summation)
        return squared_errors

    def calculate_y_intercept_derivative(self, squared_errors):
        return [2 * squared_errors[0], squared_errors[2], squared_errors[3]]

    def calculate_slope_derivative(self, squared_errors):
        return [squared_errors[2], 2 * squared_errors[1], squared_errors[4]]

    def calculate_slope_and_y_intercept(self, y_intercept_derivative, slope_derivative):
        a = [[y_intercept_derivative[0], y_intercept_derivative[1]], [slope_derivative[0], slope_derivative[1]]]
        b = [[-1 * y_intercept_derivative[2]], [-1 * slope_derivative[2]]]
        a_determinant = 1 / (a[0][0] * a[1][1] - a[0][1] * a[1][0])
        a_inverse = [[a_determinant * a[1][1], -1 * a_determinant * a[0][1]],
                     [-1 * a_determinant * a[1][0], a_determinant * a[0][0]]]
        self.trend_y_intercept = a_inverse[0][0] * b[0][0] + a_inverse[0][1] * b[1][0]
        self.trend_slope = a_inverse[1][0] * b[0][0] + a_inverse[1][1] * b[1][0]


class MassIteration:
    """ Probably shouldn't be its own class
    This class refines the takeoff mass guess for the mission to a point where the
    available and required empty masses are within half a percent of one another."""

    def __init__(self, motor, mission, battery, historical_trend, acceptable_error=0.005):
        self.iterated_empty_mass = None
        self.iterated_takeoff_mass = None
        self.acceptable_error = acceptable_error
        self.iterate_empty_mass_available(motor, mission, battery, historical_trend)

    def iterate_empty_mass_available(self, motor, mission, battery, historical_trend):
        empty_mass_required = historical_trend.calculate_empty_mass_required(mission.takeoff_mass_guess)
        empty_mass_available = mission.takeoff_mass_guess - mission.payload \
                               - BatteryPackMass(motor, mission, battery).battery_pack_mass
        error = (empty_mass_available - empty_mass_required) / empty_mass_required
        while error > self.acceptable_error:
            if empty_mass_required > empty_mass_available:
                mission.takeoff_mass_guess += empty_mass_required - empty_mass_available
            else:
                mission.takeoff_mass_guess -= empty_mass_available - empty_mass_required
            empty_mass_required = historical_trend.calculate_empty_mass_required(mission.takeoff_mass_guess)
            empty_mass_available = mission.takeoff_mass_guess - mission.payload \
                                   - BatteryPackMass(motor, mission, battery).battery_pack_mass
            error = (empty_mass_available - empty_mass_required) / empty_mass_required
        self.iterated_empty_mass = empty_mass_available
        self.iterated_takeoff_mass = mission.takeoff_mass_guess


class Matching:
    """A class to size the wing and propulsion device based on various aircraft requirements. Each sizing function is
     represented by a nested list where each list's first value is a coefficient and the second value is the power of
     the dependent variable (W/S). The matching chart is W/P vs W/S. """

    def __init__(self, takeoff_mass, max_wing_loading=10000, max_power_loading=0.3):
        self.wing_loading = None
        self.power_loading = None
        self.max_wing_loading = max_wing_loading
        self.max_power_loading = max_power_loading
        self.mass = takeoff_mass

    def create_matching_chart(self):
        plt.figure(1)
        plt.title('Matching Chart')
        plt.xlabel('Wing Loading (Pascals)')
        plt.ylabel('Power Loading (Newtons / Watt)')
        plt.xlim(0, self.max_wing_loading)  # 200 psf is the equivalent of around 10,000 Pascals
        plt.ylim(0, self.max_power_loading)  # 35 lbf/hp is the equivalent of around 0.2 Newtons per Watt

    def plot_matching_chart(self):
        plt.legend(loc=1)
        plt.show()

    def plot_stall_speed(self, name, altitude, max_clean_cl, stall_speed, pattern='-'):
        plt.vlines(self.size_to_stall(altitude, max_clean_cl, stall_speed),
                   0, self.max_power_loading, label='{}'.format(name), color='red', linestyles='{}'.format(pattern))

    def plot_takeoff_distance(self, name, takeoff_field_length, altitude, max_takeoff_cl, pattern='-'):
        wing_loading = list(range(1, self.max_wing_loading + 1))
        power_loading = [self.size_to_takeoff(takeoff_field_length, altitude, max_takeoff_cl)[0][0]
                         * x ** self.size_to_takeoff(takeoff_field_length, altitude, max_takeoff_cl)[0][1]
                         for x in wing_loading]
        plt.plot(wing_loading, power_loading, label='{}'.format(name), color='blue', ls='{}'.format(pattern))

    def plot_landing_distance(self, name, altitude, landing_field_length, max_landing_cl, pattern='-'):
        plt.vlines(self.size_to_landing(altitude, landing_field_length, max_landing_cl),
                   0, self.max_power_loading, label='{}'.format(name), color='purple', linestyles='{}'.format(pattern))

    def plot_climbing_requirements(self, name, mass, altitude, speed, aspect_ratio, rate_of_climb,
                                   propeller_efficiency=0.85, gear_down=False,
                                   oswald_efficiency_factor=0.85, cl=1.5, pattern='-'):
        [wing_loading, power_loading] = self.size_to_climb(
            mass, altitude, speed, aspect_ratio, gear_down, oswald_efficiency_factor, cl,
            rate_of_climb, propeller_efficiency)
        plt.plot(wing_loading, power_loading, label='{}'.format(name), color='green', ls='{}'.format(pattern))

    def plot_cruise_speed_requirements(self, name, speed, altitude, cruise_lift_coefficient, mass, aspect_ratio,
                                       oswald_efficiency_factor=0.85, propeller_efficiency=0.85,
                                       gear_down=True, pattern='-'):
        [wing_loading, power_loading] = self.size_to_cruise(speed, altitude, cruise_lift_coefficient, mass,
                                                            aspect_ratio, oswald_efficiency_factor,
                                                            propeller_efficiency, gear_down)
        plt.plot(wing_loading, power_loading, label='{}'.format(name), color='orange', ls='{}'.format(pattern))

    def size_to_stall(self, altitude, max_clean_cl, stall_speed):
        density = self.convert_altitude_to_density(altitude)
        return stall_speed ** 2 * density * max_clean_cl / 2

    def convert_altitude_to_density(self, altitude):
        """ Altitude in meters, density in kilograms per cubic meter. """
        return 0.000000002490 * altitude ** 2 - 0.000105332443 * altitude + 1.211228027786

    def size_to_takeoff(self, takeoff_field_length, altitude, max_takeoff_cl):
        """ takeoff_distance in meters. takeoff_distance is from stand still to 50 ft altitude. """
        takeoff_parameter = self.calculate_takeoff_parameter(takeoff_field_length)
        density_ratio = self.convert_altitude_to_density(altitude) / self.convert_altitude_to_density(0)
        return [[takeoff_parameter * density_ratio * max_takeoff_cl, -1]]

    def calculate_takeoff_parameter(self, takeoff_distance):
        a = 0.055822  # Roskam values converted to metric units (FAR 23 propeller aircraft)
        b = 8.680402  # Roskam values converted to metric units (FAR 23 propeller aircraft)
        c = -1 * takeoff_distance
        takeoff_parameter_1 = -b + (b ** 2 - 4 * a * c) ** 0.5 / (2 * a)
        takeoff_parameter_2 = -b - (b ** 2 - 4 * a * c) ** 0.5 / (2 * a)
        if takeoff_parameter_1 > takeoff_parameter_2:
            return takeoff_parameter_1
        else:
            return takeoff_parameter_2

    def size_to_landing(self, altitude, landing_field_length, max_landing_cl):
        stall_speed = math.sqrt(landing_field_length / 0.591477)
        return self.size_to_stall(altitude, max_landing_cl, stall_speed)

    def size_to_cruise(self, speed, altitude, cruise_lift_coefficient, mass, aspect_ratio, oswald_efficiency_factor,
                       propeller_efficiency, gear_down):
        wing_loading = list(range(1, self.max_wing_loading + 1))
        density = self.convert_altitude_to_density(altitude)
        [zero_lift_drag_coefficient, induced_drag_factor] = self.estimate_drag_polar(
            mass, altitude, speed, aspect_ratio, gear_down, oswald_efficiency_factor, cruise_lift_coefficient)
        cruise_drag_coefficient = zero_lift_drag_coefficient + induced_drag_factor * cruise_lift_coefficient ** 2
        power_loading = [((2 * propeller_efficiency) / (speed ** 3 * density * cruise_drag_coefficient)) * x
                         for x in wing_loading]
        return wing_loading, power_loading

    def size_to_climb(self, mass, altitude, speed, aspect_ratio, gear_down, oswald_efficiency_factor, cl,
                      rate_of_climb, propeller_efficiency):
        wing_loading = list(range(1, self.max_wing_loading + 1))
        zero_lift_drag_coefficient = self.estimate_drag_polar(
            mass, altitude, speed, aspect_ratio, gear_down, oswald_efficiency_factor, cl)[0]
        imperial_rate_of_climb = rate_of_climb * 196.85  # m/s to ft/min
        drag_polar_for_best_climb = self.calculate_max_rate_of_climb(
            aspect_ratio, oswald_efficiency_factor, zero_lift_drag_coefficient)
        density_ratio = self.convert_altitude_to_density(altitude) / self.convert_altitude_to_density(0)
        # Roskam Aircraft Design Part I Section 3.4.5.1
        power_loading = [(1 / 167.64) * propeller_efficiency /
                         ((imperial_rate_of_climb / 33000) + (((x / 47.8803) ** (1 / 2)) /
                                                              (19 * drag_polar_for_best_climb *
                                                               density_ratio ** (1 / 2)))) for x in wing_loading]
        return wing_loading, power_loading

    def calculate_max_rate_of_climb(self, aspect_ratio, oswald_efficiency_factor, zero_lift_drag_coefficient):
        # Roskam Aircraft Design Part I Equation 3.27
        return (1.345 * (aspect_ratio * oswald_efficiency_factor) ** (3 / 4)) / (zero_lift_drag_coefficient ** (1 / 4))

    def estimate_drag_polar(self, mass, altitude, speed, aspect_ratio, gear_down, oswald_efficiency_factor, cl):
        zero_lift_drag_coefficient = self.calculate_zero_lift_drag_coefficient(mass, altitude, speed, cl, gear_down)
        induced_drag_factor = self.calculate_induced_drag_factor(aspect_ratio, oswald_efficiency_factor)
        return [zero_lift_drag_coefficient, induced_drag_factor]

    def calculate_zero_lift_drag_coefficient(self, mass, altitude, speed, cl, gear_down):
        equivalent_parasite_area = self.calculate_equivalent_parasite_area(mass, altitude, speed)
        wing_planform_area = self.estimate_wing_planform_area(mass, altitude, speed, cl)
        zero_lift_drag_coefficient = equivalent_parasite_area / wing_planform_area
        if gear_down is True:
            zero_lift_drag_coefficient += 0.02
        else:
            pass
        return round(zero_lift_drag_coefficient, 6)

    def calculate_induced_drag_factor(self, aspect_ratio, oswald_efficiency_factor):
        return round(1 / (math.pi * aspect_ratio * oswald_efficiency_factor), 6)

    def estimate_wing_planform_area(self, mass, altitude, speed, cl):
        weight = mass * 9.80665
        return weight / self.estimate_wing_loading(altitude, speed, cl)

    def estimate_wing_loading(self, altitude, speed, cl):
        return cl * self.convert_altitude_to_density(altitude) * speed ** 2 / 2

    def calculate_equivalent_parasite_area(self, mass, altitude, speed):
        cf = self.estimate_skin_friction_coefficient(altitude, mass, speed)
        imperial_wetted_planform = self.calculate_imperial_wetted_planform(mass)
        if cf == 0.002:
            return 0.09290304 * 10 ** (math.log10(imperial_wetted_planform) - 2.6990)
        elif cf == 0.003:
            return 0.09290304 * 10 ** (math.log10(imperial_wetted_planform) - 2.5229)
        elif cf == 0.004:
            return 0.09290304 * 10 ** (math.log10(imperial_wetted_planform) - 2.3979)
        elif cf == 0.005:
            return 0.09290304 * 10 ** (math.log10(imperial_wetted_planform) - 2.3010)
        elif cf == 0.006:
            return 0.09290304 * 10 ** (math.log10(imperial_wetted_planform) - 2.2218)
        elif cf == 0.007:
            return 0.09290304 * 10 ** (math.log10(imperial_wetted_planform) - 2.1549)
        elif cf == 0.008:
            return 0.09290304 * 10 ** (math.log10(imperial_wetted_planform) - 2.0969)
        elif cf == 0.009:
            return 0.09290304 * 10 ** (math.log10(imperial_wetted_planform) - 2.0458)
        else:
            raise ValueError("cf must be an exact value between 0.002 and 0.009 in increments of 0.001!")

    def estimate_skin_friction_coefficient(self, altitude, mass, speed):
        # Nicolai Chapter 2 Review of Practical Aerodynamics Fig. 2.6
        if self.calculate_reynolds_number(altitude, mass, speed) < 500000:
            return round(1.328 / math.sqrt(self.calculate_reynolds_number(altitude, mass, speed)), 3)
        else:
            return round(0.455 / (math.log10(self.calculate_reynolds_number(altitude, mass, speed)) ** 2.58), 3)

    def calculate_imperial_wetted_planform(self, mass, aircraft_type='Homebuilt'):
        if aircraft_type == 'Homebuilt':
            c = 1.2362
            d = 0.4319
        else:
            raise NameError  # Eventually incorporate all of Roskam's plane types, but currently only homebuilt aircraft
        imperial_weight = mass / 0.453592
        return 10 ** (c + d * math.log10(imperial_weight))  # Roskam Eq. 3.22

    def calculate_reynolds_number(self, altitude, mass, speed):
        length = self.convert_takeoff_mass_to_length(mass)
        density = self.convert_altitude_to_density(altitude)
        viscosity = self.calculate_dynamic_viscosity(altitude)
        return density * speed * length / viscosity

    def convert_takeoff_mass_to_length(self, takeoff_mass):
        return 10 ** (0.393171 * math.log10(takeoff_mass) - 0.313193)  # Self built database with strong correlation

    def calculate_dynamic_viscosity(self, altitude):
        potential_viscosity = -0.0000000003325805 * altitude + 0.00001792696
        if potential_viscosity < 0.00001422:
            return 0.00001422
        else:
            return potential_viscosity
