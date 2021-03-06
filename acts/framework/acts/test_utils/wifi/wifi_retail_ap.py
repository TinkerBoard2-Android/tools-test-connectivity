#!/usr/bin/env python3
#
#   Copyright 2017 - The Android Open Source Project
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import fcntl
import os
import selenium
import splinter
import time
from acts import logger
from acts.controllers import access_point
from acts.controllers.ap_lib import bridge_interface
from acts.controllers.ap_lib import hostapd_security
from acts.controllers.ap_lib import hostapd_ap_preset

BROWSER_WAIT_SHORT = 1
BROWSER_WAIT_MED = 3
BROWSER_WAIT_LONG = 30
BROWSER_WAIT_EXTRA_LONG = 60


def create(configs):
    """Factory method for retail AP class.

    Args:
        configs: list of dicts containing ap settings. ap settings must contain
        the following: brand, model, ip_address, username and password
    """
    SUPPORTED_APS = {
        ("Netgear", "R7000"): "NetgearR7000AP",
        ("Netgear", "R7000NA"): "NetgearR7000NAAP",
        ("Netgear", "R7500"): "NetgearR7500AP",
        ("Netgear", "R7800"): "NetgearR7800AP",
        ("Netgear", "R8000"): "NetgearR8000AP",
        ("Netgear", "R8500"): "NetgearR8500AP",
        ("Google", "Wifi"): "GoogleWifiAP"
    }
    objs = []
    for config in configs:
        try:
            ap_class_name = SUPPORTED_APS[(config["brand"], config["model"])]
            ap_class = globals()[ap_class_name]
        except KeyError:
            raise KeyError("Invalid retail AP brand and model combination.")
        objs.append(ap_class(config))
    return objs


def detroy(objs):
    return


