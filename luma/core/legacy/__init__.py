# -*- coding: utf-8 -*-
# Copyright (c) 2017-18 Richard Hull and contributors
# See LICENSE.rst for details.

"""
These methods were originally present in the old MAX7219 driver, and are
preserved here only to aid migration away from that library. The functions are
denoted 'legacy' to discourage use - you are encouraged to use the various
drawing capabilities in the Pillow library instead.
"""

from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.core.sprite_system import framerate_regulator
from luma.core.legacy.font import DEFAULT_FONT

MY_SCROLLING_FLAG = False
MY_STOP_FLAG = False

def textsize(txt, font=None):
    """
    Calculates the bounding box of the text, as drawn in the specified font.
    This method is most useful for when the
    :py:class:`~luma.core.legacy.font.proportional` wrapper is used.

    :param txt: The text string to calculate the bounds for
    :type txt: str
    :param font: The font (from :py:mod:`luma.core.legacy.font`) to use.
    """
    font = font or DEFAULT_FONT
    src = [c for ascii_code in txt for c in font[ord(ascii_code)]]
    return (len(src), 8)


def text(draw, xy, txt, fill=None, font=None):
    """
    Draw a legacy font starting at :py:attr:`x`, :py:attr:`y` using the
    prescribed fill and font.

    :param draw: A valid canvas to draw the text onto.
    :type draw: PIL.ImageDraw
    :param txt: The text string to display (must be ASCII only).
    :type txt: str
    :param xy: An ``(x, y)`` tuple denoting the top-left corner to draw the
        text.
    :type xy: tuple
    :param fill: The fill color to use (standard Pillow color name or RGB
        tuple).
    :param font: The font (from :py:mod:`luma.core.legacy.font`) to use.
    """
    font = font or DEFAULT_FONT
    x, y = xy
    for ch in txt:
        for byte in font[ord(ch)]:
            for j in range(8):
                if byte & 0x01 > 0:
                    draw.point((x, y + j), fill=fill)

                byte >>= 1
            x += 1

def stop_scrolling():
    global MY_STOP_FLAG
    print("luma.legacy stop_scrolling")
    if(MY_SCROLLING_FLAG == True):
        MY_STOP_FLAG = True

def show_message(device, msg, y_offset=0, fill=None, font=None,
                 scroll_delay=0.03):
    """
    Scrolls a message right-to-left across the devices display.

    :param device: The device to scroll across.
    :param msg: The text message to display (must be ASCII only).
    :type msg: str
    :param y_offset: The row to use to display the text.
    :type y_offset: int
    :param fill: The fill color to use (standard Pillow color name or RGB
        tuple).
    :param font: The font (from :py:mod:`luma.core.legacy.font`) to use.
    :param scroll_delay: The number of seconds to delay between scrolling.
    :type scroll_delay: float
    """
    global MY_SCROLLING_FLAG
    global MY_STOP_FLAG
    MY_SCROLLING_FLAG = True

    fps = 0 if scroll_delay == 0 else 1.0 / scroll_delay
    regulator = framerate_regulator(fps)
    font = font or DEFAULT_FONT
    with canvas(device) as draw:
        w, h = textsize(msg, font)

    x = device.width
    virtual = viewport(device, width=w + x + x, height=device.height)

    with canvas(virtual) as draw:
        text(draw, (x, y_offset), msg, font=font, fill=fill)

    i = 0
    while i <= w + x:
        with regulator:
            virtual.set_position((i, 0))
            i += 1
        if(MY_STOP_FLAG):
            MY_STOP_FLAG = False
            with canvas(virtual) as draw:
                text(draw, (x, y_offset), "    ", font=font, fill=fill)
            i = w + x + 1
    MY_SCROLLING_FLAG = False