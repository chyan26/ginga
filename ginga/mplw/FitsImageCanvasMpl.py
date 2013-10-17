#
# FitsImageCanvasMpl.py -- A FITS image widget with canvas drawing in Matplotlib
# 
# Eric Jeschke (eric@naoj.org)
#
# Copyright (c) Eric R. Jeschke.  All rights reserved.
# This is open-source software licensed under a BSD license.
# Please see the file LICENSE.txt for details.
#
from ginga.mplw import FitsImageMpl
from ginga.mplw.FitsImageCanvasTypesMpl import *


class FitsImageCanvasError(FitsImageMpl.FitsImageMplError):
    pass

class FitsImageCanvas(FitsImageMpl.FitsImageZoom,
                      DrawingMixin, CanvasMixin, CompoundMixin):

    def __init__(self, logger=None, rgbmap=None, settings=None,
                 bindmap=None, bindings=None):
        FitsImageMpl.FitsImageZoom.__init__(self, logger=logger,
                                           rgbmap=rgbmap,
                                           settings=settings,
                                           bindmap=bindmap,
                                           bindings=bindings)
        CompoundMixin.__init__(self)
        CanvasMixin.__init__(self)
        DrawingMixin.__init__(self, drawCatalog)

        self.setSurface(self)
        self.ui_setActive(True)

    def canvascoords(self, data_x, data_y, center=True):
        # data->canvas space coordinate conversion
        x, y = self.get_canvas_xy(data_x, data_y, center=center)
        # matplotlib usually plots in data coordinates
        return (float(x) / self._imgwin_wd, float(y) / self._imgwin_ht)

    def redraw_data(self, whence=0):
        super(FitsImageCanvas, self).redraw_data(whence=whence)

        if not self.figure:
            return
        self.draw()

        # refresh the matplotlib canvas
        self.figure.canvas.draw()


#END
