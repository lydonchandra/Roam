import os
import sys

try:
    import vidcap
    from roam.editorwidgets import VideoCapture as vc

    hascamera = True
except ImportError:
    hascamera = False

from PyQt4.QtGui import QDialog, QGridLayout, QLabel, QLayout, QPixmap, QFileDialog, QAction, QToolButton, QIcon, \
    QToolBar, QPainter, QPen
from PyQt4.QtGui import QWidget, QImage, QSizePolicy, QTextDocument
from PyQt4.QtCore import QByteArray, pyqtSignal, QVariant, QTimer, Qt, QSize, QDateTime, QPointF

from qgis.core import QgsExpression
from PIL.ImageQt import ImageQt

from roam.editorwidgets.core import EditorWidget, LargeEditorWidget, registerwidgets
from roam.editorwidgets.uifiles.imagewidget import QMapImageWidget
from roam.editorwidgets.uifiles import drawingpad
from roam.ui.uifiles import actionpicker_widget, actionpicker_base
from roam.popupdialogs import PickActionDialog
from roam import utils
from roam.api import RoamEvents

import roam.config
import roam.resources_rc


class CameraError(Exception):
    pass


def stamp_from_config(image, config):
    stamp = config.get('stamp', None)
    form = config.get('formwidget', None)
    feature = None
    print stamp
    if not stamp:
        return image

    if form:
        feature = form.to_feature()
    image = stamp_image(image, stamp['value'], stamp['position'], feature)
    return image


def stamp_image(image, expression_str, position, feature):
    painter = QPainter(image)
    data = QgsExpression.replaceExpressionText(expression_str, feature, None)
    if not data:
        return image

    data = data.replace(r"\n", "<br>")
    style = """
    body {
        color: yellow;
    }
    """
    doc = QTextDocument()
    doc.setDefaultStyleSheet(style)
    data = "<body>{}</body>".format(data)
    doc.setHtml(data)
    print data
    point = QPointF(20, 20)

    # Wrap the text so we don't go crazy
    if doc.size().width() > 300:
        doc.setTextWidth(300)
    if position == "top-left":
        point = QPointF(20, 20)
    elif position == "top-right":
        x = image.width() - 20 - doc.size().width()
        point = QPointF(x, 20)
    elif position == "bottom-left":
        point = QPointF(20, image.height() - 20 - doc.size().height())
    elif position == "bottom-right":
        x = image.width() - 20 - doc.size().width()
        y = image.height() - 20 - doc.size().height()
        point = QPointF(x, y)
    painter.translate(point)
    doc.drawContents(painter)
    return image


def save_image(image, path, name):
    if isinstance(image, QByteArray):
        _image = QImage()
        _image.loadFromData(image)
        image = _image

    if not os.path.exists(path):
        os.mkdir(path)

    saved = image.save(os.path.join(path, name), "JPG")
    return saved, name


class _CameraWidget(QWidget):
    imagecaptured = pyqtSignal(QPixmap)
    done = pyqtSignal()

    def __init__(self, parent=None):
        super(_CameraWidget, self).__init__(parent)
        self.cameralabel = QLabel()
        self.cameralabel.setScaledContents(True)
        self.setLayout(QGridLayout())
        self.toolbar = QToolBar()
        spacer = QWidget()
        # spacer.setMinimumWidth(30)
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.toolbar.setIconSize(QSize(48, 48))
        self.toolbar.addWidget(spacer)
        self.swapaction = self.toolbar.addAction(QIcon(":/widgets/cameraswap"), "Swap Camera")
        self.swapaction.triggered.connect(self.swapcamera)
        self.cameralabel.mouseReleaseEvent = self.takeimage
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self.toolbar)
        self.layout().addWidget(self.cameralabel)
        self.timer = QTimer()
        self.timer.setInterval(20)
        self.timer.timeout.connect(self.showimage)
        self.cam = None
        self.pixmap = None
        self.currentdevice = 1

    def swapcamera(self):
        self.stop()
        if self.currentdevice == 0:
            self.start(1)
        else:
            self.start(0)

    def showimage(self):
        if self.cam is None:
            return

        img = self.cam.getImage()
        self.image = ImageQt(img)
        pixmap = QPixmap.fromImage(self.image)
        self.cameralabel.setPixmap(pixmap)

    def takeimage(self, *args):
        self.timer.stop()
        img = self.cam.getImage()
        self.image = ImageQt(img)
        self.pixmap = QPixmap.fromImage(self.image)
        self.cameralabel.setPixmap(self.pixmap)
        self.imagecaptured.emit(self.pixmap)
        self.done.emit()

    @property
    def camera_res(self):
        width, height = tuple(roam.config.settings['camera_res'].split(','))
        return width, height

    def start(self, dev=1):
        try:
            self.cam = vc.Device(dev)
            try:
                width, height = self.camera_res
                self.cam.setResolution(int(width), int(height))
            except KeyError:
                pass
            self.currentdevice = dev
        except vidcap.error:
            if dev == 0:
                utils.error("Could not start camera")
                raise CameraError("Could not start camera")
            self.start(dev=0)
            return

        roam.config.settings['camera'] = self.currentdevice
        self.timer.start()

    def stop(self):
        self.timer.stop()
        del self.cam
        self.cam = None


