#
# HeaderBase.py -- FITS Header plugin base class for fits viewer
#
# Eric Jeschke (eric@naoj.org)
#
# Copyright (c) Eric R. Jeschke.  All rights reserved.
# This is open-source software licensed under a BSD license.
# Please see the file LICENSE.txt for details.
#
from collections import OrderedDict

from ginga import GingaPlugin
from ginga.misc import Bunch
import ginga.util.six as six
from ginga.gw import Widgets


class Header(GingaPlugin.GlobalPlugin):

    def __init__(self, fv):
        # superclass defines some variables for us, like logger
        super(Header, self).__init__(fv)

        self._image = None
        self.channel = {}
        self.active = None
        self.info = None
        self.columns = [('Keyword', 'key'),
                        ('Value', 'value'),
                        ('Comment', 'comment'),
                        ]

        prefs = self.fv.get_preferences()
        self.settings = prefs.createCategory('plugin_Header')
        self.settings.addDefaults(sortable=False)
        self.settings.load(onError='silent')

        fv.set_callback('add-channel', self.add_channel)
        fv.set_callback('delete-channel', self.delete_channel)
        fv.set_callback('active-image', self.focus_cb)

    def build_gui(self, container):
        nb = Widgets.StackWidget()
        self.nb = nb
        container.add_widget(nb, stretch=1)

    def _create_header_window(self, info):
        vbox = Widgets.VBox()
        vbox.set_margins(2, 2, 2, 2)

        table = Widgets.TreeView(auto_expand=True)
        self.table = table
        table.setup_table(self.columns, 1, 'key')

        vbox.add_widget(table, stretch=1)

        # create sort toggle
        cb = Widgets.CheckBox("Sortable")
        cb.add_callback('activated', lambda w, tf: self.set_sortable_cb(info))
        hbox = Widgets.HBox()
        hbox.add_widget(cb, stretch=0)
        hbox.add_widget(Widgets.Label(''), stretch=1)
        vbox.add_widget(hbox, stretch=0)

        # toggle sort
        if self.settings.get('sortable', False):
            cb.set_state(True)

        info.setvals(widget=vbox, table=table, sortw=cb)
        return vbox

    def set_header(self, info, image):
        if self._image == image:
            # we've already handled this header
            return
        self.logger.debug("setting header")
        header = image.get_header()
        table = info.table

        is_sorted = info.sortw.get_state()
        tree_dict = OrderedDict()

        keys = list(header.keys())
        if is_sorted:
            keys.sort()
        for key in keys:
            card = header.get_card(key)
            ## tree_dict[key] = Bunch.Bunch(key=card.key,
            ##                              value=str(card.value),
            ##                              comment=card.comment,
            ##                              __terminal__=True)
            tree_dict[key] = card

        table.set_tree(tree_dict)

        self.logger.debug("setting header done ({0})".format(is_sorted))
        self._image = image

    def add_channel(self, viewer, chinfo):
        chname = chinfo.name
        info = Bunch.Bunch(chname=chname)
        sw = self._create_header_window(info)

        self.nb.add_widget(sw)
        index = self.nb.index_of(sw)
        info.setvals(widget=sw)
        self.channel[chname] = info

        fitsimage = chinfo.fitsimage
        fitsimage.set_callback('image-set', self.new_image_cb, info)

    def delete_channel(self, viewer, chinfo):
        chname = chinfo.name
        self.logger.debug("deleting channel %s" % (chname))
        widget = self.channel[chname].widget
        self.nb.remove(widget, delete=True)
        self.active = None
        self.info = None
        del self.channel[chname]

    def focus_cb(self, viewer, fitsimage):
        chname = self.fv.get_channelName(fitsimage)
        chinfo = self.fv.get_channelInfo(chname)
        chname = chinfo.name

        if self.active != chname:
            widget = self.channel[chname].widget
            index = self.nb.index_of(widget)
            self.nb.set_index(index)
            self.active = chname
            self.info = self.channel[self.active]

        image = fitsimage.get_image()
        if image is None:
            return
        self.set_header(self.info, image)

    def start(self):
        names = self.fv.get_channelNames()
        for name in names:
            chinfo = self.fv.get_channelInfo(name)
            self.add_channel(self.fv, chinfo)

    def new_image_cb(self, fitsimage, image, info):
        self.set_header(info, image)

    def set_sortable_cb(self, info):
        self._image = None
        chinfo = self.fv.get_channelInfo(info.chname)
        image = chinfo.fitsimage.get_image()
        self.set_header(info, image)

    def __str__(self):
        return 'header'

#END
