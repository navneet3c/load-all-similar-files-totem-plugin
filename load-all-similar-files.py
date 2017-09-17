"""
Load All Similar Files - Totem Plugin (see README.md)

Created by Navneet <navneetmails@gmail.com>
"""

from gi.repository import GLib, GObject, Peas
import os.path
from urllib import parse
import ntpath

class LoadAllSimilarFilesPlugin(GObject.Object, Peas.Activatable):
    __gtype_name__ = 'LoadAllSimilarFilesPlugin'

    object = GObject.property(type=GObject.Object)
    dst_files_list = []

    def __init__(self):
        GObject.Object.__init__(self)

        self._totem = None
        dst_files_list = []

    ###########################################################################
    # Totem plugin methods
    ###########################################################################

    def do_activate(self):
        self._totem = self.object
        dst_files_list = []

        # Register handlers
        self._totem.connect('file-opened', self.on_file_opened)

    def do_deactivate(self):
        self._totem = None
        dst_files_list = []

    ###########################################################################
    # Handlers
    ###########################################################################

    def on_file_opened(self, to, file_path):
        #print("file_path taken:",  file_path)
        GLib.timeout_add(1000, self.generate_file_list, file_path)
        
    ###########################################################################
    # Helpers
    ###########################################################################

    def generate_file_list(self, file_path):
        if not file_path.startswith("file://"):
            return False
        
        playing_file = self._totem.get_title_at_playlist_pos(self._totem.get_playlist_pos())
        if playing_file in self.dst_files_list:
            return False
        else:
            self.dst_files_list = []
        
        file_path = file_path.replace("file://", "", 1)
        file_path = parse.unquote(file_path) 
        file_name, file_extension = os.path.splitext(file_path)
        file_name = ntpath.basename(file_path)
        file_dir = os.path.dirname(file_path)
        
        if not os.path.exists(file_dir):
            return False
        for file in os.listdir(file_dir):
            if file.endswith(file_extension):
                self.dst_files_list.append(file.rsplit(file_extension, 1)[0])
        
        self.dst_files_list.sort()
        elem_idx = self.dst_files_list.index(file_name.rsplit(file_extension, 1)[0])
        self.dst_files_list = self.dst_files_list[elem_idx+1:]
        
        for file in self.dst_files_list:
            #print ("file://" + parse.quote(os.path.join(file_dir, file+file_extension)))
            self._totem.add_to_playlist("file://" + parse.quote(os.path.join(file_dir, file+file_extension)), file, False)
        
        return False
