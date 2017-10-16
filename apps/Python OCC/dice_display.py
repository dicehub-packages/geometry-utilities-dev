
# DICE modules
# ============
from dice_tools import wizard, diceProperty, diceSlot
from dice_tools import DICEObject
from dice_tools.helpers.xview import View

import os
from time import time
import mmap
from tempfile import NamedTemporaryFile
from contextlib import contextmanager
import weakref
import sys

from OCC.Display import OCCViewer
from OCC import Graphic3d

from collections import namedtuple

NoModifier = 0x00000000
ShiftModifier = 0x02000000
ControlModifier = 0x04000000
AltModifier = 0x08000000
MetaModifier = 0x10000000
KeypadModifier = 0x20000000
GroupSwitchModifier = 0x40000000

LeftButton = 0x00000001
RightButton = 0x00000002
MidButton = 0x00000004

if 'win' not in sys.platform:
    os.environ['CASROOT'] = os.path.join(sys.prefix, 'share', 'oce-0.18')

class point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class DiceDisplay(View):

    def __init__(self, size_x=1, size_y=1, **kwargs):
        super().__init__(**kwargs)
        self.__size_x = size_x
        self.__size_y = size_y

        self.display = OCCViewer.Viewer3d(None)
        self.display.Create()

        self.display.set_bg_gradient_color(206, 215, 222, 128, 128, 128)
        self.display.display_trihedron()
        self.display.SetModeShaded()
        self.display.DisableAntiAliasing()
        self.display.thisown = False

        self.__render_deferred = False

        self._drawbox = False
        self._zoom_area = False
        self._select_area = False
        self._inited = False
        self._leftisdown = False
        self._middleisdown = False
        self._rightisdown = False
        self._selection = None
        self._drawtext = True
        self._qApp = None
        self._key_map = {}
        self._current_cursor = "arrow"
        self._available_cursors = {}
        self._mouse_btn = 0

    def size_changed(self, size_x, size_y):
        """
        Size changed event handler.

        :param size_x: New size x dimension.
        :param size_y: New size y dimension.
        """
        size_x = max(1, size_x)
        size_y = max(1, size_y)
        self.__size_x = size_x
        self.__size_y = size_y
        self.display.SetSize(size_x, size_y)
        self.render()
        
    '''
    Mouse Events
    ============
    '''
    def mouse_press(self, btn, x, y, modifiers):
        """
        Mouse button press event handler.

        :param btn: Mouse button code.
        :param x: X coordinate of position where mouse pressed.
        :param y: Y coordinate of position where mouse pressed.
        :param modifiers: Keyboard modifiers, i.e. 'Alt', 'Control', 'Shift'.
        """

        self.dragStartPos = point(x, y)
        self.display.StartRotation(self.dragStartPos.x, self.dragStartPos.y)
        self._mouse_btn |= btn
        self.render()

    def mouse_release(self, btn, x, y, modifiers):
        """
        Mouse button release event handler.

        :param btn: Mouse button code.
        :param x: X coordinate of position where mouse pressed.
        :param y: Y coordinate of position where mouse pressed.
        :param modifiers: Keyboard modifiers, i.e. 'Alt', 'Control', 'Shift'.
        """

        pt = point(x, y)
        modifiers = modifiers

        if btn == LeftButton:
            if self._select_area:
                [Xmin, Ymin, dx, dy] = self._drawbox
                self.display.SelectArea(Xmin, Ymin, Xmin + dx, Ymin + dy)
                self._select_area = False
            else:
                # multiple select if shift is pressed
                if modifiers == ShiftModifier:
                    self.display.ShiftSelect(pt.x, pt.y)
                else:
                    # single select otherwise
                    self.display.Select(pt.x, pt.y)

                    # if (self.display.selected_shapes is not None) and HAVE_PYQT_SIGNAL:
                    #     self.sig_topods_selected.emit(self.display.selected_shapes)


        elif btn == RightButton:
            if self._zoom_area:
                [Xmin, Ymin, dx, dy] = self._drawbox
                self.display.ZoomArea(Xmin, Ymin, Xmin + dx, Ymin + dy)
                self._zoom_area = False

        self._mouse_btn &= ~btn
        self.render()

    def mouse_move(self, x, y, modifiers):
        """
        Mouse move event handler.

        :param x: X coordinate of position mouse moved to.
        :param y: Y coordinate of position mouse moved to.
        :param modifiers: Keyboard modifiers, i.e. 'Alt', 'Control', 'Shift'.
        """

        pt = point(x, y)
        buttons = self._mouse_btn
        # ROTATE
        if (buttons == LeftButton and
                not modifiers == ShiftModifier):
            dx = pt.x - self.dragStartPos.x
            dy = pt.y - self.dragStartPos.y
            self.cursor = "rotate"
            self.display.Rotation(pt.x, pt.y)
            self._drawbox = False
        # DYNAMIC ZOOM
        elif (buttons == RightButton and
              not modifiers == ShiftModifier):
            self.cursor = "zoom"
            self.display.Repaint()
            self.display.DynamicZoom(abs(self.dragStartPos.x),
                                      abs(self.dragStartPos.y), abs(pt.x),
                                      abs(pt.y))
            self.dragStartPos.x = pt.x
            self.dragStartPos.y = pt.y
            self._drawbox = False
        # PAN
        elif buttons == MidButton:
            dx = pt.x - self.dragStartPos.x
            dy = pt.y - self.dragStartPos.y
            self.dragStartPos.x = pt.x
            self.dragStartPos.y = pt.y
            self.cursor = "pan"
            self.display.Pan(dx, -dy)
            self._drawbox = False
        # DRAW BOX
        # ZOOM WINDOW
        elif (buttons == RightButton and
              modifiers == ShiftModifier):
            self._zoom_area = True
            self.cursor = "zoom-area"
            # self.DrawBox(evt)
        # SELECT AREA
        elif (buttons == LeftButton and
              modifiers == ShiftModifier):
            self._select_area = True
            # self.DrawBox(evt)
        else:
            self._drawbox = False
            self.display.MoveTo(pt.x, pt.y)
        self.render()

    def mouse_wheel(self, delta_x, delta_y, x, y, modifiers):
        """
        Mouse wheel event handler.

        :param delta_x: Unused.
        :param delta_y: Mouse wheel turn offset.
        :param x: X coordinate of position where mouse wheel was turned.
        :param y: Y coordinate of position where mouse wheel was turned.
        :param modifiers: Keyboard modifiers, i.e. 'Alt', 'Control', 'Shift'.
        """

        if delta_y > 0:
            zoom_factor = 2.
        else:
            zoom_factor = 0.5
        self.display.Repaint()
        self.display.ZoomFactor(zoom_factor)
        self.render()

    def __deferred_render(self):
        if self.__render_deferred:
            self.render(False)

    def render(self, deferred=True):
        """
        Starts scene rendering.

        :param deferred: When True rendering wil be started next tick.
        """
        if deferred:
            if not self.__render_deferred:
                self.__render_deferred = True
                wizard.timeout(self.__deferred_render, 0)  # render next tick
        else:
            self.__render_deferred = False
            data = self.display.GetImageData(Graphic3d.Graphic3d_BT_RGBA)
            size = self.display.GetSize()
            self.updated(size, data)

    def updated(self, size, data):
        self.update(size[0], size[1], True, data)