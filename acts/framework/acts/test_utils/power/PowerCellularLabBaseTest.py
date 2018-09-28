#!/usr/bin/env python3.4
#
#   Copyright 2018 - The Android Open Source Project
#
#   Licensed under the Apache License, Version 2.0 (the 'License');
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an 'AS IS' BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import acts.test_utils.power.PowerBaseTest as PBT
from acts.controllers.anritsu_lib._anritsu_utils import AnritsuError
from acts.controllers.anritsu_lib.md8475a import MD8475A
from acts.test_utils.power.tel_simulations.GsmSimulation import GsmSimulation
from acts.test_utils.power.tel_simulations.LteSimulation import LteSimulation
from acts.test_utils.power.tel_simulations.UmtsSimulation import UmtsSimulation


class PowerCellularLabBaseTest(PBT.PowerBaseTest):
    """ Base class for Cellular power related tests.

    Inherits from PowerBaseTest so it has methods to collect power measurements.
    On top of that, it provides functions to setup and control the Anritsu simulation.

    """

    # List of test name keywords that indicate the RAT to be used

    PARAM_SIM_TYPE_LTE = "lte"
    PARAM_SIM_TYPE_UMTS = "umts"
    PARAM_SIM_TYPE_GSM = "gsm"

    def __init__(self, controllers):
        """ Class initialization.

        Sets class attributes to None.
        """

        super().__init__(controllers)

        # Tests are sorted alphabetically so all the tests in the same band are grouped together
        self.tests = sorted(self.tests)

        self.simulation = None
        self.anritsu = None

    def setup_class(self):
        """ Executed before any test case is started.

        Sets the device to rockbottom and connects to the anritsu callbox.

        Returns:
            False if connecting to the callbox fails.
        """

        super().setup_class()
        if hasattr(self, 'network_file'):
            self.networks = self.unpack_custom_file(self.network_file, False)
            self.main_network = self.networks['main_network']
            self.aux_network = self.networks['aux_network']
        if hasattr(self, 'packet_senders'):
            self.pkt_sender = self.packet_senders[0]

        # Set DUT to rockbottom
        self.dut_rockbottom()

        # Establish connection to Anritsu Callbox
        return self.connect_to_anritsu()

    def connect_to_anritsu(self):
        """ Connects to Anritsu Callbox and gets handle object.

        Returns:
            False if a connection with the callbox could not be started
        """

        try:
            self.anritsu = MD8475A(self.md8475a_ip_address, self.log,
                                   self.wlan_option)
            return True
        except AnritsuError:
            self.log.error('Error in connecting to Anritsu Callbox')
            return False

    def setup_test(self):
        """ Executed before every test case.

        Parses parameters from the test name and sets a simulation up according to those values.
        Also takes care of attaching the phone to the base station. Because starting new simulations
        and recalibrating takes some time, the same simulation object is kept between tests and is only
        destroyed and re instantiated in case the RAT is different from the previous tests.

        Children classes need to call the parent method first. This method will create the list self.parameters
        with the keywords separated by underscores in the test name and will remove the ones that were consumed
        for the simulation config. The setup_test methods in the children classes can then consume the remaining
        values.
        """

        # Get list of parameters from the test name
        self.parameters = self.current_test_name.split('_')

        # Remove the 'test' keyword
        self.parameters.remove('test')

        # Changing cell parameters requires the phone to be detached
        if self.simulation:
            self.simulation.stop()

        # Decide what type of simulation and instantiate it if needed
        if self.consume_parameter(self.PARAM_SIM_TYPE_LTE):
            self.init_simulation(self.PARAM_SIM_TYPE_LTE)
        elif self.consume_parameter(self.PARAM_SIM_TYPE_UMTS):
            self.init_simulation(self.PARAM_SIM_TYPE_UMTS)
        elif self.consume_parameter(self.PARAM_SIM_TYPE_GSM):
            self.init_simulation(self.PARAM_SIM_TYPE_GSM)
        else:
            self.log.error("Simulation type needs to be indicated in the test name.")
            return False

        # Parse simulation parameters
        if not self.simulation.parse_parameters(self.parameters):
            return False

        # Attach the phone to the basestation
        self.simulation.start()

        # Make the device go to sleep
        self.dut.droid.goToSleepNow()

        return True

    def consume_parameter(self, parameter_name, num_values=0):
        """ Parses a parameter from the test name.

        Allows the test to get parameters from its name. Will delete parameters from the list after
        consuming them to ensure that they are not used twice.

        Args:
          parameter_name: keyword to look up in the test name
          num_values: number of arguments following the parameter name in the test name
        Returns:
          A list containing the parameter name and the following num_values arguments
        """

        try:
            i = self.parameters.index(parameter_name)
        except ValueError:
            # parameter_name is not set
            return []

        return_list = []

        try:
            for j in range(num_values+1):
                return_list.append(self.parameters.pop(i))
        except IndexError:
            self.log.error("Parameter {} has to be followed by {} values.".format(parameter_name, num_values))
            raise ValueError()

        return return_list


    def teardown_class(self):
        """Clean up the test class after tests finish running.

        Stop the simulation and then disconnect from the Anritsu Callbox.

        """
        super().teardown_class()

        if self.anritsu:
            self.anritsu.stop_simulation()
            self.anritsu.disconnect()

    def init_simulation(self, sim_type):
        """ Starts a new simulation only if needed.

        Only starts a new simulation if type is different from the one running before.

        Args:
            type: defines the type of simulation to be started.
        """

        if sim_type == self.PARAM_SIM_TYPE_LTE:

            if self.simulation and type(self.simulation) is LteSimulation:
                # The simulation object we already have is enough.
                return

            # Instantiate a new simulation
            self.simulation = LteSimulation(self.anritsu, self.log, self.dut)

        elif sim_type == self.PARAM_SIM_TYPE_UMTS:

            if self.simulation and type(self.simulation) is UmtsSimulation:
                return

            self.simulation = UmtsSimulation(self.anritsu, self.log, self.dut)

        elif sim_type == self.PARAM_SIM_TYPE_GSM:

            if self.simulation and type(self.simulation) is GsmSimulation:
                return

            self.simulation = GsmSimulation(self.anritsu, self.log, self.dut)
