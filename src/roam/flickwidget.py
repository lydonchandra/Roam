## See https://code.google.com/p/flickcharm-python/
import copy
import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *

class FlickData:
    Steady = 0
    Pressed = 1
    ManualScroll = 2
    AutoScroll = 3
    Stop = 4

    def __init__(self):
        self.state = FlickData.Steady
        self.widget = None
        self.pressPos = QPoint(0, 0)
        self.offset = QPoint(0, 0)
        self.dragPos = QPoint(0, 0)
        self.speed = QPoint(0, 0)
        self.ignored = []


class FlickCharmPrivate:

    def __init__(self):
        self.flickData = {}
        self.ticker = QBasicTimer()


class FlickCharm(QObject):

    def __init__(self, parent = None):
        QObject.__init__(self, parent)
        self.d = FlickCharmPrivate()
        self.lastvalue = 0

    def activateOn(self, widget):
        if isinstance(widget, QWebView):
            frame = widget.page().mainFrame()
            widget.installEventFilter(self)
            self.d.flickData[widget] = FlickData()
            self.d.flickData[widget].widget = widget
            self.d.flickData[widget].state = FlickData.Steady

        if hasattr(widget, "viewport"):
            viewport = widget.viewport()
            viewport.installEventFilter(self)
            widget.installEventFilter(self)
            self.d.flickData[viewport] = FlickData()
            self.d.flickData[viewport].widget = widget
            self.d.flickData[viewport].state = FlickData.Steady

        if hasattr(widget, "setVerticalScrollMode"):
            widget.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

    def deactivateFrom(self, widget):
        if isinstance(widget, QWebView):
            widget.removeEventFilter(self)
            del(self.d.flickData[widget])
        else:
            viewport = widget.viewport()
            viewport.removeEventFilter(self)
            widget.removeEventFilter(self)
            del(self.d.flickData[viewport])


    def eventFilter(self, object, event):
        if not object.isWidgetType():
            return False

        eventType = event.type()
        if eventType != QEvent.MouseButtonPress and \
           eventType != QEvent.MouseButtonRelease and \
           eventType != QEvent.MouseMove:
            return False

        if event.modifiers() != Qt.NoModifier:
            return False

        if not self.d.flickData.has_key(object):
            return False

        data = self.d.flickData[object]
        found, newIgnored = removeAll(data.ignored, event)
        if found:
            data.ignored = newIgnored
            return False

        consumed = False

        if data.state == FlickData.Steady:
            if eventType == QEvent.MouseButtonPress:
                if event.buttons() == Qt.LeftButton:
                    consumed = True
                    data.state = FlickData.Pressed
                    data.pressPos = event.pos()
                    data.offset = scrollOffset(data.widget)

        elif data.state == FlickData.Pressed:
            if eventType == QEvent.MouseButtonRelease:
                consumed = True
                data.state = FlickData.Steady
                event1 = QMouseEvent(QEvent.MouseButtonPress,
                                     data.pressPos, Qt.LeftButton,
                                     Qt.LeftButton, Qt.NoModifier)
                event2 = QMouseEvent(event)
                data.ignored.append(event1)
                data.ignored.append(event2)
                QApplication.postEvent(object, event1)
                QApplication.postEvent(object, event2)
            elif eventType == QEvent.MouseMove:
                moved_pos = QCursor.pos() - data.pressPos
                if moved_pos.manhattanLength() < 200:
                    consumed = False
                else:
                    consumed = True
                    data.state = FlickData.ManualScroll
                    data.dragPos = QCursor.pos()
                    if not self.d.ticker.isActive():
                        self.d.ticker.start(20, self)

        elif data.state == FlickData.ManualScroll:
            if eventType == QEvent.MouseMove:
                consumed = True
                pos = event.pos()
                delta = pos - data.pressPos
                setScrollOffset(data.widget, pos, data.pressPos)
            elif eventType == QEvent.MouseButtonRelease:
                consumed = True
                data.state = FlickData.Steady

        return consumed

    def timerEvent(self, event):
        count = 0
        for data in self.d.flickData.values():
            if data.state == FlickData.ManualScroll:
                count += 1
                cursorPos = QCursor.pos()
                data.speed = cursorPos - data.dragPos
                data.dragPos = cursorPos

        if count == 0:
            self.d.ticker.stop()

        QObject.timerEvent(self, event);


def scrollOffset(widget):
    if isinstance(widget, QWebView):
        frame = widget.page().mainFrame()
        x = frame.evaluateJavaScript("window.scrollX")
        y = frame.evaluateJavaScript("window.scrollY")
    else:
        x = widget.horizontalScrollBar().value()
        y = widget.verticalScrollBar().value()
    return QPoint(x, y)


lastvalue = 0

def setScrollOffset(widget, current, press=None):
    up = current.y() > press.y()
    up = current.y() > lastvalue
    global lastvalue
    lastvalue = current.y()

    if isinstance(widget, QWebView):
        frame = widget.page().mainFrame()
        y = frame.evaluateJavaScript("window.scrollY;")
        if up:
            y -= 15
        else:
            y += 15
        frame.evaluateJavaScript("window.scrollTo(%d,%d);" % (current.x(), y))
    else:
        # calc the percentage moved
        if up:
            y = widget.verticalScrollBar().value() - 15
        else:
            y = widget.verticalScrollBar().value() + 15
        widget.verticalScrollBar().setValue(y)


def deaccelerate(speed, a=1, maxVal=64):
    x = qBound(-maxVal, speed.x(), maxVal)
    y = qBound(-maxVal, speed.y(), maxVal)
    if x > 0:
        x = max(0, x - a)
    elif x < 0:
        x = min(0, x + a)
    if y > 0:
        y = max(0, y - a)
    elif y < 0:
        y = min(0, y + a)
    return QPoint(x, y)


def qBound(minVal, current, maxVal):
    return max(min(current, maxVal), minVal)


def removeAll(list, val):
    found = False
    ret = []
    for element in list:
        if element == val:
            found = True
        else:
            ret.append(element)
    return (found, ret)
