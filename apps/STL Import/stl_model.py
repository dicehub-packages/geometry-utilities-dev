from dice_tools.helpers.xmodel import modelRole, modelMethod, ModelItem
from dice_tools import wizard


class StlMesh:
    def __init__(self, parent, file, mesh, vtk_obj, **kwargs):
        super().__init__(**kwargs)
        self.__parent = parent
        self.file = file
        self.__mesh = mesh
        self.__vtk_obj = vtk_obj
        self.__selected = False
        self.__highlight = False
        self.__valid = True

        wizard.subscribe(self, self.__vtk_obj)

    @property
    def mesh(self):
        return self.__mesh

    def update(self):
        wizard.w_model_update_item(self)

    @property
    def is_valid(self):
        return self.__valid and self.file.is_valid
    
    def invalidate(self):
        self.__valid = False

    @modelMethod('deleteThis')
    def delete(self):
        if self.__valid:
            self.__parent.delete_mesh(self)

    @property
    def vtk_obj(self):
        return self.__vtk_obj

    def w_property_changed(self, obj, name, value):
        if name == 'visible':
            self.part_visible = value

    def w_geometry_object_clicked(self, obj, *args, **kwargs):
        self.__parent.stl_model.current_item = self

    @modelRole('type')
    def item_type(self):
        return 'mesh'

    @modelRole('name')
    def name(self):
        return self.__mesh.name.decode('ascii', errors='ignore')

    @name.setter
    def name(self, value):
        self.__mesh.name = value.encode('ascii')

    @modelMethod('setName')
    def set_name(self, name):
        if self.__valid and self.name != name:
            self.__parent.mesh_rename(self, name)

    @modelRole('itemHilghlighted')
    def item_hilghlighted(self):
        return self.__highlight

    @item_hilghlighted.setter
    def item_hilghlighted(self, value):
        self.__highlight = value

    @modelRole('isVisible')
    def visible(self):
        return self.__vtk_obj.visible != 0
    
    @visible.setter
    def visible(self, value):
        if (self.__vtk_obj.visible != 0) != value:
            self.__vtk_obj.visible = value

    @modelRole('itemId')
    def item_id(self):
        return id(self)


class StlFile(ModelItem):

    def __init__(self, parent, name, source, modified, app, **kwargs):
        super().__init__(**kwargs)
        self.__parent = parent
        self.__name = name
        self.__source = source
        self.__visible = True
        self.__selection_state = 0
        self.__highlight = False
        self.__is_item_visible = True
        self.__valid = True
        self.__loading = True
        self.app = app
        self.modified = modified

    @modelRole('loading')
    def loading(self):
        return self.__loading

    @loading.setter
    def loading(self, value):
        self.__loading = value
        for m in self.elements:
            m.item_visible = value

    @property
    def is_valid(self):
        return self.__valid

    def invalidate(self):
        self.__valid = False

    @modelRole('canSplit')
    def can_split(self):
        return len(self.elements) > 1

    @modelMethod('splitThis')
    def split(self):
        if self.__valid:
            self.__parent.split_file(self)

    @modelMethod('deleteThis')
    def delete(self):
        if self.__valid:
            self.__parent.delete_file(self)

    @modelRole('name')
    def name(self):
        return self.__name
        
    @name.setter
    def name(self, value):
        self.__name = value

    @modelMethod('setName')
    def set_name(self, name):
        if self.__valid and self.name != name:
            self.__parent.file_rename(self, name)

    @modelRole('type')
    def item_type(self):
        return 'file'

    @modelRole('isVisible')
    def is_visible(self):
        return self.__visible

    @is_visible.setter
    def is_visible(self, value):
        self.__visible = value
        for m in self.elements:
            m.visible = value

    @modelRole('sourceDesc')
    def source(self):
        return self.__source

    @modelRole('itemHilghlighted')
    def item_hilghlighted(self):
        return self.__highlight

    @item_hilghlighted.setter
    def item_hilghlighted(self, value):
        self.__highlight = value

    @modelMethod('mergeFiles')
    def merge_files(self, items_ids):
        if self.__valid:
            self.__parent.merge_files(self, items_ids)

    @modelMethod('moveMeshes')
    def move_meshes(self, items_ids):
        if self.__valid:
            self.__parent.move_meshes(self, items_ids)

    @modelRole('itemId')
    def item_id(self):
        return id(self)
