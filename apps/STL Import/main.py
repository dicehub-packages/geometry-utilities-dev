"""
GeometryImport
==============

Copyright (c) 2014-2015 by DICE Developers
All rights reserved.
"""

# Standard Python modules
# =======================
import os
import sys
import weakref
import json
import random
import shutil
from multiprocessing import Process
import threading
random.seed()

# External modules
# ================
import yaml
import stl.mesh
import stl.stl

# DICE modules
# ============
from dice_tools import *
from dice_tools.helpers.file_operations import FileOperations
from dice_vtk import VisApp
from dice_vtk.geometries import AxesWidget, Cube
from dice_vtk.geometries import VtkNumpySTL
from dice_tools.helpers import FileOperations, DictHelper
from dice_tools.helpers import JsonOrderedDict
from dice_tools.helpers.xmodel import standard_model, list_of_dicts_model

# App modules
# ============
from stl_model import StlMesh, StlFile


class GeometryImport(
        VisApp,
        Application,
        FileOperations,
        DictHelper):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        """
        Constructor of vtkApp
        """
        self.debug("Starting Applications")

        self.__history_pos = -1
        self.__stl_model = standard_model(StlMesh, StlFile)
        self.__history_model = list_of_dicts_model('cmd', 'paramStr')

        wizard.subscribe(self, self)
        wizard.subscribe(self, self.__stl_model)
        wizard.subscribe(self, self.__history_model)
        wizard.subscribe(self.w_geometry_object_clicked)

        self.__worker = None

        self.__prepare_dirs()
        self.__prepare_config()
        self.__load_history()

        self.__value = 1

        self.__cog = None
        self.__intertia_matrix = None
        self.__volume = None


    def connected(self):
        super().connected()
        if list(self.__stl_model.elements_of(StlFile)):
            self.set_progress(-1)
        else:
            self.set_progress(0)

    def w_geometry_object_clicked(self, obj, *args, **kwargs):
        if obj == None:
            self.stl_model.current_item = None

    def w_model_selection_changed(self, model, selected, deselected):
        if model == self.__stl_model:
            for v in deselected:
                if isinstance(v, StlFile):
                    for m in v.elements:
                        m.vtk_obj.set_selected(False)
                else:
                    v.vtk_obj.set_selected(False)
            for v in selected:
                if isinstance(v, StlFile):
                    for m in v.elements:
                        m.vtk_obj.set_selected(True)
                else:
                    v.vtk_obj.set_selected(True)

    def __prepare_config(self):
        conf = self.config_path("config.json")
        self.config = JsonOrderedDict(conf)
        for v in self.config.setdefault('stl', []):
            file = self.__add_file(*v)
            path = self.run_path('files', file.name + '.stl')
            for m in stl.mesh.Mesh.from_multi_file(path):
                self.__add_mesh(file, m, m.name.decode('ascii', errors='ignore'))
            file.loading = False
        return self.config

    def input_changed(self, input_data):
        self.__input_data = input_data
        stl_input = self.__input_data.get('stl_files', {})
        for v in list(self.__stl_model.elements_of(StlFile)):
            if v.app and v.app not in stl_input:
                self.delete_file(v)
        for app, sources in stl_input.items():
            sources = sources or []
            for v in list(self.__stl_model.elements_of(StlFile)):
                if v.app == app:
                    if v.source not in sources:
                        self.delete_file(v)
                    else:
                        modified = os.stat(v.source).st_mtime
                        if modified != v.modified:
                            self.delete_file(v) 
            for s in sources:
                s = self.workflow_path(s)
                for v in list(self.__stl_model.elements_of(StlFile)):
                    if v.app == app and s == v.source:
                        break
                else:
                    action = dict(cmd = 'import',
                            params = dict(source = s, app = app))
                    self.__apply_action(action)
        self.set_progress(-1)

    def __decorated_history(self):
        hist = self.__history.to_simple_list()
        for i in range(len(hist)):
            cmd = hist[i]['cmd'] if 'cmd' in hist[i] else ''
            method = getattr(self, "run_"+cmd) if cmd != '' else None
            hist[i]['doc'] = method.__doc__ if method is not None else cmd
            hist[i]['parameterStr'] = str(dict(hist[i]['parameters'])) if 'parameters' in hist[i] else ''
        return hist

    @diceSlot(name="deleteSelected")
    def delete_selected(self):
        for v in list(self.__stl_model.selection):
            v.delete()

    @diceSlot(name="splitSelected")
    def split_selected(self):
        for v in list(self.__stl_model.selection):
            if isinstance(v, StlFile):
                v.split()

    @diceSlot(name="clearHistory")
    def clear_history(self):
        self.__history_model.root_elements.clear()
        history_file = self.config_path("history.log")
        with open(history_file, 'w') as f:
            pass

    @diceSlot(name="removeLastAction")
    def remove_last_action(self):
        action = self.__history_model.root_elements.pop()
        offset = action['offset']
        history_file = self.config_path("history.log")
        with open(history_file, 'r+') as f:
            f.truncate(offset)

    @diceSlot(name="removeLastActionAndReplay")
    def remove_last_action_and_replay(self):
        action = self.__history_model.root_elements.pop()
        offset = action['offset']
        history_file = self.config_path("history.log")
        with open(history_file, 'r+') as f:
            f.truncate(offset)
        self.__replay_actions()

    @diceSlot(name="replay")
    def replay(self):
        self.__replay_actions()

    def __load_history(self):
        history_file = self.config_path("history.log")
        decoder = json.JSONDecoder()
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                buf = f.read()
                offset = 0
                while buf:
                    action, pos = decoder.raw_decode(buf)
                    buf = buf[pos:].lstrip()
                    self.__add_action_to_model(action, offset)
                    offset = pos

    def __add_action_to_model(self, action, offset):
        action['offset'] = offset
        method = getattr(self, '_action_' + action['cmd'])
        action['doc'] = method.__doc__
        action['paramStr'] = \
            str(dict(action['params'])) if 'params' in action else ''
        self.__history_model.root_elements.append(action)

    def __save_action(self, action):
        history_file = self.config_path("history.log")
        with open(history_file, 'a') as f:
            offset = f.tell()
            f.write(json.dumps(action)+'\n')
            return offset

    def __prepare_dirs(self):
        if not os.path.exists(self.run_path('files')):
            os.mkdir(self.run_path('files'))

        wizard.subscribe(self, 'camera_updated')

    def __replay_actions(self, start = 0):
        for v in list(self.__stl_model.elements_of(StlFile)):
            action = dict(cmd = 'delete_file',
                params = dict(file = v.name))
            self.__apply_action(action, False)

        self.input_changed(self.__input_data)
        self.__history_pos = start
        for i in range(start, len(self.__history_model.root_elements)):
            self.__apply_action(self.__history_model.root_elements[i], False)

    def __apply_action(self, action, save = True):
        getattr(self, '_action_' + action['cmd'])(**action['params'])
        self.__history_pos += 1
        if save:
            offset = self.__save_action(action)
            self.__add_action_to_model(action, offset)

    '''
    Actions
    =======
    '''
    @staticmethod
    def _unique_name(path, name):
        counter = 0
        while True:
            new_name, ext = os.path.splitext(name)
            if counter > 0:
                new_name += '_%i'%counter
            new_path = os.path.join(path, new_name + ext)
            if not os.path.exists(new_path):
                return new_name
            counter += 1

    def _unique_mesh_name(self, name, mesh=None):
        counter = 0

        for i, c in enumerate(name):
            if ((c < '1' or c > '9') and
                    (c < 'A' or c > 'Z') and
                    (c < 'a' or c > 'z')):
                name = name[:i] + '_' + name[i+1:]

        names = set([m.name for m in
            self.__stl_model.elements_of(StlMesh)
            if m != mesh])

        while True:
            new_name = name
            if counter > 0:
                new_name += '_%i'%counter
            if new_name not in names:
                return new_name
            counter += 1

    def _action_import(self, source, app = None):
        source = source.format(workflow_dir = self.workflow_dir)
        file_name = os.path.splitext(os.path.basename(source))[0]
        if not os.path.exists(self.run_path('files')):
            os.makedirs(self.run_path('files'))

        new_name = self._unique_name(
            self.run_path('files'), file_name + '.stl')
        path = self.run_path('files', new_name + '.stl')

        modified = os.stat(source).st_mtime
        file = self.__add_file(new_name, source, modified, app)
        with open(path, 'wb') as f:
            for m in stl.mesh.Mesh.from_multi_file(source):
                if m.name: 
                    mesh_name = m.name.decode('ascii', errors='ignore')
                else:
                    mesh_name = 'Mesh'
                mesh_name = self._unique_mesh_name(mesh_name)
                mesh = self.__add_mesh(file, m, mesh_name)
                # m.save(mesh_name.encode('ascii'), f, mode = stl.stl.ASCII)
                m.save(mesh_name, f, mode=stl.stl.ASCII)
        file.loading = False
        self.config['stl'].append((file.name, file.source, file.modified, file.app))
        self.update_output()
        self.config.write()

        if list(self.__stl_model.elements_of(StlFile)):
            self.set_progress(-1)
        else:
            self.set_progress(0)

    def _action_delete_file(self, file):
        file = self.__find_file(file)
        file.invalidate()
        self.__stl_model.root_elements.remove(file)
        for m in file.elements:
            self.vis_remove_object(m.vtk_obj)
        
        for i, v in enumerate(self.config['stl']):
            if v[0] == file.name:
                del self.config['stl'][i]
                break

        if os.path.exists(self.run_path('files', file.name + '.stl')):
            os.remove(self.run_path('files', file.name + '.stl'))
        self.update_output()
        self.config.write()

    def _action_delete_mesh(self, file, mesh):
        path = self.run_path('files', file + '.stl')
        file = self.__find_file(file)
        mesh = self.__find_mesh(file, mesh)
        mesh.invalidate()
        self.vis_remove_object(mesh.vtk_obj)
        file.elements.remove(mesh)
        with open(path, 'wb') as f:
            for m in file.elements:
                m.mesh.save(m.mesh.name, f, mode = stl.stl.ASCII)
        self.update_output()

    def _action_merge_files(self, source_files, dest_file):
        dest = self.__find_file(dest_file)
        dest_path = self.run_path('files', dest_file + '.stl')
        for name in source_files:
            source = self.__find_file(name)
            moved = source.elements[:]
            self.__stl_model.data.move(source, 0, len(source.elements),
                dest, len(dest.elements))
            for m in moved:
                m.name = self._unique_mesh_name(m.name, m)
                m.file = dest
                with open(dest_path, 'ab') as f:
                    m.mesh.save(m.mesh.name, f, mode = stl.stl.ASCII)
                m.update()
            self._action_delete_file(name)
        self.update_output()

    def _action_move_meshes(self, sources, dest_file):
        dest = self.__find_file(dest_file)
        dest_path = self.run_path('files', dest_file + '.stl')
        for name, meshes in sources.items():
            source = self.__find_file(name)
            
            for mesh_name in meshes:
                for m in source.elements:
                    if m.name == mesh_name:
                        m.name = self._unique_mesh_name(m.name, m)
                        self.__stl_model.data.move(source, source.elements.index(m),
                            1, dest, len(dest.elements))
                        m.file = dest
                        m.update()
                        with open(dest_path, 'ab') as f:
                            m.mesh.save(m.mesh.name, f, mode = stl.stl.ASCII)
                        break

            source_path = self.run_path('files', name + '.stl')
            with open(source_path, 'wb') as f:
                for m in source.elements:
                    m.mesh.save(m.mesh.name, f, mode = stl.stl.ASCII)

        self.update_output()

    def _action_rename_file(self, file, name):
        file = self.__find_file(file)
        path = self.run_path('files')
        new_name = self._unique_name(path, name + '.stl')
        from_path = os.path.join(path, file.name + '.stl')
        to_path = os.path.join(path, new_name + '.stl')
        os.rename(from_path, to_path)
        for i, v in enumerate(self.config['stl']):
            if v[0] == file.name:
                self.config['stl'][i] = (new_name,) +tuple(v[1:])
                break

        self.update_output()
        file.name = new_name
        self.config.write() 

    def _action_rename_mesh(self, file, mesh, name):
        file = self.__find_file(file)
        mesh = self.__find_mesh(file, mesh)
        path = self.run_path('files', file.name + '.stl')
        mesh.name = self._unique_mesh_name(name, mesh)
        with open(path, 'wb') as f:
            for m in file.elements:
                m.mesh.save(m.mesh.name, f, mode = stl.stl.ASCII)
        self.update_output()

    def _action_split_file(self, file):
        file = self.__find_file(file)
        name = file.name
        path = self.run_path('files')
        for m in file.elements[:]:
            new_name = self._unique_name(path, '%s_%s'%(name, m.name) + '.stl')
            new_path = os.path.join(path, new_name + '.stl')

            with open(new_path, 'wb') as f:
                m.mesh.save(m.mesh.name, f, mode = stl.stl.ASCII)

            model_item = StlFile(self, new_name, file.source, file.modified, file.app)
            self.config['stl'].append((new_name, file.source, file.modified, file.app))
            model_item.loading = False
            self.__stl_model.root_elements.append(model_item)
            m.file = model_item
            self.__stl_model.data.move(file, file.elements.index(m),
                            1, model_item, 0)
            self.update_output()

        self._action_delete_file(file.name)
        self.config.write()

    def __find_file(self, file):
        for v in self.__stl_model.elements_of(StlFile):
            if v.name == file:
                return v

    def __find_mesh(self, file, mesh):
        for m in file.elements:
            if m.name == mesh:
                return m

    '''
    QML Interface
    ===========================================================================
    '''

    @diceProperty('QVariant', name="historyModel")
    def history_model(self):
        return self.__history_model

    @history_model.setter
    def history_model(self, model):
        if self.__history_model != model:
            self.__history_model = model

    @diceProperty('QVariant')
    def stl_model(self):
        return self.__stl_model

    @stl_model.setter
    def stl_model(self, model):
        if self.__stl_model != model:
            self.__stl_model = model

    @diceSlot("QString", name="addSTL")
    def import_stl(self, files):
        if not isinstance(files, (list, tuple)):
            files = (files,)

        wf = self.workflow_path()
        for fn in files:
            fn = FileOperations.parse_url(fn)
            pre = os.path.commonprefix((fn, wf))
            if pre:
                fn = os.path.join('{workflow_dir}',
                    os.path.relpath(fn, wf))

            action = dict(cmd = 'import',
                    params = dict(source = fn))
            
            self.__apply_action(action)

    def build_output(self, name):
        if not os.path.exists(self.run_path('files')):
            os.makedirs(self.run_path('files'))
        path = self.config_path('files', name + '.stl')
        output = self.run_path('files', name + '.stl')
        shutil.copyfile(path, output)
        self.update_output()

    def clear_output(self, name):
        output = self.run_path('files', name + '.stl')
        if os.path.exists(output):
            os.remove(output)
        self.update_output()

    def rename_output(self, name, new_name):
        from_path = self.run_path('files', name + '.stl')
        to_path = self.run_path('files', new_name + '.stl') 
        os.rename(from_path, to_path)
        self.update_output()

    def update_output(self):
        path = self.run_path('files')
        output = []
        for name in os.listdir(path):
            output.append(
                os.path.join(
                    self.run_path('files', relative=True), name))
        print('stl_files ->>', output)
        self.set_output('stl_files', output)

    # items commands

    def delete_file(self, file):
        action = dict(cmd = 'delete_file',
            params = dict(file = file.name))
        self.__apply_action(action)

    def delete_mesh(self, mesh):
        if len(mesh.file.elements) == 1:
            action = dict(cmd = 'delete_file',
                params = dict(file = mesh.file.name))
            self.__apply_action(action)
        else:
            action = dict(cmd = 'delete_mesh',
                params = dict(file = mesh.file.name,
                    mesh = mesh.name))
            self.__apply_action(action)

    def file_rename(self, file, name):
        action = dict(cmd = 'rename_file',
            params = dict(file = file.name,
                name = name))
        self.__apply_action(action)

    def mesh_rename(self, mesh, name):
        action = dict(cmd = 'rename_mesh',
            params = dict(file = mesh.file.name,
                mesh = mesh.name, name = name))
        self.__apply_action(action)

    def merge_files(self, file, items_ids):
        items_ids = set(items_ids)
        sources = [v.name for v in self.__stl_model.elements_of(StlFile)
            if v.is_valid and v.item_id in items_ids and v != file]
        action = dict(cmd = 'merge_files',
            params = dict(source_files = sources,
                dest_file = file.name))
        self.__apply_action(action)

    def move_meshes(self, file, items_ids):
        items_ids = set(items_ids)
        sources = {}
        for v in self.__stl_model.elements_of(StlMesh):
            if v.file != file and v.is_valid and v.item_id in items_ids:
                sources.setdefault(v.file.name, []).append(v.name)
        action = dict(cmd = 'move_meshes',
            params = dict(sources = sources,
                dest_file = file.name))
        self.__apply_action(action)

    def split_file(self, file):
        action = dict(cmd = 'split_file',
            params = dict(file = file.name))
        self.__apply_action(action)

    def __add_file(self, stl_name, source, modified, app):
        model_item = StlFile(self, stl_name, source, modified, app)
        self.__stl_model.root_elements.append(model_item)
        return model_item

    def __add_mesh(self, file, m, name):
        color = [random.uniform(0.3, 0.7),
            random.uniform(0.6, 1.0), random.uniform(0.6, 1.0)]
        vtk_stl = VtkNumpySTL(
            data = m.vectors, name=name, color=color)
        mesh = StlMesh(self, file, m, vtk_stl)
        mesh.name = name
        file.elements.append(mesh)
        self.vis_add_object(vtk_stl)
        return mesh

    def app_config_signal_name(self, *path):
        return "config.json"

    def get_app_config(self, path):
        var_path = path.split(" ")
        try:
            return self.get_value_by_path(self.config, var_path)
        except KeyError:
            return None

    def set_app_config(self, path, value):
        var_path = path.split(" ")
        dict_var = self.get_dict_by_path(self.config, var_path)
        dict_var[var_path[-1]] = value
        self.config.write()
        self.signal(self.app_config_signal_name())

    # Mass properties
    # ===============
    @diceSlot(name="getMassProperties")
    def get_mass_properties(self):
        mass_properties = \
            self.stl_model.current_item.mesh.get_mass_properties()
        self.__volume = mass_properties[0]
        self.__cog = mass_properties[1].tolist()
        self.__intertia_matrix = mass_properties[2].tolist()
        self.mass_property_changed()

    mass_property_changed = diceSignal(name="massPropertyChanged")

    @diceProperty('QVariant', name="selectedGeometryVolume",
                          notify=mass_property_changed)
    def selected_geometry_volume(self):
        return self.__volume

    @diceProperty('QVariant', name='selectedGeometryCOG', \
                               notify=mass_property_changed)
    def selected_geometry_cog(self):
        return self.__cog

    @diceProperty('QVariant', name='selectedGeometryIntertiaMatrix',
                               notify=mass_property_changed)
    def selected_geometry_intertia_matrix(self):
        return self.__intertia_matrix

    '''
    Main application control functions
    ==================================
    '''

    @diceTask('run')
    def dummy_run(self):
        return True