# -*- coding: utf-8 -*-
"""The Raspberry pancam

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

import logging
logger = logging.getLogger(__name__)
import os, sys
import threading
import datetime

from janitoo.fsm import HierarchicalMachine as Machine
from janitoo.thread import JNTBusThread, BaseThread
from janitoo.options import get_option_autostart
from janitoo.utils import HADD
from janitoo.node import JNTNode
from janitoo.value import JNTValue
from janitoo.component import JNTComponent

from janitoo_factory.buses.fsm import JNTFsmBus

from janitoo_raspberry_camera.camera import CameraBus
from janitoo_raspberry_camera.camera import CameraStream as PiCameraStream, CameraVideo as PiCameraVideo, CameraPhoto as PiCameraPhoto
from janitoo_raspberry_i2c.bus_i2c import I2CBus
from janitoo_raspberry_i2c_pca9685.pca9685 import PanComponent as PiPanComponent
from janitoo_raspberry_pancam import OID

def make_stream(**kwargs):
    return StreamComponent(**kwargs)

def make_pancam(**kwargs):
    return PancamComponent(**kwargs)

class PancamBus(JNTFsmBus):
    """A bus to manage pancam
    """

    states = [
       'booting',
       'sleeping',
       'reporting',
    ]
    """The pancam states :
    """

    transitions = [
        { 'trigger': 'boot',
            'source': 'booting',
            'dest': 'sleeping',
            'conditions': 'condition_values',
        },
        { 'trigger': 'sleep',
            'source': '*',
            'dest': 'sleeping',
        },
        { 'trigger': 'wakeup',
            'source': 'sleeping',
            'dest': 'reporting',
            'conditions': 'condition_values',
        },
        { 'trigger': 'report',
            'source': '*',
            'dest': 'reporting',
            'conditions': 'condition_values',
        },
    ]
    """The transitions
    """

    def __init__(self, **kwargs):
        """
        """
        JNTFsmBus.__init__(self, **kwargs)
        self.buses = {}
        self.buses['i2c'] = I2CBus(masters=[self], **kwargs)
        self.buses['camera'] = CameraBus(masters=[self], **kwargs)
        self.check_timer = None
        self._bus_lock = threading.Lock()
        self.extend_from_entry_points('rpii2c', ['pca9865'])

    def get_state(self, node_uuid, index):
        """Get the state of the fsm
        """
        return self.state

    def condition_values(self):
        """
        """
        logger.debug("[%s] - condition_values", self.__class__.__name__)
        return True

    def on_enter_reporting(self):
        """
        """
        logger.debug("[%s] - on_enter_reporting", self.__class__.__name__)
        #~ self.bus_acquire()
        #~ try:
            #~ self.nodeman.find_value('led', 'blink').data = 'heartbeat'
            #~ self.nodeman.add_polls(self.polled_sensors, slow_start=True, overwrite=False)
            #~ #In sleeping mode, send the state of the fsm every 900 seconds
            #~ #We update poll_delay directly to not update the value in configfile
            #~ state = self.nodeman.find_bus_value('state')
            #~ state.poll_delay = self.nodeman.find_bus_value('state_poll').data
            #~ overheat = self.nodeman.find_bus_value('overheat')
            #~ overheat.poll_delay = self.nodeman.find_bus_value('overheat_poll').data
            #~ self.nodeman.publish_value(overheat)
            #~ self.nodeman.add_polls([state, overheat], slow_start=True, overwrite=True)
        #~ except Exception:
            #~ logger.exception("[%s] - Error in on_enter_reporting", self.__class__.__name__)
        #~ finally:
            #~ self.bus_release()

    def on_enter_sleeping(self):
        """
        """
        logger.debug("[%s] - on_enter_sleeping", self.__class__.__name__)
        #~ self.bus_acquire()
        #~ try:
            #~ self.stop_check()
            #~ self.nodeman.remove_polls(self.polled_sensors)
            #~ self.nodeman.find_value('led', 'blink').data = 'off'
            #~ #In sleeping mode, send the state of the fsm every 900 seconds
            #~ #We update poll_delay directly to nto update the value in config file
            #~ self.nodeman.find_bus_value('state').poll_delay = 900
        #~ except Exception:
            #~ logger.exception("[%s] - Error in on_enter_sleeping", self.__class__.__name__)
        #~ finally:
            #~ self.bus_release()

    def on_exit_sleeping(self):
        """
        """
        logger.debug("[%s] - on_exit_sleeping", self.__class__.__name__)
        #~ self.on_check()

    def bus_acquire(self, blocking=True):
        """Get a lock on the bus"""
        if self._bus_lock.acquire(blocking):
            return True
        return False

    def bus_release(self):
        """Release a lock on the bus"""
        self._bus_lock.release()

    def bus_locked(self):
        """Get status of the lock"""
        return self._bus_lock.locked()

    #~ def stop_check(self):
        #~ """Check that the component is 'available'
