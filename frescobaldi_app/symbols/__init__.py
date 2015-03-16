# This file is part of the Frescobaldi project, http://www.frescobaldi.org/
#
# Copyright (c) 2008 - 2014 by Wilbert Berendsen
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# See http://www.gnu.org/licenses/ for more information.

"""
Code to use LilyPond-generated SVGs as icons.
The default black color will be adjusted to the default Text color.
"""

from __future__ import unicode_literals

import os

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QApplication, QIcon, QIconEngineV2, QImage, QPainter, QPixmap, QStyleOption
from PyQt4.QtSvg import QSvgRenderer

__all__ = ["icon"]


_icons = {}
_pixmaps = {}


def icon(name, palette=None):
    """Returns a QIcon that shows a LilyPond-generated SVG in the default text color."""
    if not palette:
        palette = QApplication.palette()
    key = (name, palette.foreground().color().rgba(),
           palette.highlightedText().color().rgba())
    try:
        return _icons[key]
    except KeyError:
        icon = _icons[key] = QIcon(Engine(name, palette))
        return icon


def pixmap(name, size, mode, state, palette):
    """Returns a (possibly cached) pixmap of the name and size with the default text color.
    
    The state argument is ignored for now.
    
    """
    if mode == QIcon.Selected:
        color = palette.highlightedText().color()
    else:
        color = palette.foreground().color()
    key = (name, size.width(), size.height(), color.rgba(), mode)
    try:
        return _pixmaps[key]
    except KeyError:
        i = QImage(size, QImage.Format_ARGB32_Premultiplied)
        i.fill(0)
        painter = QPainter(i)
        # render SVG symbol
        QSvgRenderer(os.path.join(__path__[0], name + ".svg")).render(painter)
        # recolor to text color
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(i.rect(), color)
        painter.end()
        # let style alter the drawing based on mode, and create QPixmap
        pixmap = QApplication.style().generatedIconPixmap(mode, QPixmap.fromImage(i), QStyleOption())
        _pixmaps[key] = pixmap
        return pixmap


class Engine(QIconEngineV2):
    """Engine to provide renderings of SVG icons in the default text color."""
    def __init__(self, name, palette):
        super(Engine, self).__init__()
        self._name = name
        self._palette = palette
        
    def pixmap(self, size, mode, state):
        return pixmap(self._name, size, mode, state, self._palette)
        
    def paint(self, painter, rect, mode, state):
        p = self.pixmap(rect.size(), mode, state)
        painter.drawPixmap(rect, p)
        

