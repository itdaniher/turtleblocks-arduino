#!/usr/bin/env python
# Copyright (c)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os
from time import time

from gettext import gettext as _
from plugins.plugin import Plugin

from TurtleArt.tapalette import make_palette
from TurtleArt.talogo import media_blocks_dictionary, primitive_dictionary




class Plugin-example(Plugin):

    def __init__(self, parent):
        self._parent = parent

    def setup(self):
        pass

    def start(self):
        pass

    def quit(self):
        pass

    def stop(self):
        pass

    def clear(self):
        pass