#~
        #~ """
        #~ if self.check_timer is not None:
            #~ self.check_timer.cancel()
            #~ self.check_timer = None
#~
    #~ def on_check(self):
        #~ """Make a check using a timer.
#~
        #~ """
        #~ self.bus_acquire()
        #~ try:
            #~ self.stop_check()
            #~ if self.check_timer is None and self.is_started:
                #~ timer_delay = self.get_bus_value('timer_delay').data
                #~ if self.state == 'ringing':
                    #~ timer_delay = 1.0 * timer_delay / 2
                #~ self.check_timer = threading.Timer(timer_delay, self.on_check)
                #~ self.check_timer.start()
        #~ finally:
            #~ self.bus_release()
        #~ try:
            #~ state = True
            #~ #Check the temperatures
            #~ critical_temp = self.get_bus_value('temperature_critical').data
            #~ criticals = 0
            #~ nums = 0
            #~ total = 0
            #~ mini = maxi = None
            #~ for value in [('temperature', 'temperature'), ('ambiance', 'temperature'), ('cpu', 'temperature')]:
                #~ data = self.nodeman.find_value(*value).data
                #~ if data is None:
                    #~ #We should notify a sensor problem here.
                    #~ pass
                #~ else:
                    #~ nums += 1
                    #~ total += data
                    #~ if data > critical_temp:
                        #~ criticals += 1
                    #~ if maxi is None or data > maxi:
                        #~ maxi = data
                    #~ if mini is None or data < mini:
                        #~ mini = data
            #~ if criticals > 1:
                #~ if self.state != 'ringing':
                    #~ #We should notify a security problem : fire ?
                    #~ self.nodeman.find_bus_value('overheat').data = True
                    #~ self.ring()
            #~ elif self.state == 'ringing':
                #~ #We should notify a security problem : fire ?
                #~ self.nodeman.find_bus_value('overheat').data = False
                #~ self.report()
            #~ if nums != 0:
                #~ self.get_bus_value('temperature').data = total / nums
        #~ except Exception:
            #~ logger.exception("[%s] - Error in on_check", self.__class__.__name__)

    def start(self, mqttc, trigger_thread_reload_cb=None):
        """Start the bus
        """
        for bus in self.buses:
            self.buses[bus].start(mqttc, trigger_thread_reload_cb=None)
        JNTFsmBus.start(self, mqttc, trigger_thread_reload_cb)

    def stop(self):
        """Stop the bus
        """
        self.stop_check()
        for bus in self.buses:
            self.buses[bus].stop()
        JNTFsmBus.stop(self)

    def loop(self, stopevent):
        """Retrieve data
        Don't do long task in loop. Use a separated thread to not perturbate the nodeman

        """
        for bus in self.buses:
            self.buses[bus].loop(stopevent)

class StreamComponent(PiCameraStream):
    """ A component for pancam """

    def __init__(self, bus=None, addr=None, **kwargs):
        """
        """
        oid = kwargs.pop('oid', '%s.stream'%OID)
        name = kwargs.pop('name', "Stream pan camera")
        PiCameraStream.__init__(self, oid=oid, bus=bus, addr=addr, name=name,
                **kwargs)
        logger.debug("[%s] - __init__ node uuid:%s", self.__class__.__name__, self.uuid)

class PancamComponent(PiPanComponent):
    """ A component for pancam """

    def __init__(self, bus=None, addr=None, **kwargs):
        """
        """
        oid = kwargs.pop('oid', '%s.pancam'%OID)
        name = kwargs.pop('name', "Pan camera")
        PiPanComponent.__init__(self, oid=oid, bus=bus, addr=addr, name=name,
                **kwargs)
        logger.debug("[%s] - __init__ node uuid:%s", self.__class__.__name__, self.uuid)
