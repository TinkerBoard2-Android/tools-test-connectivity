from acts import asserts
from acts import base_test
from acts.controllers import android_device
from acts.test_decorators import test_tracker_info

from scapy.all import *
from threading import Event
from threading import Thread
import time
import warnings


CLIENT_PORT = 68
SERVER_PORT = 67
BROADCAST_MAC = 'ff:ff:ff:ff:ff:ff'
INET4_ANY = '0.0.0.0'
NETADDR_PREFIX = '192.168.42.'
OTHER_NETADDR_PREFIX = '192.168.43.'
NETADDR_BROADCAST = '255.255.255.255'
SUBNET_BROADCAST = NETADDR_PREFIX + '255'


OFFER = 2
REQUEST = 3
ACK = 5
NAK = 6


pmc_base_cmd = (
    "am broadcast -a com.android.pmc.action.AUTOPOWER --es PowerAction ")
start_pmc_cmd = (
    "am start -S -n com.android.pmc/com.android.pmc.PMCMainActivity")
pmc_start_usb_tethering_cmd = "%sStartUSBTethering" % pmc_base_cmd
pmc_stop_usb_tethering_cmd = "%sStopUSBTethering" % pmc_base_cmd


class DhcpServerTest(base_test.BaseTestClass):
    def setup_class(self):
        self.dut = self.android_devices[0]
        self.USB_TETHERED = False
        self.next_hwaddr_index = 0
        self.stop_arp = Event()

        conf.checkIPaddr = 0
        conf.checkIPsrc = 0
        # Allow using non-67 server ports as long as client uses 68
        bind_layers(UDP, BOOTP, dport=CLIENT_PORT)

        self.dut.adb.shell(start_pmc_cmd)
        self.dut.adb.shell("setprop log.tag.PMC VERBOSE")
        iflist_before = get_if_list()
        self._start_usb_tethering(self.dut)
        self.iface = self._wait_for_new_iface(iflist_before)
        self.real_hwaddr = get_if_raw_hwaddr(self.iface)

        # Start a thread to answer to all ARP "who-has"
        thread = Thread(target=self._sniff_arp, args=(self.stop_arp,))
        thread.start()

        # Discover server IP and device hwaddr
        hwaddr = self._next_hwaddr()
        resp = self._get_response(self._make_discover(hwaddr))
        asserts.assert_false(None == resp,
            "Device did not reply to first DHCP discover")
        self.server_addr = getopt(resp, 'server_id')
        self.dut_hwaddr = resp.getlayer(Ether).src
        asserts.assert_false(None == self.server_addr,
            "DHCP server did not specify server identifier")
        # Ensure that we don't depend on assigned route/gateway on the host
        conf.route.add(host=self.server_addr, dev=self.iface, gw="0.0.0.0")

    def setup_test(self):
        # Some versions of scapy do not close the receive file properly
        warnings.filterwarnings("ignore", category=ResourceWarning)

        bind_layers(UDP, BOOTP, dport=68)
        self.hwaddr = self._next_hwaddr()
        self.other_hwaddr = self._next_hwaddr()
        self.cleanup_releases = []

    def teardown_test(self):
        for packet in self.cleanup_releases:
            self._send(packet)

    def teardown_class(self):
        self.stop_arp.set()
        self._stop_usb_tethering(self.dut)

    def on_fail(self, test_name, begin_time):
        self.dut.take_bug_report(test_name, begin_time)

    def _start_usb_tethering(self, dut):
        """ Start USB tethering

        Args:
            1. dut - ad object
        """
        self.log.info("Starting USB Tethering")
        dut.stop_services()
        dut.adb.shell(pmc_start_usb_tethering_cmd)
        self._wait_for_device(self.dut)
        self.USB_TETHERED = True

    def _stop_usb_tethering(self, dut):
        """ Stop USB tethering

        Args:
            1. dut - ad object
        """
        self.log.info("Stopping USB Tethering")
        dut.adb.shell(pmc_stop_usb_tethering_cmd)
        self._wait_for_device(self.dut)
        dut.start_services(skip_sl4a=getattr(dut, "skip_sl4a", False))
        self.USB_TETHERED = False

    def _wait_for_device(self, dut):
        """ Wait for device to come back online

        Args:
            1. dut - ad object
        """
        while dut.serial not in android_device.list_adb_devices():
            pass
        dut.adb.wait_for_device()

    def _wait_for_new_iface(self, old_ifaces):
        old_set = set(old_ifaces)
        # Try 10 times to find a new interface with a 1s sleep every time
        # (equivalent to a 9s timeout)
        for i in range(0, 10):
            new_ifaces = set(get_if_list()) - old_set
            asserts.assert_true(len(new_ifaces) < 2,
                "Too many new interfaces after turning on tethering")
            if len(new_ifaces) == 1:
                return new_ifaces.pop()
            time.sleep(1)
        asserts.fail("Timeout waiting for tethering interface on host")

    def _sniff_arp(self, stop_arp):
        try:
            sniff(iface=self.iface, filter='arp', prn=self._handle_arp, store=0,
                stop_filter=lambda p: stop_arp.is_set())
        except:
            # sniff may raise when tethering is disconnected. Ignore
            # exceptions if stop was requested.
            if not stop_arp.is_set():
                raise

    def _handle_arp(self, packet):
        # Reply to all arp "who-has": say we have everything
        if packet[ARP].op == ARP.who_has:
            reply = ARP(op=ARP.is_at, hwsrc=self.real_hwaddr, psrc=packet.pdst,
                hwdst=BROADCAST_MAC, pdst=SUBNET_BROADCAST)
            sendp(Ether(dst=BROADCAST_MAC, src=self.real_hwaddr) / reply,
                iface=self.iface, verbose=False)

    @test_tracker_info(uuid="a8712769-977a-4ee1-902f-90b3ba30b40c")
    def test_config_assumptions(self):
        resp = self._get_response(self._make_discover(self.hwaddr))
        asserts.assert_false(None == resp, "Device did not reply to discover")
        asserts.assert_true(get_yiaddr(resp).startswith(NETADDR_PREFIX),
            "Server does not use expected prefix")

    def test_discover_broadcastbit(self):
        resp = self._get_response(
            self._make_discover(self.hwaddr, bcastbit=True))
        self._assert_offer(resp)
        self._assert_broadcast(resp)

    def test_discover_relayed_broadcastbit(self):
        giaddr = NETADDR_PREFIX + '123'
        resp = self._get_response(
            self._make_discover(self.hwaddr, giaddr=giaddr, bcastbit=True))
        self._assert_offer(resp)
        self._assert_unicast(resp, giaddr)
        self._assert_broadcastbit(resp)

    def _run_discover_paramrequestlist(self, params, unwanted_params):
        params_opt = tuple(['param_req_list'] + [
            chr(DHCPRevOptions[optname][0]).encode() for optname in params])
        resp = self._get_response(
            self._make_discover(self.hwaddr, options=[params_opt]))

        self._assert_offer(resp)
        # List of requested params in response order
        resp_opts = [opt[0] for opt in resp.getlayer(DHCP).options]
        resp_requested_opts = [opt for opt in resp_opts if opt in params]
        # All above params should be supported, order should be conserved
        asserts.assert_equal(params, resp_requested_opts)
        asserts.assert_equal(0, len(set(resp_opts) & set(unwanted_params)))
        return resp

    def test_discover_paramrequestlist(self):
        resp = self._run_discover_paramrequestlist(
            ['subnet_mask', 'broadcast_address', 'router', 'name_server'],
            unwanted_params=[])
        for opt in ['broadcast_address', 'router', 'name_server']:
            asserts.assert_true(getopt(resp, opt).startswith(NETADDR_PREFIX),
                opt + ' does not start with ' + NETADDR_PREFIX)

        subnet_mask = getopt(resp, 'subnet_mask')
        asserts.assert_true(subnet_mask.startswith('255.255.'),
            'Unexpected subnet mask for /16+: ' + subnet_mask)

    def test_discover_paramrequestlist_rev(self):
        # RFC2132 #9.8: "The DHCP server is not required to return the options
        # in the requested order, but MUST try to insert the requested options
        # in the order requested"
        asserts.skip('legacy behavior not compliant: fixed order used')
        self._run_discover_paramrequestlist(
            ['name_server', 'router', 'broadcast_address', 'subnet_mask'],
            unwanted_params=[])

    def test_discover_paramrequestlist_unwanted(self):
        asserts.skip('legacy behavior always sends all parameters')
        self._run_discover_paramrequestlist(['router', 'name_server'],
            unwanted_params=['broadcast_address', 'subnet_mask'])

    def _assert_renews(self, request, addr, exp_time, resp_type=ACK):
        # Sleep to test lease time renewal
        time.sleep(3)
        resp = self._get_response(request)
        self._assert_type(resp, resp_type)
        asserts.assert_equal(addr, get_yiaddr(resp))
        remaining_lease = getopt(resp, 'lease_time')
        # Lease renewed: waited for 3s, lease time not decreased by more than 2
        asserts.assert_true(remaining_lease >= exp_time - 2,
            'Lease not renewed')
        # Lease times should be consistent across offers/renewals
        asserts.assert_true(remaining_lease <= exp_time + 2,
            'Lease time inconsistent')
        return resp

    @test_tracker_info(uuid="d6b598b7-f443-4b5a-ba80-4af5d211cade")
    def test_discover_assigned_ownaddress(self):
        addr, siaddr, resp = self._request_address(self.hwaddr)

        lease_time = getopt(resp, 'lease_time')
        server_id = getopt(resp, 'server_id')
        asserts.assert_true(lease_time >= 60, "Lease time is too short")
        asserts.assert_false(addr == INET4_ANY, "Assigned address is empty")
        # Wait to test lease expiration time change
        time.sleep(3)

        # New discover, same address
        resp = self._assert_renews(self._make_discover(self.hwaddr),
            addr, lease_time, resp_type=OFFER)
        self._assert_unicast(resp, get_yiaddr(resp))
        self._assert_broadcastbit(resp, isset=False)

    @test_tracker_info(uuid="cbb07d77-912b-4269-bbbc-adba99779587")
    def test_discover_assigned_otherhost(self):
        addr, siaddr, _ = self._request_address(self.hwaddr)

        # New discover, same address, different client
        resp = self._get_response(self._make_discover(self.other_hwaddr,
            [('requested_addr', addr)]))

        self._assert_offer(resp)
        asserts.assert_false(get_yiaddr(resp) == addr,
            "Already assigned address offered")
        self._assert_unicast(resp, get_yiaddr(resp))
        self._assert_broadcastbit(resp, isset=False)

    @test_tracker_info(uuid="3d2b3d2f-eb5f-498f-b887-3b4638cebf14")
    def test_discover_requestaddress(self):
        addr = NETADDR_PREFIX + '200'
        resp = self._get_response(self._make_discover(self.hwaddr,
            [('requested_addr', addr)]))
        self._assert_offer(resp)
        asserts.assert_equal(get_yiaddr(resp), addr)

        # Lease not committed: can request again
        resp = self._get_response(self._make_discover(self.other_hwaddr,
            [('requested_addr', addr)]))
        self._assert_offer(resp)
        asserts.assert_equal(get_yiaddr(resp), addr)

    def test_request_unicast(self):
        addr, siaddr, resp = self._request_address(self.hwaddr, bcast=False)
        self._assert_unicast(resp, addr)

    @test_tracker_info(uuid="ec00d268-80cb-4be5-9771-2292cc7d2e18")
    def test_request_selecting_inuse(self):
        addr, siaddr, _ = self._request_address(self.hwaddr)
        resp = self._get_response(
            self._make_request(self.other_hwaddr, addr, siaddr))
        self._assert_nak(resp)
        self._assert_broadcast(resp)

    def test_request_selecting_wrongsiaddr(self):
        addr = NETADDR_PREFIX + '200'
        wrong_siaddr = NETADDR_PREFIX + '201'
        asserts.assert_false(wrong_siaddr == self.server_addr,
            'Test assumption not met: server addr is ' + wrong_siaddr)
        resp = self._get_response(
            self._make_request(self.hwaddr, addr, siaddr=wrong_siaddr))
        asserts.assert_true(resp == None,
            'Received response for request with incorrect siaddr')

    def _run_initreboot(self, bcastbit):
        addr, siaddr, resp = self._request_address(self.hwaddr)
        exp = getopt(resp, 'lease_time')

        # init-reboot: siaddr is None
        return self._assert_renews(self._make_request(
                self.hwaddr, addr, siaddr=None, bcastbit=bcastbit), addr, exp)

    @test_tracker_info(uuid="263c91b9-cfe9-4f21-985d-b7046df80528")
    def test_request_initreboot(self):
        resp = self._run_initreboot(bcastbit=False)
        self._assert_unicast(resp)
        self._assert_broadcastbit(resp, isset=False)

    def test_request_initreboot_broadcastbit(self):
        resp = self._run_initreboot(bcastbit=True)
        self._assert_broadcast(resp)

    @test_tracker_info(uuid="5563c616-2136-47f6-9151-4e28cbfe797c")
    def test_request_initreboot_nolease(self):
        # RFC2131 #4.3.2
        asserts.skip("legacy behavior not compliant")
        addr = NETADDR_PREFIX + '123'
        resp = self._get_response(self._make_request(self.hwaddr, addr, None))
        asserts.assert_equal(resp, None)

    @test_tracker_info(uuid="da5c5537-cb38-4a2e-828f-44bc97976fe5")
    def test_request_initreboot_incorrectlease(self):
        otheraddr = NETADDR_PREFIX + '123'
        addr, siaddr, _ = self._request_address(self.hwaddr)
        asserts.assert_false(addr == otheraddr,
            "Test assumption not met: server assigned " + otheraddr)

        resp = self._get_response(
            self._make_request(self.hwaddr, otheraddr, siaddr=None))
        self._assert_nak(resp)
        self._assert_broadcast(resp)

    @test_tracker_info(uuid="ce42ba57-07be-427b-9cbd-5535c62b0120")
    def test_request_initreboot_wrongnet(self):
        resp = self._get_response(self._make_request(self.hwaddr,
            OTHER_NETADDR_PREFIX + '1', siaddr=None))
        self._assert_nak(resp)
        self._assert_broadcast(resp)

    def _run_rebinding(self, bcastbit, giaddr=INET4_ANY):
        addr, siaddr, resp = self._request_address(self.hwaddr)
        exp = getopt(resp, 'lease_time')

        # Rebinding: no siaddr or reqaddr
        resp = self._assert_renews(
            self._make_request(self.hwaddr, reqaddr=None, siaddr=None,
                ciaddr=addr, giaddr=giaddr, ip_src=addr,
                ip_dst=NETADDR_BROADCAST, bcastbit=bcastbit),
            addr, exp)
        return resp, addr

    @test_tracker_info(uuid="68bfcb25-5873-41ad-ad0a-bf22781534ca")
    def test_request_rebinding(self):
        resp, addr = self._run_rebinding(bcastbit=False)
        self._assert_unicast(resp, addr)
        self._assert_broadcastbit(resp, isset=False)

    def test_request_rebinding_relayed(self):
        giaddr = NETADDR_PREFIX + '123'
        resp, _ = self._run_rebinding(bcastbit=False, giaddr=giaddr)
        self._assert_unicast(resp, giaddr)
        self._assert_broadcastbit(resp, isset=False)

    @test_tracker_info(uuid="cee2668b-bd79-47d7-b358-8f9387d715b1")
    def test_request_rebinding_inuse(self):
        addr, siaddr, _ = self._request_address(self.hwaddr)

        resp = self._get_response(self._make_request(
                self.other_hwaddr, reqaddr=None, siaddr=None, ciaddr=addr))
        self._assert_nak(resp)
        self._assert_broadcast(resp)

    @test_tracker_info(uuid="d95d69b5-ab9a-42f5-8dd0-b9b6a6d960cc")
    def test_request_rebinding_wrongaddr(self):
        otheraddr = NETADDR_PREFIX + '123'
        addr, siaddr, _ = self._request_address(self.hwaddr)
        asserts.assert_false(addr == otheraddr,
            "Test assumption not met: server assigned " + otheraddr)

        resp = self._get_response(self._make_request(
            self.hwaddr, reqaddr=None, siaddr=siaddr, ciaddr=otheraddr))
        self._assert_nak(resp)
        self._assert_broadcast(resp)

    @test_tracker_info(uuid="421a86b3-8779-4910-8050-7806536efabb")
    def test_request_rebinding_wrongaddr_relayed(self):
        otheraddr = NETADDR_PREFIX + '123'
        relayaddr = NETADDR_PREFIX + '124'
        addr, siaddr, _ = self._request_address(self.hwaddr)
        asserts.assert_false(addr == otheraddr,
            "Test assumption not met: server assigned " + otheraddr)
        asserts.assert_false(addr == relayaddr,
            "Test assumption not met: server assigned " + relayaddr)

        req = self._make_request(self.hwaddr, reqaddr=None, siaddr=None,
            ciaddr=otheraddr, giaddr=relayaddr)

        resp = self._get_response(req)
        self._assert_nak(resp)
        self._assert_unicast(resp, relayaddr)
        self._assert_broadcastbit(resp)

    @test_tracker_info(uuid="6ff1fab4-009a-4758-9153-0d9db63423da")
    def test_release(self):
        addr, siaddr, _ = self._request_address(self.hwaddr)
        # Re-requesting fails
        resp = self._get_response(
            self._make_request(self.other_hwaddr, addr, siaddr))
        self._assert_nak(resp)
        self._assert_broadcast(resp)

        # Succeeds after release
        self._send(self._make_release(self.hwaddr, addr, siaddr))
        resp = self._get_response(
            self._make_request(self.other_hwaddr, addr, siaddr))
        self._assert_ack(resp)

    @test_tracker_info(uuid="abb1a53e-6b6c-468f-88b9-ace9ca4d6593")
    def test_release_noserverid(self):
        addr, siaddr, _ = self._request_address(self.hwaddr)

        # Release without server_id opt is ignored
        release = self._make_release(self.hwaddr, addr, siaddr)
        removeopt(release, 'server_id')
        self._send(release)

        # Not released: request fails
        resp = self._get_response(
            self._make_request(self.other_hwaddr, addr, siaddr))
        self._assert_nak(resp)
        self._assert_broadcast(resp)

    @test_tracker_info(uuid="8415b69e-ae61-4474-8495-d783ba6818d1")
    def test_release_wrongserverid(self):
        addr, siaddr, _ = self._request_address(self.hwaddr)

        # Release with wrong server id
        release = self._make_release(self.hwaddr, addr, siaddr)
        setopt(release, 'server_id', addr)
        self._send(release)

        # Not released: request fails
        resp = self._get_response(
            self._make_request(self.other_hwaddr, addr, siaddr))
        self._assert_nak(resp)
        self._assert_broadcast(resp)

    def test_unicast_l2l3(self):
        reqAddr = NETADDR_PREFIX + '124'
        resp = self._get_response(self._make_request(
            self.hwaddr, reqAddr, siaddr=None))
        self._assert_unicast(resp)
        str_hwaddr = format_hwaddr(self.hwaddr)
        asserts.assert_equal(str_hwaddr, resp.getlayer(Ether).dst)
        asserts.assert_equal(reqAddr, resp.getlayer(IP).dst)
        asserts.assert_equal(CLIENT_PORT, resp.getlayer(UDP).dport)

    def _request_address(self, hwaddr, bcast=True):
        resp = self._get_response(self._make_discover(hwaddr))
        self._assert_offer(resp)
        addr = get_yiaddr(resp)
        siaddr = getopt(resp, 'server_id')
        resp = self._get_response(self._make_request(hwaddr, addr, siaddr,
                ip_dst=(INET4_ANY if bcast else siaddr)))
        self._assert_ack(resp)
        return addr, siaddr, resp

    def _get_response(self, packet):
        resp = srp1(packet, iface=self.iface, timeout=10, verbose=False)
        bootp_resp = (resp or None) and resp.getlayer(BOOTP)
        if bootp_resp != None and get_mess_type(bootp_resp) == ACK:
            # Note down corresponding release for this request
            release = self._make_release(bootp_resp.chaddr, bootp_resp.yiaddr,
                getopt(bootp_resp, 'server_id'))
            self.cleanup_releases.append(release)
        return resp

    def _send(self, packet):
        sendp(packet, iface=self.iface, verbose=False)

    def _assert_type(self, packet, tp):
        asserts.assert_false(None == packet, "No packet")
        asserts.assert_equal(tp, get_mess_type(packet))

    def _assert_ack(self, packet):
        self._assert_type(packet, ACK)

    def _assert_nak(self, packet):
        self._assert_type(packet, NAK)

    def _assert_offer(self, packet):
        self._assert_type(packet, OFFER)

    def _assert_broadcast(self, packet):
        asserts.assert_false(None == packet, "No packet")
        asserts.assert_equal(packet.getlayer(Ether).dst, BROADCAST_MAC)
        asserts.assert_equal(packet.getlayer(IP).dst, NETADDR_BROADCAST)
        self._assert_broadcastbit(packet)

    def _assert_broadcastbit(self, packet, isset=True):
        mask = 0x8000
        flag = packet.getlayer(BOOTP).flags
        asserts.assert_equal(flag & mask, mask if isset else 0)

    def _assert_unicast(self, packet, ipAddr=None):
        asserts.assert_false(None == packet, "No packet")
        asserts.assert_false(packet.getlayer(Ether).dst == BROADCAST_MAC,
            "Layer 2 packet destination address was broadcast")
        if ipAddr:
            asserts.assert_equal(packet.getlayer(IP).dst, ipAddr)

    def _next_hwaddr(self):
        addr = make_hwaddr(self.next_hwaddr_index)
        self.next_hwaddr_index = self.next_hwaddr_index + 1
        return addr

    def _make_dhcp(self, src_hwaddr, options, ciaddr=INET4_ANY,
            ip_src=INET4_ANY, ip_dst=NETADDR_BROADCAST, giaddr=INET4_ANY,
            bcastbit=False):
        broadcast = (ip_dst == NETADDR_BROADCAST)
        ethernet = Ether(dst=(BROADCAST_MAC if broadcast else self.dut_hwaddr))
        ip = IP(src=ip_src, dst=ip_dst)
        udp = UDP(sport=68, dport=SERVER_PORT)
        bootp = BOOTP(chaddr=src_hwaddr, ciaddr=ciaddr, giaddr=giaddr,
            flags=(0x8000 if bcastbit else 0), xid=RandInt())
        dhcp = DHCP(options=options)
        return ethernet / ip / udp / bootp / dhcp

    def _make_discover(self, src_hwaddr, options = [], giaddr=INET4_ANY,
            bcastbit=False):
        opts = [('message-type','discover')]
        opts.extend(options)
        opts.append('end')
        return self._make_dhcp(src_hwaddr, options=opts, giaddr=giaddr,
            ip_dst=NETADDR_BROADCAST, bcastbit=bcastbit)

    def _make_request(self, src_hwaddr, reqaddr, siaddr, ciaddr=INET4_ANY,
            ip_dst=None, ip_src=None, giaddr=INET4_ANY, bcastbit=False):
        if not ip_dst:
            ip_dst = siaddr or INET4_ANY

        if not ip_src and ip_dst == INET4_ANY:
            ip_src = INET4_ANY
        elif not ip_src:
            ip_src = ciaddr if not isempty(ciaddr) else reqaddr
        # Kernel will not receive unicast UDP packets with empty ip_src
        asserts.assert_false(ip_dst != INET4_ANY and isempty(ip_src),
            "Unicast ip_src cannot be zero")
        opts = [('message-type', 'request')]
        if siaddr:
            opts.append(('server_id', siaddr))
        if reqaddr:
            opts.append(('requested_addr', reqaddr))
        opts.append('end')
        return self._make_dhcp(src_hwaddr, options=opts, ciaddr=ciaddr,
            ip_src=ip_src, ip_dst=ip_dst, giaddr=giaddr, bcastbit=bcastbit)

    def _make_release(self, src_hwaddr, addr, server_id):
        opts = [('message-type', 'release'), ('server_id', server_id), 'end']
        return self._make_dhcp(src_hwaddr, opts, ciaddr=addr, ip_src=addr,
            ip_dst=server_id)

def isempty(addr):
    return not addr or addr == INET4_ANY


def setopt(packet, optname, val):
    dhcp = packet.getlayer(DHCP)
    if optname in [opt[0] for opt in dhcp.options]:
        dhcp.options = [(optname, val) if opt[0] == optname else opt
            for opt in dhcp.options]
    else:
        # Add before the last option (last option is "end")
        dhcp.options.insert(len(dhcp.options) - 1, (optname, val))


def getopt(packet, key):
    opts = [opt[1] for opt in packet.getlayer(DHCP).options if opt[0] == key]
    return opts[0] if opts else None


def removeopt(packet, key):
    dhcp = packet.getlayer(DHCP)
    dhcp.options = [opt for opt in dhcp.options if opt[0] != key]


def get_yiaddr(packet):
    return packet.getlayer(BOOTP).yiaddr


def get_mess_type(packet):
    return getopt(packet, 'message-type')


def make_hwaddr(index):
    if index > 0xffff:
        raise ValueError("Address index out of range")
    return '\x44\x85\x00\x00{}{}'.format(chr(index >> 8), chr(index & 0xff))


def format_hwaddr(addr):
    return  ':'.join(['%02x' % ord(c) for c in addr])
