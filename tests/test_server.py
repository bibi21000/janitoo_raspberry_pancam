# -*- coding: utf-8 -*-

"""Unittests for Janitoo-Raspberry Pi Server.
"""
__license__ = """
    This file is part of Janitoo.

    Janitoo is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Janitoo is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Janitoo. If not, see <http://www.gnu.org/licenses/>.

"""
__author__ = 'Sébastien GALLET aka bibi21000'
__email__ = 'bibi21000@gmail.com'
__copyright__ = "Copyright © 2013-2014-2015-2016 Sébastien GALLET aka bibi21000"

import warnings
warnings.filterwarnings("ignore")

import time

from janitoo_nosetests.server import JNTTServer, JNTTServerCommon
from janitoo.utils import HADD_SEP, HADD
from janitoo.thread import JNTBusThread
from janitoo_raspberry.server import PiServer

class TestTutorialServer(JNTTServer, JNTTServerCommon):
    """Test the tutorial server
    """
    server_class = PiServer
    server_conf = "tests/data/janitoo_raspberry_pancam.conf"
    server_section = "pancam"

    hadds = [HADD%(217,0), HADD%(217,1), HADD%(217,2), HADD%(217,3)]

    def test_040_server_start_no_error_in_log(self):
        self.onlyRasperryTest()
        JNTTServerCommon.test_040_server_start_no_error_in_log(self)

    def test_100_server_start_machine_state(self):
        self.start()
        time.sleep(20)
        thread = self.server.find_thread(self.server_section)
        self.assertNotEqual(thread, None)
        self.assertIsInstance(thread, JNTBusThread)
        bus = thread.bus
        self.assertNotEqual(bus, None)
        self.waitHeartbeatNodes(hadds=self.hadds)
        self.assertFsmBoot()
        bus.wakeup()
        time.sleep(2)
        bus.sleep()
        time.sleep(2)
        bus.report()
        time.sleep(15)
        bus.sleep()
        time.sleep(2)

    def test_101_server_pan(self):
        self.onlyRasperryTest()
        self.start()
        time.sleep(20)
        thread = self.server.find_thread(self.server_section)
        self.assertNotEqual(thread, None)
        self.assertIsInstance(thread, JNTBusThread)
        bus = thread.bus
        self.assertNotEqual(bus, None)
        self.waitHeartbeatNodes(hadds=self.hadds)
        self.assertFsmBoot()
        bus.wakeup()
        time.sleep(2)
        self.assertTrue(thread.nodeman.is_started)
        self.assertNotEqual(None, bus.nodeman.find_node('pan'))
        self.assertNotEqual(None, bus.find_components('pancam.pancam'))
        pancams = bus.find_components('pancam.pancam')
        self.assertEqual(1, len(pancams))
        pancam = pancams[0]
        self.assertNotEqual(None, pancam)
        #~ pancam.set_change(None, 0, '155,1')
        changes = bus.find_values('pancam.pancam','position')
        self.assertEqual(1, len(changes))
        changes[0].data = '0|0'
        time.sleep(2)
        changes[0].data = '90|45'
        time.sleep(2)
        changes[0].data = '135|90'
        time.sleep(2)
        changes[0].data = '180|135'
        time.sleep(2)
        changes[0].data = '90|45'
        time.sleep(2)
        changes[0].data = '-1|-1'
        time.sleep(2)
        changes[0].data = '90|45'
        time.sleep(2)
        changes[0].data = '0|0'
        time.sleep(2)
        self.assertEqual('0|0', changes[0].data)
