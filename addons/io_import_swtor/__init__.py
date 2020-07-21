import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
    StringProperty,
    CollectionProperty,
)
from bpy_extras.io_utils import (
    ImportHelper,
    ExportHelper,
)


bl_info = {
    "name": "SWTOR GR2 Format",
    "author": "Henrik Melsom",
    "version": (0, 2, 0),
    "blender": (2, 83, 0),
    "location": "File > Import",
    "description": "Import GR2 meshes",
    "warning": "",
    "doc_url": "https://github.com/GarmOfGnipahellir/blender-swtor-importer",
    "support": 'COMMUNITY',
    "category": "Import-Export",
}


class ImportGR2(bpy.types.Operator, ImportHelper):
    """Load a GR2 file"""
    bl_idname = "import_scene.gr2"
    bl_label = "Import SWTOR"
    bl_options = {'UNDO'}

    filename_ext = ".gr2"
    filter_glob: StringProperty(default="*.gr2", options={'HIDDEN'})

    import_collision: BoolProperty(
        name="Import Collision", default=False)

    import_skeleton: BoolProperty(
        name="Import Skeleton (Experimental)", default=False)

    import_materials: BoolProperty(
        name="Import Materials (Experimental)", default=False)

    import_textures: BoolProperty(
        name="Import Textures (Experimental)", default=False)

    def execute(self, context):
        from . import import_gr2
        return import_gr2.load(self, context, self.filepath)


def menu_func_import(self, context):
    self.layout.operator(ImportGR2.bl_idname, text="SWTOR Mesh (.gr2)")


def register():
    bpy.utils.register_class(ImportGR2)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportGR2)

    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()
