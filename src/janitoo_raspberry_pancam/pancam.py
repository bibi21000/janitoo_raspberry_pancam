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
from janitoo_raspberry_i2c_pca9685.pca9685 import ServoComponent as PiServoComponent

from janitoo_raspberry_pancam import OID

def make_stream(**kwargs):
    return StreamComponent(**kwargs)

def make_pancam(**kwargs):
    return PancamComponent(**kwargs)

def make_servo(**kwargs):
    return ServoComponent(**kwargs)

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
        #~ self.extend_from_entry_points('rpii2c', ['pca9865'])

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
        #~ self.stop_check()
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

class ServoComponent(PiServoComponent):
    """ A component for servo """

    def __init__(self, bus=None, addr=None, **kwargs):
        """
        """
        oid = kwargs.pop('oid', '%s.servo'%OID)
        name = kwargs.pop('name', "Servo")
        PiServoComponent.__init__(self, oid=oid, bus=bus, addr=addr, name=name,
                **kwargs)
        logger.debug("[%s] - __init__ node uuid:%s", self.__class__.__name__, self.uuid)

class PancamComponent(JNTComponent):
    """ A pan component"""

    def __init__(self, bus=None, addr=None, **kwargs):
        """
        """
        oid = kwargs.pop('oid', '%s.pancam'%OID)
        name = kwargs.pop('name', "Pan & Tilt component")
        product_name = kwargs.pop('product_name', "Pan & Tilt component")
        product_type = kwargs.pop('product_type', "Pan & Tilt component")
        product_manufacturer = kwargs.pop('product_manufacturer', "Janitoo")
        JNTComponent.__init__(self, oid=oid, bus=bus, addr=addr, name=name,
                product_name=product_name, product_type=product_type, product_manufacturer=product_manufacturer, **kwargs)
        logger.debug("[%s] - __init__ node uuid:%s", self.__class__.__name__, self.uuid)

        uuid="servox"
        self.values[uuid] = self.value_factory['config_string'](options=self.options, uuid=uuid,
            node_uuid=self.uuid,
            help="The node name of the servo for x",
            label='servox',
            default='servox',
        )
        uuid="servoy"
        self.values[uuid] = self.value_factory['config_string'](options=self.options, uuid=uuid,
            node_uuid=self.uuid,
            help="The node name of the servo for y",
            label='servoy',
            default='servoy',
        )
        uuid="angle_minx"
        self.values[uuid] = self.value_factory['config_integer'](options=self.options, uuid=uuid,
            node_uuid=self.uuid,
            help="The minimal angle for x",
            label='angle_minx',
            default=0,
        )
        uuid="angle_maxx"
        self.values[uuid] = self.value_factory['config_integer'](options=self.options, uuid=uuid,
            node_uuid=self.uuid,
            help="The maximal angle for x",
            label='angle_maxx',
            default=180,
        )
        uuid="angle_miny"
        self.values[uuid] = self.value_factory['config_integer'](options=self.options, uuid=uuid,
            node_uuid=self.uuid,
            help="The minimal angle for y",
            label='angle_miny',
            default=0,
        )
        uuid="angle_maxy"
        self.values[uuid] = self.value_factory['config_integer'](options=self.options, uuid=uuid,
            node_uuid=self.uuid,
            help="The maximal angle for y",
            label='angle_maxy',
            default=90,
        )
        uuid="initial"
        self.values[uuid] = self.value_factory['config_string'](options=self.options, uuid=uuid,
            node_uuid=self.uuid,
            help="Initial position : x|y",
            label='Init pos',
            default='0|0',
        )
        uuid="position"
        self.values[uuid] = self.value_factory['action_string'](options=self.options, uuid=uuid,
            node_uuid=self.uuid,
            set_data_cb=self.set_position,
            help="Position : x|y",
            label='Position',
        )
        poll_value = self.values[uuid].create_poll_value(default=300)
        self.values[poll_value.uuid] = poll_value

        self.travel_timer = None
        self.travel_timer_lock = threading.Lock()
        uuid="travel_speed"
        self.values[uuid] = self.value_factory['config_string'](options=self.options, uuid=uuid,
            node_uuid=self.uuid,
            help="The travel speed in degrees|time(ms)",
            label='travel_speed',
            default='1|100',
        )
        uuid="travel"
        self.values[uuid] = self.value_factory['action_string'](options=self.options, uuid=uuid,
            node_uuid=self.uuid,
            set_data_cb=self.set_travel,
            help="Travel to position : x|y. Send -1|-1 to stop the travel",
            label='Travel',
        )
        poll_value = self.values[uuid].create_poll_value(default=300)
        self.values[poll_value.uuid] = poll_value

    def stop(self, **kwargs):
        """Stop the component
        """
        self.stop_traveling()
        self.values['position'].data = self.values['initial'].data
        JNTComponent.stop(self)

    def set_position(self, node_uuid, index, data):
        """Change the position of the pan
        """
        try:
            servox = self._bus.nodeman.find_node('servox')
            servoy = self._bus.nodeman.find_node('servoy')
            logger.debug('[%s] - set_position of servos %s and %s', self.__class__.__name__, servox, servoy)
            if data is None or data=="-1|-1":
                sx,sy = self.values['initial'].get_data_index(index=index).split('|')
            else:
                sx,sy = data.split('|')
            logger.debug('[%s] - set_position to data %s|%s', self.__class__.__name__, sx, sy)
            datax = "%s|%s|%s"%(sx, self.values['angle_minx'].get_data_index(index=index), self.values['angle_maxx'].get_data_index(index=index))
            datay = "%s|%s|%s"%(sy, self.values['angle_miny'].get_data_index(index=index), self.values['angle_maxy'].get_data_index(index=index) )
            servox.values['angle'].data = datax
            servoy.values['angle'].data = datay
            self.values['position']._data = data
        except Exception:
            logger.exception('[%s] - Exception when set_position', self.__class__.__name__)

    def set_travel(self, node_uuid=None, index=None, data = None):
        """
        """
        if data is None or data=="-1|-1":
            self.stop_traveling(node_uuid=node_uuid, index=index, data = data)
            self.values['travel']._data = "-1|-1"
        else:
            self.values['travel']._data = data
            self.start_traveling(node_uuid=node_uuid, index=index, data = data)

    def start_traveling(self, **kwargs):
        """
        """
        self.travel_timer_lock.acquire()
        try:
            if self.travel_timer is not None:
                self.travel_timer.cancel()
                self.travel_timer = None
            self.travel_timer = threading.Timer(0.01, self.timer_travel_change)
            self.travel_timer.start()
        finally:
            self.travel_timer_lock.release()

    def stop_traveling(self, **kwargs):
        """
        """
        #~ print 'locking', self.travel_timer_lock.acquire(False)
        if self.travel_timer_lock is None:
            return
        self.travel_timer_lock.acquire()
        try:
            if self.travel_timer is not None:
                self.travel_timer.cancel()
                self.travel_timer = None
        finally:
            self.travel_timer_lock.release()

    def timer_travel_change(self):
        """
        """
        if self.travel_timer_lock is None:
            return
        self.travel_timer_lock.acquire()
        try:
            if self.travel_timer is not None:
                self.travel_timer.cancel()
                self.travel_timer = None
            speed_ang,speed_time = self.values['travel_speed']._data.split('|')
            if self.values['travel']._data is None or self.values['travel']._data=="-1|-1":
                self.values['travel']._data = "-1|-1"
                return
            else:
                tx,ty = self.values['travel']._data.split('|')
                px,py = self.values['position']._data.split('|')
            npx = int(px)
            if int(tx)>int(px):
                npx = int(px)+int(speed_ang)
            elif int(tx)<int(px):
                npx = int(px)-int(speed_ang)
            npy = int(py)
            if int(ty)>int(py):
                npy = int(py)+int(speed_ang)
            elif int(ty)<int(py):
                npy = int(py)-int(speed_ang)
            if npx != int(px) or npy != int(py):
                logger.debug('[%s] - timer_travel_change to data %s|%s', self.__class__.__name__, npx, npy)
                self.values['position'].data = "%s|%s" % (npx, npy)
                self.travel_timer = threading.Timer(int(speed_time)/1000, self.timer_travel_change)
                self.travel_timer.start()
        finally:
            self.travel_timer_lock.release()
