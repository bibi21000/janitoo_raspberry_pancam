#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup file of Janitoo
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

from os import name as os_name
from setuptools import setup, find_packages
from platform import system as platform_system
import glob
import os
import sys
from _version import janitoo_version

DEBIAN_PACKAGE = False
filtered_args = []

for arg in sys.argv:
    if arg == "--debian-package":
        DEBIAN_PACKAGE = True
    else:
        filtered_args.append(arg)
sys.argv = filtered_args

def data_files_config(res, rsrc, src, pattern):
    for root, dirs, fils in os.walk(src):
        if src == root:
            sub = []
            for fil in fils:
                sub.append(os.path.join(root,fil))
            res.append((rsrc, sub))
            for dire in dirs:
                    data_files_config(res, os.path.join(rsrc, dire), os.path.join(root, dire), pattern)

data_files = []
data_files_config(data_files, 'docs','src/docs/','*')

setup(
    name = 'janitoo_raspberry_pancam',
    description = "The tutorial for Janitoo.",
    long_description = "With this tutorial you'll see how to create servers for your Raspberry Pi, deploy using Docker and use the network.",
    author='Sébastien GALLET aka bibi2100 <bibi21000@gmail.com>',
    author_email='bibi21000@gmail.com',
    nickname='bibi21000',
    url='https://github.com/bibi21000/janitoo_raspberry_pancam',
    git_url='https://github.com/bibi21000/janitoo_raspberry_pancam',
    doc_url='https://bibi21000.github.io/janitoo_raspberry_pancam',
    license = """
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
    """,
    version = janitoo_version,
    zip_safe = False,
    scripts=['src/scripts/jnt_raspberry_pancam'],
    packages = find_packages('src', exclude=["scripts", "docs", "config"]),
    package_dir = { '': 'src' },
    keywords = "core,raspberry,tutorial,dht,onewire",
    include_package_data=True,
    data_files = data_files,
    install_requires=[
                     'janitoo',
                     'janitoo_factory',
                     'janitoo_factory_exts',
                     'janitoo_raspberry',
                     'janitoo_raspberry_camera',
                     'janitoo_raspberry_i2c',
                     'janitoo_raspberry_i2c_pca9685',
                    ],
    dependency_links = [
      'https://github.com/bibi21000/janitoo/archive/master.zip#egg=janitoo',
      'https://github.com/bibi21000/janitoo_factory/archive/master.zip#egg=janitoo_factory',
      'https://github.com/bibi21000/janitoo_factory_exts/archive/master.zip#egg=janitoo_factory_exts',
      'https://github.com/bibi21000/janitoo_raspberry/archive/master.zip#egg=janitoo_raspberry',
      'https://github.com/bibi21000/janitoo_raspberry_camera/archive/master.zip#egg=janitoo_raspberry_camera',
      'https://github.com/bibi21000/janitoo_raspberry_i2c/archive/master.zip#egg=janitoo_raspberry_i2c',
      'https://github.com/bibi21000/janitoo_raspberry_i2c_pca9685/archive/master.zip#egg=janitoo_raspberry_i2c_pca9685',
    ],
    entry_points = {
        "janitoo.threads": [
            "pancam = janitoo_raspberry_pancam.thread_pancam:make_thread",
        ],
        "janitoo.components": [
            "pancam.stream = janitoo_raspberry_pancam.pancam:make_stream",
            "pancam.pancam = janitoo_raspberry_pancam.pancam:make_pancam",
            "pancam.servo = janitoo_raspberry_pancam.pancam:make_servo",
        ],
    },
)