class BlockingBrowser(splinter.driver.webdriver.chrome.WebDriver):
    """Class that implements a blocking browser session on top of selenium.

    The class inherits from and builds upon splinter/selenium's webdriver class
    and makes sure that only one such webdriver is active on a machine at any
    single time. The class ensures single session operation using a lock file.
    The class is to be used within context managers (e.g. with statements) to
    ensure locks are always properly released.
    """
    def __init__(self, headless, timeout):
        """Constructor for BlockingBrowser class.

        Args:
            headless: boolean to control visible/headless browser operation
            timeout: maximum time allowed to launch browser
        """
        self.log = logger.create_tagged_trace_logger("ChromeDriver")
        self.chrome_options = splinter.driver.webdriver.chrome.Options()
        self.chrome_options.add_argument("--no-proxy-server")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--allow-running-insecure-content")
        self.chrome_options.add_argument("--ignore-certificate-errors")
        self.chrome_capabilities = selenium.webdriver.common.desired_capabilities.DesiredCapabilities.CHROME.copy(
        )
        self.chrome_capabilities["acceptSslCerts"] = True
        self.chrome_capabilities["acceptInsecureCerts"] = True
        if headless:
            self.chrome_options.add_argument("--headless")
            self.chrome_options.add_argument("--disable-gpu")
        self.lock_file_path = "/usr/local/bin/chromedriver"
        self.timeout = timeout

    def __enter__(self):
        """Entry context manager for BlockingBrowser.

        The enter context manager for BlockingBrowser attempts to lock the
        browser file. If successful, it launches and returns a chromedriver
        session. If an exception occurs while starting the browser, the lock
        file is released.
        """
        self.lock_file = open(self.lock_file_path, "r")
        start_time = time.time()
        while time.time() < start_time + self.timeout:
            try:
                fcntl.flock(self.lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                time.sleep(BROWSER_WAIT_SHORT)
                continue
            try:
                self.driver = selenium.webdriver.Chrome(
                    options=self.chrome_options,
                    desired_capabilities=self.chrome_capabilities)
                self.element_class = splinter.driver.webdriver.WebDriverElement
                self._cookie_manager = splinter.driver.webdriver.cookie_manager.CookieManager(
                    self.driver)
                super(splinter.driver.webdriver.chrome.WebDriver,
                      self).__init__(2)
                return super(BlockingBrowser, self).__enter__()
            except:
                fcntl.flock(self.lock_file, fcntl.LOCK_UN)
                self.lock_file.close()
                raise RuntimeError("Error starting browser. "
                                   "Releasing lock file.")
        raise TimeoutError("Could not start chrome browser in time.")

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit context manager for BlockingBrowser.

        The exit context manager simply calls the parent class exit and
        releases the lock file.
        """
        try:
            super(BlockingBrowser, self).__exit__(exc_type, exc_value,
                                                  traceback)
        except:
            raise RuntimeError("Failed to quit browser. Releasing lock file.")
        finally:
            fcntl.flock(self.lock_file, fcntl.LOCK_UN)
            self.lock_file.close()

    def restart(self):
        """Method to restart browser session without releasing lock file."""
        self.quit()
        self.__enter__()

    def visit_persistent(self,
                         url,
                         page_load_timeout,
                         num_tries,
                         backup_url="about:blank",
                         check_for_element=None):
        """Method to visit webpages and retry upon failure.

        The function visits a web page and checks the the resulting URL matches
        the intended URL, i.e. no redirects have happened

        Args:
            url: the intended url
            page_load_timeout: timeout for page visits
            num_tries: number of tries before url is declared unreachable
            backup_url: url to visit if first url is not reachable. This can be
            used to simply refresh the browser and try again or to re-login to
            the AP
            check_for_element: element id to check for existence on page
        """
        self.driver.set_page_load_timeout(page_load_timeout)
        for idx in range(num_tries):
            try:
                self.visit(url)
            except:
                self.restart()

            page_reached = self.url.split("/")[-1] == url.split("/")[-1]
            if check_for_element:
                time.sleep(BROWSER_WAIT_MED)
                element = self.find_by_id(check_for_element)
                if not element:
                    page_reached = 0
            if page_reached:
                break
            else:
                try:
                    self.visit(backup_url)
                except:
                    self.restart()

            if idx == num_tries - 1:
                self.log.error("URL unreachable. Current URL: {}".format(
                    self.url))
                raise RuntimeError("URL unreachable.")


class WifiRetailAP(object):
    """Base class implementation for retail ap.

    Base class provides functions whose implementation is shared by all aps.
    If some functions such as set_power not supported by ap, checks will raise
    exceptions.
    """
    def __init__(self, ap_settings):
        self.ap_settings = ap_settings.copy()
        self.log = logger.create_tagged_trace_logger("AccessPoint|{}".format(
            self._get_control_ip_address()))
        # Lock AP
        if self.ap_settings.get('lock_ap', 0):
            self.lock_timeout = self.ap_settings.get('lock_timeout', 3600)
            self._lock_ap()

    def read_ap_settings(self):
        """Function that reads current ap settings.

        Function implementation is AP dependent and thus base class raises exception
        if function not implemented in child class.
        """
        raise NotImplementedError

    def validate_ap_settings(self):
        """Function to validate ap settings.

        This function compares the actual ap settings read from the web GUI
        with the assumed settings saved in the AP object. When called after AP
        configuration, this method helps ensure that our configuration was
        successful.
        Note: Calling this function updates the stored ap_settings

        Raises:
            ValueError: If read AP settings do not match stored settings.
        """
        assumed_ap_settings = self.ap_settings.copy()
        actual_ap_settings = self.read_ap_settings()
        if assumed_ap_settings != actual_ap_settings:
            self.log.warning(
                "Discrepancy in AP settings. Some settings may have been overwritten."
            )

    def configure_ap(self, **config_flags):
        """Function that configures ap based on values of ap_settings.

        Function implementation is AP dependent and thus base class raises exception
        if function not implemented in child class.

        Args:
            config_flags: optional configuration flags
        """
        raise NotImplementedError

    def set_region(self, region):
        """Function that sets AP region.

        This function sets the region for the AP. Note that this may overwrite
        channel and bandwidth settings in cases where the new region does not
        support the current wireless configuration.

        Args:
            region: string indicating AP region
        """
        self.log.warning("Updating region may overwrite wireless settings.")
        setting_to_update = {"region": region}
        self.update_ap_settings(setting_to_update)

    def set_radio_on_off(self, network, status):
        """Function that turns the radio on or off.

        Args:
            network: string containing network identifier (2G, 5G_1, 5G_2)
            status: boolean indicating on or off (0: off, 1: on)
        """
        setting_to_update = {"status_{}".format(network): int(status)}
        self.update_ap_settings(setting_to_update)

    def set_ssid(self, network, ssid):
        """Function that sets network SSID.

        Args:
            network: string containing network identifier (2G, 5G_1, 5G_2)
            ssid: string containing ssid
        """
        setting_to_update = {"ssid_{}".format(network): str(ssid)}
        self.update_ap_settings(setting_to_update)

    def set_channel(self, network, channel):
        """Function that sets network channel.

        Args:
            network: string containing network identifier (2G, 5G_1, 5G_2)
            channel: string or int containing channel
        """
        setting_to_update = {"channel_{}".format(network): str(channel)}
        self.update_ap_settings(setting_to_update)

    def set_bandwidth(self, network, bandwidth):
        """Function that sets network bandwidth/mode.

        Args:
            network: string containing network identifier (2G, 5G_1, 5G_2)
            bandwidth: string containing mode, e.g. 11g, VHT20, VHT40, VHT80.
        """
        setting_to_update = {"bandwidth_{}".format(network): str(bandwidth)}
        self.update_ap_settings(setting_to_update)

    def set_power(self, network, power):
        """Function that sets network transmit power.

        Args:
            network: string containing network identifier (2G, 5G_1, 5G_2)
            power: string containing power level, e.g., 25%, 100%
        """
        setting_to_update = {"power_{}".format(network): str(power)}
        self.update_ap_settings(setting_to_update)

    def set_security(self, network, security_type, *password):
        """Function that sets network security setting and password.

        Args:
            network: string containing network identifier (2G, 5G_1, 5G_2)
            security: string containing security setting, e.g., WPA2-PSK
            password: optional argument containing password
        """
        if (len(password) == 1) and (type(password[0]) == str):
            setting_to_update = {
                "security_type_{}".format(network): str(security_type),
                "password_{}".format(network): str(password[0])
            }
        else:
            setting_to_update = {
                "security_type_{}".format(network): str(security_type)
            }
        self.update_ap_settings(setting_to_update)

    def set_rate(self):
        """Function that configures rate used by AP.

        Function implementation is not supported by most APs and thus base
        class raises exception if function not implemented in child class.
        """
        raise NotImplementedError

    def update_ap_settings(self, dict_settings={}, **named_settings):
        """Function to update settings of existing AP.

        Function copies arguments into ap_settings and calls configure_retail_ap
        to apply them.

        Args:
            *dict_settings accepts single dictionary of settings to update
            **named_settings accepts named settings to update
            Note: dict and named_settings cannot contain the same settings.
        """
        settings_to_update = dict(dict_settings, **named_settings)
        if len(settings_to_update) != len(dict_settings) + len(named_settings):
            raise KeyError("The following keys were passed twice: {}".format(
                (set(dict_settings.keys()).intersection(
                    set(named_settings.keys())))))
        if not set(settings_to_update.keys()).issubset(
                set(self.ap_settings.keys())):
            raise KeyError(
                "The following settings are invalid for this AP: {}".format(
                    set(settings_to_update.keys()).difference(
                        set(self.ap_settings.keys()))))

        updates_requested = False
        status_toggle_flag = False
        for setting, value in settings_to_update.items():
            if self.ap_settings[setting] != value:
                self.ap_settings[setting] = value
                if "status" in setting:
                    status_toggle_flag = True
                updates_requested = True

        if updates_requested:
            self.configure_ap(status_toggled=status_toggle_flag)

    def band_lookup_by_channel(self, channel):
        """Function that gives band name by channel number.

        Args:
            channel: channel number to lookup
        Returns:
            band: name of band which this channel belongs to on this ap
        """
        for key, value in self.channel_band_map.items():
            if channel in value:
                return key
        raise ValueError("Invalid channel passed in argument.")

    def _get_control_ip_address(self):
        """Function to get AP's Control Interface IP address."""
        if "ssh_config" in self.ap_settings.keys():
            return self.ap_settings["ssh_config"]["host"]
        else:
            return self.ap_settings["ip_address"]

    def _lock_ap(self):
        """Function to lock the ap while tests are running."""
        self.lock_file_path = "/tmp/{}_{}_{}.lock".format(
            self.ap_settings['brand'], self.ap_settings['model'],
            self._get_control_ip_address())
        if not os.path.exists(self.lock_file_path):
            with open(self.lock_file_path, 'w'):
                pass
        self.lock_file = open(self.lock_file_path, "r")
        start_time = time.time()
        self.log.info('Trying to acquire AP lock.')
        while time.time() < start_time + self.lock_timeout:
            try:
                fcntl.flock(self.lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                time.sleep(BROWSER_WAIT_SHORT)
                continue
            self.log.info('AP lock acquired.')
            return
        raise RuntimeError("Could not lock AP in time.")

    def _unlock_ap(self):
        """Function to unlock the AP when tests are done."""
        self.log.info('Releasing AP lock.')
        if hasattr(self, "lock_file"):
            fcntl.flock(self.lock_file, fcntl.LOCK_UN)
            self.lock_file.close()


class NetgearR7000AP(WifiRetailAP):
    """Class that implements Netgear R7500 AP."""
    def __init__(self, ap_settings):
        super().__init__(ap_settings)
        self.init_gui_data()
        # Read and update AP settings
        self.read_ap_settings()
        if not set(ap_settings.items()).issubset(self.ap_settings.items()):
            self.update_ap_settings(ap_settings)

    def init_gui_data(self):
        """Function to initialize data used while interacting with web GUI"""
        self.config_page = (
            "{protocol}://{username}:{password}@"
            "{ip_address}:{port}/WLG_wireless_dual_band_r10.htm").format(
                protocol=self.ap_settings["protocol"],
                username=self.ap_settings["admin_username"],
                password=self.ap_settings["admin_password"],
                ip_address=self.ap_settings["ip_address"],
                port=self.ap_settings["port"])
        self.config_page_nologin = (
            "{protocol}://{ip_address}:{port}/"
            "WLG_wireless_dual_band_r10.htm").format(
                protocol=self.ap_settings["protocol"],
                ip_address=self.ap_settings["ip_address"],
                port=self.ap_settings["port"])
        self.config_page_advanced = (
            "{protocol}://{username}:{password}@"
            "{ip_address}:{port}/WLG_adv_dual_band2.htm").format(
                protocol=self.ap_settings["protocol"],
                username=self.ap_settings["admin_username"],
                password=self.ap_settings["admin_password"],
                ip_address=self.ap_settings["ip_address"],
                port=self.ap_settings["port"])
        self.networks = ["2G", "5G_1"]
        self.channel_band_map = {
            "2G": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
            "5G_1": [
                36, 40, 44, 48, 52, 56, 60, 64, 100, 104, 108, 112, 116, 120,
                124, 128, 132, 136, 140, 149, 153, 157, 161, 165
            ]
        }
        self.region_map = {
            "1": "Africa",
            "2": "Asia",
            "3": "Australia",
            "4": "Canada",
            "5": "Europe",
            "6": "Israel",
            "7": "Japan",
            "8": "Korea",
            "9": "Mexico",
            "10": "South America",
            "11": "United States",
            "12": "Middle East(Algeria/Syria/Yemen)",
            "14": "Russia",
            "16": "China",
            "17": "India",
            "18": "Malaysia",
            "19": "Middle East(Iran/Labanon/Qatar)",
            "20": "Middle East(Turkey/Egypt/Tunisia/Kuwait)",
            "21": "Middle East(Saudi Arabia)",
            "22": "Middle East(United Arab Emirates)",
            "23": "Singapore",
            "24": "Taiwan"
        }
        self.config_page_fields = {
            "region": "WRegion",
            ("2G", "status"): "enable_ap",
            ("5G_1", "status"): "enable_ap_an",
            ("2G", "ssid"): "ssid",
            ("5G_1", "ssid"): "ssid_an",
            ("2G", "channel"): "w_channel",
            ("5G_1", "channel"): "w_channel_an",
            ("2G", "bandwidth"): "opmode",
            ("5G_1", "bandwidth"): "opmode_an",
            ("2G", "power"): "enable_tpc",
            ("5G_1", "power"): "enable_tpc_an",
            ("2G", "security_type"): "security_type",
            ("5G_1", "security_type"): "security_type_an",
            ("2G", "password"): "passphrase",
            ("5G_1", "password"): "passphrase_an"
        }
        self.bw_mode_values = {
            "g and b": "11g",
            "145Mbps": "VHT20",
            "300Mbps": "VHT40",
            "HT80": "VHT80"
        }
        self.power_mode_values = {
            "1": "100%",
            "2": "75%",
            "3": "50%",
            "4": "25%"
        }
        self.bw_mode_text = {
            "11g": "Up to 54 Mbps",
            "VHT20": "Up to 289 Mbps",
            "VHT40": "Up to 600 Mbps",
            "VHT80": "Up to 1300 Mbps"
        }

    def read_ap_settings(self):
        """Function to read ap settings."""
        with BlockingBrowser(self.ap_settings["headless_browser"],
                             900) as browser:
            # Visit URL
            browser.visit_persistent(self.config_page, BROWSER_WAIT_MED, 10)

            for key, value in self.config_page_fields.items():
                if "status" in key:
                    browser.visit_persistent(self.config_page_advanced,
                                             BROWSER_WAIT_MED, 10)
                    config_item = browser.find_by_name(value)
                    self.ap_settings["{}_{}".format(key[1], key[0])] = int(
                        config_item.first.checked)
                    browser.visit_persistent(self.config_page,
                                             BROWSER_WAIT_MED, 10)
                else:
                    config_item = browser.find_by_name(value)
                    if "bandwidth" in key:
                        self.ap_settings["{}_{}".format(
                            key[1], key[0])] = self.bw_mode_values[
                                config_item.first.value]
                    elif "power" in key:
                        self.ap_settings["{}_{}".format(
                            key[1], key[0])] = self.power_mode_values[
                                config_item.first.value]
                    elif "region" in key:
                        self.ap_settings["region"] = self.region_map[
                            config_item.first.value]
                    elif "security_type" in key:
                        for item in config_item:
                            if item.checked:
                                self.ap_settings["{}_{}".format(
                                    key[1], key[0])] = item.value
                    else:
                        config_item = browser.find_by_name(value)
                        self.ap_settings["{}_{}".format(
                            key[1], key[0])] = config_item.first.value
        return self.ap_settings.copy()

    def configure_ap(self, **config_flags):
        """Function to configure ap wireless settings."""
        # Turn radios on or off
        if config_flags["status_toggled"]:
            self.configure_radio_on_off()
        # Configure radios
        with BlockingBrowser(self.ap_settings["headless_browser"],
                             900) as browser:
            # Visit URL
            browser.visit_persistent(self.config_page, BROWSER_WAIT_MED, 10)
            browser.visit_persistent(self.config_page_nologin,
                                     BROWSER_WAIT_MED, 10, self.config_page)

            # Update region, and power/bandwidth for each network
            config_item = browser.find_by_name(
                self.config_page_fields["region"]).first
            config_item.select_by_text(self.ap_settings["region"])
            for key, value in self.config_page_fields.items():
                if "power" in key:
                    config_item = browser.find_by_name(value).first
                    config_item.select_by_text(self.ap_settings["{}_{}".format(
                        key[1], key[0])])
                elif "bandwidth" in key:
                    config_item = browser.find_by_name(value).first
                    try:
                        config_item.select_by_text(
                            self.bw_mode_text[self.ap_settings["{}_{}".format(
                                key[1], key[0])]])
                    except AttributeError:
                        self.log.warning(
                            "Cannot select bandwidth. Keeping AP default.")

            # Update security settings (passwords updated only if applicable)
            for key, value in self.config_page_fields.items():
                if "security_type" in key:
                    browser.choose(
                        value, self.ap_settings["{}_{}".format(key[1],
                                                               key[0])])
                    if self.ap_settings["{}_{}".format(key[1],
                                                       key[0])] == "WPA2-PSK":
                        config_item = browser.find_by_name(
                            self.config_page_fields[(key[0],
                                                     "password")]).first
                        config_item.fill(self.ap_settings["{}_{}".format(
                            "password", key[0])])

            # Update SSID and channel for each network
            # NOTE: Update ordering done as such as workaround for R8000
            # wherein channel and SSID get overwritten when some other
            # variables are changed. However, region does have to be set before
            # channel in all cases.
            for key, value in self.config_page_fields.items():
                if "ssid" in key:
                    config_item = browser.find_by_name(value).first
                    config_item.fill(self.ap_settings["{}_{}".format(
                        key[1], key[0])])
                elif "channel" in key:
                    config_item = browser.find_by_name(value).first
                    try:
                        config_item.select(self.ap_settings["{}_{}".format(
                            key[1], key[0])])
                        time.sleep(BROWSER_WAIT_SHORT)
                    except AttributeError:
                        self.log.warning(
                            "Cannot select channel. Keeping AP default.")
                    try:
                        alert = browser.get_alert()
                        alert.accept()
                    except:
                        pass

            time.sleep(BROWSER_WAIT_SHORT)
            browser.find_by_name("Apply").first.click()
            time.sleep(BROWSER_WAIT_SHORT)
            try:
                alert = browser.get_alert()
                alert.accept()
                time.sleep(BROWSER_WAIT_SHORT)
            except:
                time.sleep(BROWSER_WAIT_SHORT)
            browser.visit_persistent(self.config_page, BROWSER_WAIT_EXTRA_LONG,
                                     10)

    def configure_radio_on_off(self):
        """Helper configuration function to turn radios on/off."""
        with BlockingBrowser(self.ap_settings["headless_browser"],
                             900) as browser:
            # Visit URL
            browser.visit_persistent(self.config_page, BROWSER_WAIT_MED, 10)
            browser.visit_persistent(self.config_page_advanced,
                                     BROWSER_WAIT_MED, 10)

            # Turn radios on or off
            for key, value in self.config_page_fields.items():
                if "status" in key:
                    config_item = browser.find_by_name(value).first
                    if self.ap_settings["{}_{}".format(key[1], key[0])]:
                        config_item.check()
                    else:
                        config_item.uncheck()

            time.sleep(BROWSER_WAIT_SHORT)
            browser.find_by_name("Apply").first.click()
            time.sleep(BROWSER_WAIT_EXTRA_LONG)
            browser.visit_persistent(self.config_page, BROWSER_WAIT_EXTRA_LONG,
                                     10)


class NetgearR7000NAAP(NetgearR7000AP):
    """Class that implements Netgear R7000 NA AP."""
    def init_gui_data(self):
        """Function to initialize data used while interacting with web GUI"""
        super.init_gui_data()
        self.region_map["11"] = "North America"


class NetgearR7500AP(WifiRetailAP):
    """Class that implements Netgear R7500 AP."""
    def __init__(self, ap_settings):
        super().__init__(ap_settings)
        self.init_gui_data()
        # Read and update AP settings
        self.read_ap_settings()
        if not set(ap_settings.items()).issubset(self.ap_settings.items()):
            self.update_ap_settings(ap_settings)

    def init_gui_data(self):
        """Function to initialize data used while interacting with web GUI"""
        self.config_page = ("{protocol}://{username}:{password}@"
                            "{ip_address}:{port}/index.htm").format(
                                protocol=self.ap_settings["protocol"],
                                username=self.ap_settings["admin_username"],
                                password=self.ap_settings["admin_password"],
                                ip_address=self.ap_settings["ip_address"],
                                port=self.ap_settings["port"])
        self.config_page_advanced = (
            "{protocol}://{username}:{password}@"
            "{ip_address}:{port}/adv_index.htm").format(
                protocol=self.ap_settings["protocol"],
                username=self.ap_settings["admin_username"],
                password=self.ap_settings["admin_password"],
                ip_address=self.ap_settings["ip_address"],
                port=self.ap_settings["port"])
        self.networks = ["2G", "5G_1"]
        self.channel_band_map = {
            "2G": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
            "5G_1": [
                36, 40, 44, 48, 52, 56, 60, 64, 100, 104, 108, 112, 116, 120,
                124, 128, 132, 136, 140, 149, 153, 157, 161, 165
            ]
        }
        self.config_page_fields = {
            "region": "WRegion",
            ("2G", "status"): "enable_ap",
            ("5G_1", "status"): "enable_ap_an",
            ("2G", "ssid"): "ssid",
            ("5G_1", "ssid"): "ssid_an",
            ("2G", "channel"): "w_channel",
            ("5G_1", "channel"): "w_channel_an",
            ("2G", "bandwidth"): "opmode",
            ("5G_1", "bandwidth"): "opmode_an",
            ("2G", "security_type"): "security_type",
            ("5G_1", "security_type"): "security_type_an",
            ("2G", "password"): "passphrase",
            ("5G_1", "password"): "passphrase_an"
        }
        self.region_map = {
            "0": "Africa",
            "1": "Asia",
            "2": "Australia",
            "3": "Canada",
            "4": "Europe",
            "5": "Israel",
            "6": "Japan",
            "7": "Korea",
            "8": "Mexico",
            "9": "South America",
            "10": "United States",
            "11": "China",
            "12": "India",
            "13": "Malaysia",
            "14": "Middle East(Algeria/Syria/Yemen)",
            "15": "Middle East(Iran/Labanon/Qatar)",
            "16": "Middle East(Turkey/Egypt/Tunisia/Kuwait)",
            "17": "Middle East(Saudi Arabia)",
            "18": "Middle East(United Arab Emirates)",
            "19": "Russia",
            "20": "Singapore",
            "21": "Taiwan"
        }
        self.bw_mode_text_2g = {
            "11g": "Up to 54 Mbps",
            "VHT20": "Up to 289 Mbps",
            "VHT40": "Up to 600 Mbps"
        }
        self.bw_mode_text_5g = {
            "VHT20": "Up to 347 Mbps",
            "VHT40": "Up to 800 Mbps",
            "VHT80": "Up to 1733 Mbps"
        }
        self.bw_mode_values = {
            "1": "11g",
            "2": "VHT20",
            "3": "VHT40",
            "7": "VHT20",
            "8": "VHT40",
            "9": "VHT80"
        }

    def read_ap_settings(self):
        """Function to read ap wireless settings."""
        # Get radio status (on/off)
        self.read_radio_on_off()
        # Get radio configuration. Note that if both radios are off, the below
        # code will result in an error
        with BlockingBrowser(self.ap_settings["headless_browser"],
                             900) as browser:
            browser.visit_persistent(self.config_page,
                                     BROWSER_WAIT_MED,
                                     10,
                                     check_for_element="wireless")
            wireless_button = browser.find_by_id("wireless").first
            wireless_button.click()
            time.sleep(BROWSER_WAIT_MED)

            with browser.get_iframe("formframe") as iframe:
                for key, value in self.config_page_fields.items():
                    if "bandwidth" in key:
                        config_item = iframe.find_by_name(value).first
                        self.ap_settings["{}_{}".format(
                            key[1],
                            key[0])] = self.bw_mode_values[config_item.value]
                    elif "region" in key:
                        config_item = iframe.find_by_name(value).first
                        self.ap_settings["region"] = self.region_map[
                            config_item.value]
                    elif "password" in key:
                        try:
                            config_item = iframe.find_by_name(value).first
                            self.ap_settings["{}_{}".format(
                                key[1], key[0])] = config_item.value
                            self.ap_settings["{}_{}".format(
                                "security_type", key[0])] = "WPA2-PSK"
                        except:
                            self.ap_settings["{}_{}".format(
                                key[1], key[0])] = "defaultpassword"
                            self.ap_settings["{}_{}".format(
                                "security_type", key[0])] = "Disable"
                    elif ("channel" in key) or ("ssid" in key):
                        config_item = iframe.find_by_name(value).first
                        self.ap_settings["{}_{}".format(
                            key[1], key[0])] = config_item.value
                    else:
                        pass
        return self.ap_settings.copy()

    def configure_ap(self, **config_flags):
        """Function to configure ap wireless settings."""
        # Turn radios on or off
        if config_flags["status_toggled"]:
            self.configure_radio_on_off()
        # Configure radios
        with BlockingBrowser(self.ap_settings["headless_browser"],
                             900) as browser:
            browser.visit_persistent(self.config_page,
                                     BROWSER_WAIT_MED,
                                     10,
                                     check_for_element="wireless")
            wireless_button = browser.find_by_id("wireless").first
            wireless_button.click()
            time.sleep(BROWSER_WAIT_MED)

            with browser.get_iframe("formframe") as iframe:
                # Update AP region. Must be done before channel setting
                config_item = iframe.find_by_name(
                    self.config_page_fields["region"]).first
                config_item.select_by_text(self.ap_settings["region"])
                # Update wireless settings for each network
                for key, value in self.config_page_fields.items():
                    if "ssid" in key:
                        config_item = iframe.find_by_name(value).first
                        config_item.fill(self.ap_settings["{}_{}".format(
                            key[1], key[0])])
                    elif "channel" in key:
                        channel_string = "0" * (int(self.ap_settings[
                            "{}_{}".format(key[1], key[0])]) < 10) + str(
                                self.ap_settings["{}_{}".format(
                                    key[1], key[0])]) + "(DFS)" * (48 < int(
                                        self.ap_settings["{}_{}".format(
                                            key[1], key[0])]) < 149)
                        config_item = iframe.find_by_name(value).first
                        try:
                            config_item.select_by_text(channel_string)
                        except AttributeError:
                            self.log.warning(
                                "Cannot select channel. Keeping AP default.")
                    elif key == ("2G", "bandwidth"):
                        config_item = iframe.find_by_name(value).first
                        try:
                            config_item.select_by_text(
                                str(self.bw_mode_text_2g[self.ap_settings[
                                    "{}_{}".format(key[1], key[0])]]))
                        except AttributeError:
                            self.log.warning(
                                "Cannot select bandwidth. Keeping AP default.")
                    elif key == ("5G_1", "bandwidth"):
                        config_item = iframe.find_by_name(value).first
                        try:
                            config_item.select_by_text(
                                str(self.bw_mode_text_5g[self.ap_settings[
                                    "{}_{}".format(key[1], key[0])]]))
                        except AttributeError:
                            self.log.warning(
                                "Cannot select bandwidth. Keeping AP default.")
                # Update passwords for WPA2-PSK protected networks
                # (Must be done after security type is selected)
                for key, value in self.config_page_fields.items():
                    if "security_type" in key:
                        iframe.choose(
                            value,
                            self.ap_settings["{}_{}".format(key[1], key[0])])
                        if self.ap_settings["{}_{}".format(
                                key[1], key[0])] == "WPA2-PSK":
                            config_item = iframe.find_by_name(
                                self.config_page_fields[(key[0],
                                                         "password")]).first
                            config_item.fill(self.ap_settings["{}_{}".format(
                                "password", key[0])])

                apply_button = iframe.find_by_name("Apply")
                apply_button[0].click()
                time.sleep(BROWSER_WAIT_SHORT)
                try:
                    alert = browser.get_alert()
                    alert.accept()
                except:
                    pass
                time.sleep(BROWSER_WAIT_SHORT)
                try:
                    alert = browser.get_alert()
                    alert.accept()
                except:
                    pass
                time.sleep(BROWSER_WAIT_SHORT)
            time.sleep(BROWSER_WAIT_EXTRA_LONG)
            browser.visit_persistent(self.config_page, BROWSER_WAIT_EXTRA_LONG,
                                     10)

    def configure_radio_on_off(self):
        """Helper configuration function to turn radios on/off."""
        with BlockingBrowser(self.ap_settings["headless_browser"],
                             900) as browser:
            browser.visit_persistent(self.config_page, BROWSER_WAIT_MED, 10)
            browser.visit_persistent(self.config_page_advanced,
                                     BROWSER_WAIT_MED,
                                     10,
                                     check_for_element="advanced_bt")
            advanced_button = browser.find_by_id("advanced_bt").first
            advanced_button.click()
            time.sleep(BROWSER_WAIT_MED)
            wireless_button = browser.find_by_id("wladv").first
            wireless_button.click()
            time.sleep(BROWSER_WAIT_MED)

            with browser.get_iframe("formframe") as iframe:
                # Turn radios on or off
                for key, value in self.config_page_fields.items():
                    if "status" in key:
                        config_item = iframe.find_by_name(value).first
                        if self.ap_settings["{}_{}".format(key[1], key[0])]:
                            config_item.check()
                        else:
                            config_item.uncheck()

                time.sleep(BROWSER_WAIT_SHORT)
                browser.find_by_name("Apply").first.click()
                time.sleep(BROWSER_WAIT_EXTRA_LONG)
                browser.visit_persistent(self.config_page,
                                         BROWSER_WAIT_EXTRA_LONG, 10)

    def read_radio_on_off(self):
        """Helper configuration function to read radio status."""
        with BlockingBrowser(self.ap_settings["headless_browser"],
                             900) as browser:
            browser.visit_persistent(self.config_page, BROWSER_WAIT_MED, 10)
            browser.visit_persistent(self.config_page_advanced,
                                     BROWSER_WAIT_MED,
                                     10,
                                     check_for_element="advanced_bt")
            advanced_button = browser.find_by_id("advanced_bt").first
            advanced_button.click()
            time.sleep(BROWSER_WAIT_SHORT)
            wireless_button = browser.find_by_id("wladv").first
            wireless_button.click()
            time.sleep(BROWSER_WAIT_MED)

            with browser.get_iframe("formframe") as iframe:
                # Turn radios on or off
                for key, value in self.config_page_fields.items():
                    if "status" in key:
                        config_item = iframe.find_by_name(value).first
                        self.ap_settings["{}_{}".format(key[1], key[0])] = int(
                            config_item.checked)


class NetgearR7800AP(NetgearR7500AP):
    """Class that implements Netgear R7800 AP.

    Since most of the class' implementation is shared with the R7500, this
    class inherits from NetgearR7500AP and simply redifines config parameters
    """
    def __init__(self, ap_settings):
        super().__init__(ap_settings)
        self.init_gui_data()
        # Overwrite minor differences from R7500 AP
        self.bw_mode_text_2g["VHT20"] = "Up to 347 Mbps"
        # Read and update AP settings
        self.read_ap_settings()
        if not set(ap_settings.items()).issubset(self.ap_settings.items()):
            self.update_ap_settings(ap_settings)


class NetgearR8000AP(NetgearR7000AP):
    """Class that implements Netgear R8000 AP.

    Since most of the class' implementation is shared with the R7000, this
    class inherits from NetgearR7000AP and simply redifines config parameters
    """
    def __init__(self, ap_settings):
        super().__init__(ap_settings)
        self.init_gui_data()
        # Overwrite minor differences from R7000 AP
        self.config_page = (
            "{protocol}://{username}:{password}@"
            "{ip_address}:{port}/WLG_wireless_dual_band_r8000.htm").format(
                protocol=self.ap_settings["protocol"],
                username=self.ap_settings["admin_username"],
                password=self.ap_settings["admin_password"],
                ip_address=self.ap_settings["ip_address"],
                port=self.ap_settings["port"])
        self.config_page_nologin = (
            "{protocol}://{ip_address}:{port}/"
            "WLG_wireless_dual_band_r8000.htm").format(
                protocol=self.ap_settings["protocol"],
                ip_address=self.ap_settings["ip_address"],
                port=self.ap_settings["port"])
        self.config_page_advanced = (
            "{protocol}://{username}:{password}@"
            "{ip_address}:{port}/WLG_adv_dual_band2_r8000.htm").format(
                protocol=self.ap_settings["protocol"],
                username=self.ap_settings["admin_username"],
                password=self.ap_settings["admin_password"],
                ip_address=self.ap_settings["ip_address"],
                port=self.ap_settings["port"])
        self.networks = ["2G", "5G_1", "5G_2"]
        self.channel_band_map = {
            "2G": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
            "5G_1": [36, 40, 44, 48],
            "5G_2": [149, 153, 157, 161, 165]
        }
        self.config_page_fields = {
            "region": "WRegion",
            ("2G", "status"): "enable_ap",
            ("5G_1", "status"): "enable_ap_an",
            ("5G_2", "status"): "enable_ap_an_2",
            ("2G", "ssid"): "ssid",
            ("5G_1", "ssid"): "ssid_an",
            ("5G_2", "ssid"): "ssid_an_2",
            ("2G", "channel"): "w_channel",
            ("5G_1", "channel"): "w_channel_an",
            ("5G_2", "channel"): "w_channel_an_2",
            ("2G", "bandwidth"): "opmode",
            ("5G_1", "bandwidth"): "opmode_an",
            ("5G_2", "bandwidth"): "opmode_an_2",
            ("2G", "security_type"): "security_type",
            ("5G_1", "security_type"): "security_type_an",
            ("5G_2", "security_type"): "security_type_an_2",
            ("2G", "password"): "passphrase",
            ("5G_1", "password"): "passphrase_an",
            ("5G_2", "password"): "passphrase_an_2"
        }
        # Read and update AP settings
        self.read_ap_settings()
        if not set(ap_settings.items()).issubset(self.ap_settings.items()):
            self.update_ap_settings(ap_settings)


class NetgearR8500AP(NetgearR7000AP):
    """Class that implements Netgear R8500 AP.

    Since most of the class' implementation is shared with the R7000, this
    class inherits from NetgearR7000AP and simply redifines config parameters
    """
    def __init__(self, ap_settings):
        super().__init__(ap_settings)
        self.init_gui_data()
        # Overwrite minor differences from R8000 AP
        self.config_page = (
            "{protocol}://{username}:{password}@"
            "{ip_address}:{port}/WLG_wireless_tri_band.htm").format(
                protocol=self.ap_settings["protocol"],
                username=self.ap_settings["admin_username"],
                password=self.ap_settings["admin_password"],
                ip_address=self.ap_settings["ip_address"],
                port=self.ap_settings["port"])
        self.config_page_nologin = (
            "{protocol}://{ip_address}:{port}/"
            "WLG_wireless_tri_band.htm").format(
                protocol=self.ap_settings["protocol"],
                ip_address=self.ap_settings["ip_address"],
                port=self.ap_settings["port"])
        self.config_page_advanced = (
            "{protocol}://{username}:{password}@"
            "{ip_address}:{port}/WLG_adv_tri_band2.htm").format(
                protocol=self.ap_settings["protocol"],
                username=self.ap_settings["admin_username"],
                password=self.ap_settings["admin_password"],
                ip_address=self.ap_settings["ip_address"],
                port=self.ap_settings["port"])
        self.networks = ["2G", "5G_1", "5G_2"]
        self.channel_band_map = {
            "2G": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
            "5G_1": [36, 40, 44, 48],
            "5G_2": [149, 153, 157, 161, 165]
        }
        self.config_page_fields = {
            "region": "WRegion",
            ("2G", "status"): "enable_ap",
            ("5G_1", "status"): "enable_ap_an",
            ("5G_2", "status"): "enable_ap_an_2",
            ("2G", "ssid"): "ssid",
            ("5G_1", "ssid"): "ssid_an",
            ("5G_2", "ssid"): "ssid_an_2",
            ("2G", "channel"): "w_channel",
            ("5G_1", "channel"): "w_channel_an",
            ("5G_2", "channel"): "w_channel_an_2",
            ("2G", "bandwidth"): "opmode",
            ("5G_1", "bandwidth"): "opmode_an",
            ("5G_2", "bandwidth"): "opmode_an_2",
            ("2G", "security_type"): "security_type",
            ("5G_1", "security_type"): "security_type_an",
            ("5G_2", "security_type"): "security_type_an_2",
            ("2G", "password"): "passphrase",
            ("5G_1", "password"): "passphrase_an",
            ("5G_2", "password"): "passphrase_an_2"
        }
        self.bw_mode_text = {
            "11g": "Up to 54 Mbps",
            "VHT20": "Up to 433 Mbps",
            "VHT40": "Up to 1000 Mbps",
            "VHT80": "Up to 2165 Mbps"
        }
        # Read and update AP settings
        self.read_ap_settings()
        if not set(ap_settings.items()).issubset(self.ap_settings.items()):
            self.update_ap_settings(ap_settings)


class GoogleWifiAP(WifiRetailAP):
    """ Class that implements Google Wifi AP.

    This class is a work in progress
    """
    def __init__(self, ap_settings):
        super().__init__(ap_settings)
        # Initialize AP
        if self.ap_settings["status_2G"] and self.ap_settings["status_5G_1"]:
            raise ValueError("Error initializing Google Wifi AP. "
                             "Only one interface can be enabled at a time.")
        self.channel_band_map = {
            "2G": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
            "5G_1": [36, 40, 44, 48, 149, 153, 157, 161, 165]
        }
        self.BW_MODE_MAP = {
            "legacy": 20,
            "VHT20": 20,
            "VHT40": 40,
            "VHT80": 80
        }
        self.default_settings = {
            "region": "United States",
            "brand": "Google",
            "model": "Wifi",
            "hostapd_profile": "whirlwind",
            "status_2G": 0,
            "status_5G_1": 0,
            "ssid_2G": "GoogleWifi_2G",
            "ssid_5G_1": "GoogleWifi_5G",
            "channel_2G": 11,
            "channel_5G_1": 149,
            "bandwidth_2G": "VHT20",
            "bandwidth_5G_1": "VHT20",
            "power_2G": "auto",
            "power_5G_1": "auto",
            "security_type_2G": "Open",
            "security_type_5G_1": "Open",
            "subnet_2G": "192.168.1.0/24",
            "subnet_5G_1": "192.168.9.0/24",
            "password_2G": "password",
            "password_5G_1": "password"
        }

        for setting in self.default_settings.keys():
            if setting not in self.ap_settings:
                self.log.warning(
                    "{0} not found during init. Setting {0} = {1}".format(
                        setting, self.default_settings[setting]))
                self.ap_settings[setting] = self.default_settings[setting]
        init_settings = self.ap_settings.copy()
        init_settings["ap_subnet"] = {
            "2g": self.ap_settings["subnet_2G"],
            "5g": self.ap_settings["subnet_5G_1"]
        }
        self.access_point = access_point.AccessPoint(init_settings)
        self.configure_ap()

    def read_ap_settings(self):
        """Function that reads current ap settings."""
        return self.ap_settings.copy()

    def update_ap_settings(self, dict_settings={}, **named_settings):
        """Function to update settings of existing AP.

        Function copies arguments into ap_settings and calls configure_ap
        to apply them.

        Args:
            dict_settings: single dictionary of settings to update
            **named_settings: named settings to update
            Note: dict and named_settings cannot contain the same settings.
        """
        settings_to_update = dict(dict_settings, **named_settings)
        if len(settings_to_update) != len(dict_settings) + len(named_settings):
            raise KeyError("The following keys were passed twice: {}".format(
                (set(dict_settings.keys()).intersection(
                    set(named_settings.keys())))))
        if not set(settings_to_update.keys()).issubset(
                set(self.ap_settings.keys())):
            raise KeyError(
                "The following settings are invalid for this AP: {}".format(
                    set(settings_to_update.keys()).difference(
                        set(self.ap_settings.keys()))))

        updating_2G = any(["2G" in x for x in settings_to_update.keys()])
        updating_5G_1 = any(["5G_1" in x for x in settings_to_update.keys()])
        if updating_2G and updating_5G_1:
            raise ValueError(
                "Error updating Google WiFi AP. "
                "One interface can be activated and updated at a time")
        elif updating_2G:
            # If updating an interface and not explicitly setting its status,
            # it is assumed that the interface is to be ENABLED and updated
            if "status_2G" not in settings_to_update:
                settings_to_update["status_2G"] = 1
                settings_to_update["status_5G_1"] = 0
        elif updating_5G_1:
            if "status_5G_1" not in settings_to_update:
                settings_to_update["status_2G"] = 0
                settings_to_update["status_5G_1"] = 1

        updates_requested = False
        for setting, value in settings_to_update.items():
            if self.ap_settings[setting] != value:
                self.ap_settings[setting] = value
                updates_requested = True

        if updates_requested:
            self.configure_ap()

    def configure_ap(self):
        """Function to configure Google Wifi."""
        self.log.info("Stopping Google Wifi interfaces.")
        self.access_point.stop_all_aps()

        if self.ap_settings["status_2G"] == 1:
            network = "2G"
            self.log.info("Bringing up 2.4 GHz network.")
        elif self.ap_settings["status_5G_1"] == 1:
            network = "5G_1"
            self.log.info("Bringing up 5 GHz network.")
        else:
            return

        bss_settings = []
        ssid = self.ap_settings["ssid_{}".format(network)]
        security_mode = self.ap_settings["security_type_{}".format(
            network)].lower()
        if "wpa" in security_mode:
            password = self.ap_settings["password_{}".format(network)]
            security = hostapd_security.Security(security_mode=security_mode,
                                                 password=password)
        else:
            security = hostapd_security.Security(security_mode=None,
                                                 password=None)
        channel = int(self.ap_settings["channel_{}".format(network)])
        bandwidth = self.BW_MODE_MAP[self.ap_settings["bandwidth_{}".format(
            network)]]
        config = hostapd_ap_preset.create_ap_preset(
            channel=channel,
            ssid=ssid,
            security=security,
            bss_settings=bss_settings,
            vht_bandwidth=bandwidth,
            profile_name=self.ap_settings["hostapd_profile"],
            iface_wlan_2g=self.access_point.wlan_2g,
            iface_wlan_5g=self.access_point.wlan_5g)
        config_bridge = self.access_point.generate_bridge_configs(channel)
        brconfigs = bridge_interface.BridgeInterfaceConfigs(
            config_bridge[0], "lan0", config_bridge[2])
        self.access_point.bridge.startup(brconfigs)
        self.access_point.start_ap(config)
        self.set_power(network, self.ap_settings["power_{}".format(network)])
        self.log.info("AP started on channel {} with SSID {}".format(
            channel, ssid))

    def set_power(self, network, power):
        """Function that sets network transmit power.

        Args:
            network: string containing network identifier (2G, 5G_1, 5G_2)
            power: power level in dBm
        """
        if power == "auto":
            power_string = "auto"
        else:
            if not float(power).is_integer():
                self.log.info(
                    "Power in dBm must be an integer. Setting to {}".format(
                        int(power)))
            power = int(power)
            power_string = "fixed {}".format(int(power) * 100)

        if "2G" in network:
            interface = self.access_point.wlan_2g
            self.ap_settings["power_2G"] = power
        elif "5G_1" in network:
            interface = self.access_point.wlan_5g
            self.ap_settings["power_5G_1"] = power
        self.access_point.ssh.run("iw dev {} set txpower {}".format(
            interface, power_string))

    def set_rate(self,
                 network,
                 mode=None,
                 num_streams=None,
                 rate=None,
                 short_gi=0):
        """Function that sets rate.

        Args:
            network: string containing network identifier (2G, 5G_1, 5G_2)
            mode: string indicating the WiFi standard to use
            num_streams: number of MIMO streams. used only for VHT
            rate: data rate of MCS index to use
            short_gi: boolean controlling the use of short guard interval
        """
        if "2G" in network:
            interface = self.access_point.wlan_2g
            interface_short = "2.4"
        elif "5G_1" in network:
            interface = self.access_point.wlan_5g
            interface_short = "5"

        if "legacy" in mode.lower():
            cmd_string = "iw dev {0} set bitrates legacy-{1} {2} ht-mcs-{1} vht-mcs-{1}".format(
                interface, interface_short, rate)
        elif "vht" in mode.lower():
            cmd_string = "iw dev {0} set bitrates legacy-{1} ht-mcs-{1} vht-mcs-{1} {2}:{3}".format(
                interface, interface_short, num_streams, rate)
            if short_gi:
                cmd_string = cmd_string + " sgi-{}".format(interface_short)
        elif "ht" in mode.lower():
            cmd_string = "iw dev {0} set bitrates legacy-{1} ht-mcs-{1} {2} vht-mcs-{1}".format(
                interface, interface_short, rate)
            if short_gi:
                cmd_string = cmd_string + " sgi-{}".format(interface_short)
        self.access_point.ssh.run(cmd_string)
