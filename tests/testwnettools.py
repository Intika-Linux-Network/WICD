import unittest
from unittest import mock
from wicd import wnettools

class TestWnettools(unittest.TestCase):
	def setUp(self):
		self.interface = wnettools.BaseInterface('eth0')
	
	def test_find_wireless_interface(self):
		interfaces = wnettools.GetWirelessInterfaces()
		# wlan0 may change depending on your system
		#self.assertTrue('wlan0' in interfaces)
		self.assertTrue(type(interfaces) == list)

	@mock.patch('wicd.misc.Run')
	def test_parse_new_cfg80211_interface_stdout(self, mock_syscall):
		with open('tests/crazy.wifi', 'r') as content_file:
			iw_scan = content_file.read()
		mock_syscall.return_value = iw_scan
		cells = wnettools.BaseWirelessInterface('wlan0').GetNetworks()
		self.assertGreater(len(cells), 0)
		
	@mock.patch('wicd.wnettools.os')
	@mock.patch('wicd.wnettools.open')
	def test_find_wired_interface(self, mock_f, mock_os):
		mock_os.listdir.return_value = ['eth0']
		mock_os.path.isdir.return_value = True
		mock_f.return_value.readlines.return_value = "1"
		interfaces = wnettools.GetWiredInterfaces()
		self.assertTrue('eth0' in interfaces)
		
	@mock.patch('wicd.misc.Run')
	def test_wext_is_valid_wpasupplicant_driver(self, mock_syscall):
		self.assertTrue(wnettools.IsValidWpaSuppDriver('wext'))
		mock_syscall.assert_called_once()
		
	def test_needs_external_calls_not_implemented(self):
		self.assertRaises(NotImplementedError, wnettools.NeedsExternalCalls)
		
	def test_is_up_boolean(self):
		self.assertTrue(type(self.interface.IsUp()) == bool)

	def test_enable_debug_mode(self):
		self.interface.SetDebugMode(True)
		self.assertTrue(self.interface.verbose)
		
	def test_disable_debug_mode(self):
		self.interface.SetDebugMode(False)
		self.assertFalse(self.interface.verbose)
		
	def test_interface_name_sanitation(self):
		interface = wnettools.BaseInterface('blahblah; uptime > /tmp/blah | cat')
		self.assertEqual(interface.iface, 'blahblahuptimetmpblahcat')
		
	def test_freq_translation_low(self):
		freq = '2.412 GHz'
		interface = wnettools.BaseWirelessInterface('wlan0')
		self.assertEqual(interface._FreqToChannel(freq), 1)
		
	def test_freq_translation_high(self):
		freq = '2.484 GHz'
		interface = wnettools.BaseWirelessInterface('wlan0')
		self.assertEqual(interface._FreqToChannel(freq), 14)
		
	def test_generate_psk(self):
		interface = wnettools.BaseWirelessInterface('wlan0')
		if 'wlan0' in wnettools.GetWirelessInterfaces():
			psk = interface.GeneratePSK({'essid' : 'Network 1', 'key' : 'arandompassphrase'})
			self.assertEqual(psk, 'd70463014514f4b4ebb8e3aebbdec13f4437ac3a9af084b3433f3710e658a7be')

def suite():
	suite = unittest.TestSuite()
	tests = []
	[ tests.append(test) for test in dir(TestWnettools) if test.startswith('test') ]
	for test in tests:
		suite.addTest(TestWnettools(test))
	return suite

if __name__ == '__main__':
	unittest.main()