class CameraWidget(LargeEditorWidget):
    def __init__(self, *args, **kwargs):
        super(CameraWidget, self).__init__(*args, **kwargs)
        self._value = None

    def createWidget(self, parent):
        return _CameraWidget(parent)

    def initWidget(self, widget):
        widget.imagecaptured.connect(self.image_captured)
        widget.done.connect(self.emit_finished)

    def image_captured(self, pixmap):
        image = stamp_from_config(pixmap, self.config)
        self._value = image
        self.emitvaluechanged(self._value)

    def after_load(self):
        camera = roam.config.settings.get('camera', 1)
        try:
            self.widget.start(dev=camera)
        except CameraError as ex:
            self.emit_cancel(reason=ex.message)
            return

    def value(self):
        return self._value

    def __del__(self):
        if self.widget:
            self.widget.stop()


class DrawingPadWidget(LargeEditorWidget):
    def __init__(self, *args, **kwargs):
        super(DrawingPadWidget, self).__init__(*args, **kwargs)
        self.canvas = kwargs.get('map', None)

    def createWidget(self, parent=None):
        pad1 = drawingpad.DrawingPad(parent=parent)
        return pad1

    def initWidget(self, widget):
        widget.toolStamp.pressed.connect(self.stamp_image)
        widget.actionSave.triggered.connect(self.emit_finished)
        widget.actionCancel.triggered.connect(self.emit_cancel)
        widget.canvas = self.canvas

    def stamp_image(self):
        image = self.widget.pixmap
        image = stamp_from_config(image, self.config)
        self.widget.pixmap = image

    def value(self):
        return self.widget.pixmap

    def setvalue(self, value):
        self.widget.pixmap = value


class ImageWidget(EditorWidget):
    widgettype = 'Image'

    def __init__(self, *args, **kwargs):
        super(ImageWidget, self).__init__(*args)
        self.tobase64 = False
        self.defaultlocation = ''
        self.savetofile = False
        self.modified = False
        self.filename = None

        self.selectAction = QAction(QIcon(r":\widgets\folder"), "From folder", None)
        self.cameraAction = QAction(QIcon(":\widgets\camera"), "Camera", None)
        self.drawingAction = QAction(QIcon(":\widgets\drawing"), "Drawing/Map snapshot", None)

        self.selectAction.triggered.connect(self._selectImage)
        self.cameraAction.triggered.connect(self._selectCamera)
        self.drawingAction.triggered.connect(self._selectDrawing)


    def createWidget(self, parent):
        return QMapImageWidget(parent)

    def initWidget(self, widget):
        widget.openRequest.connect(self.showlargeimage)
        widget.imageloaded.connect(self.emitvaluechanged)
        widget.imageremoved.connect(self.emitvaluechanged)
        widget.imageloadrequest.connect(self.showpicker)
        widget.annotateimage.connect(self._selectDrawing)

    def showpicker(self):
        actionpicker = PickActionDialog(msg="Select image source")
        actionpicker.addactions(self.actions)
        actionpicker.exec_()

    @property
    def actions(self):
        yield self.selectAction
        if hascamera:
            yield self.cameraAction
        yield self.drawingAction

    def _selectImage(self):
        # Show the file picker
        defaultlocation = os.path.expandvars(self.defaultlocation)
        image = QFileDialog.getOpenFileName(self.widget, "Select Image", defaultlocation)
        utils.debug(image)
        if image is None or not image:
            return

        self.widget.loadImage(image)
        self.modified = True

    def _selectDrawing(self, *args):
        image = self.widget.orignalimage
        self.open_large_widget(DrawingPadWidget, image, self.phototaken, self.config)

    def _selectCamera(self):
        self.open_large_widget(CameraWidget, None, self.phototaken_camera, self.config)

    def phototaken_camera(self, value):
        pix = value.copy()
        self.setvalue(pix)
        self.modified = True

    def phototaken(self, value):
        self.setvalue(value)
        self.modified = True

    def updatefromconfig(self):
        self.defaultlocation = self.config.get('defaultlocation', '')
        self.savetofile = self.config.get('savetofile', False)
        if not self.savetofile and self.field and self.field.type() == QVariant.String:
            self.tobase64 = True

    def validate(self, *args):
        return not self.widget.isDefault

    def showlargeimage(self, pixmap):
        RoamEvents.openimage.emit(pixmap)

    def get_filename(self):
        name = QDateTime.currentDateTime().toString("yyyy-MM-dd-hh-mm-ss-zzz.JPG")
        return name

    def save(self, folder, filename):
        saved, name = save_image(self.widget.getImage(), folder, filename)
        return saved

    def setvalue(self, value):
        if self.savetofile and isinstance(value, basestring):
            self.filename = value

        if isinstance(value, QPixmap):
            self.widget.loadImage(value, fromfile=self.savetofile)
            return

        if self.tobase64 and value:
            value = QByteArray.fromBase64(value)

        self.widget.loadImage(value, fromfile=self.savetofile)

    def value(self):
        image = self.widget.getImage()
        if self.tobase64 and image:
            image = image.toBase64()
            return image.data()

        return image

