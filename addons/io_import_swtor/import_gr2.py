# heavily based on http://wiki.xentax.com/index.php/SWTOR:_.gr2_3D_model_file

import bpy
import bmesh
import math
import os
from mathutils import Matrix, Vector
from .utils import read_byte, read_bytes, read_u16, read_u32, read_i32, read_f16, read_f32, find_parent_dir


def read_offset_string(fp, offset):
    prev_offset = fp.tell()
    fp.seek(offset)
    string = ""
    cur_byte = read_byte(fp.read)
    while cur_byte != 0:
        string += chr(cur_byte)
        cur_byte = read_byte(fp.read)
    fp.seek(prev_offset)
    return string


class GR2Vertex():
    def __init__(self, fp, offset, size):
        r = fp.read

        fp.seek(offset)

        self.x = read_f32(r)
        self.y = read_f32(r)
        self.z = read_f32(r)

        if size == 24:
            self.normal = read_bytes(r, 4)
            self.unknown_bytes = read_bytes(r, 4)
            self.u = read_f16(r)
            self.v = read_f16(r)
        elif size == 32:
            self.weights = read_bytes(r, 4)
            self.bones = read_bytes(r, 4)
            self.normal = read_bytes(r, 4)
            self.unknown_bytes = read_bytes(r, 4)
            self.u = read_f16(r)
            self.v = read_f16(r)

    def __iter__(self):
        return iter([self.x, self.y, self.z])


class GR2Face():
    def __init__(self, fp, offset, size):
        r = fp.read

        fp.seek(offset)

        self.v1 = read_u16(r)
        self.v2 = read_u16(r)
        self.v3 = read_u16(r)

    def __iter__(self):
        return iter([self.v1, self.v2, self.v3])


class GR2MeshPiece():
    def __init__(self, fp, offset):
        r = fp.read

        fp.seek(offset)

        self.start_index = read_u32(r)
        self.num_faces = read_u32(r)
        self.material_id = read_i32(r)
        self.piece_index = read_i32(r)
        fp.read(4*8)  # bounding box


class GR2Mesh():
    def __init__(self, fp, offset):
        r = fp.read

        fp.seek(offset)

        self.offset_name = read_u32(r)
        self.unknown_float = read_f32(r)
        self.num_pieces = read_u16(r)
        self.num_used_bones = read_u16(r)
        self.unknown_u16 = read_u16(r)
        self.vertex_size = read_u16(r)
        self.num_vertices = read_u32(r)
        self.num_indices = read_u32(r)
        self.offset_vertices = read_u32(r)
        self.offset_pieces = read_u32(r)
        self.offset_indices = read_u32(r)
        self.offset_bones = read_u32(r)

        self.name = read_offset_string(fp, self.offset_name)

        self.vertices = []
        for i in range(self.num_vertices):
            self.vertices.append(
                GR2Vertex(fp, self.offset_vertices + i * self.vertex_size, self.vertex_size))

        self.faces = []
        for i in range(self.num_indices // 3):
            self.faces.append(
                GR2Face(fp, self.offset_indices + i * 6, self.vertex_size))

        self.pieces = []
        fp.seek(self.offset_pieces)
        for i in range(self.num_pieces):
            self.pieces.append(GR2MeshPiece(fp, fp.tell()))

    def build(self, mesh_loader, skel_loader=None):
        me = bpy.data.meshes.new(self.name)
        obj = bpy.data.objects.new(self.name, me)
        bpy.context.collection.objects.link(obj)
        obj.matrix_local = Matrix.Rotation(math.pi * 0.5, 4, [1, 0, 0])

        bm = bmesh.new()
        
        for i, v in enumerate(self.vertices):
            vert = bm.verts.new()
            vert.index = i
            vert.co = list(v)
        bm.verts.ensure_lookup_table()

        for p in self.pieces:
            mat = mesh_loader.materials[p.material_id]
            if mat.name not in bpy.data.materials:
                bpy.data.materials.new(name=mat.name).use_nodes = True
            material = bpy.data.materials[mat.name]
            if material not in obj.data.materials.items():
                obj.data.materials.append(material)
            material_index = obj.data.materials.find(mat.name)
            for i in range(p.start_index, p.start_index + p.num_faces):
                f = self.faces[i]
                face = bm.faces.new([bm.verts[v] for v in list(f)])
                face.index = i
                face.material_index = material_index
        bm.faces.ensure_lookup_table()

        if self.vertex_size >= 24:
            uv_layer = bm.loops.layers.uv.new()
            for face in bm.faces:
                for loop in face.loops:
                    v = self.vertices[loop.vert.index]
                    loop[uv_layer].uv = Vector([v.u, 1-v.v])

        bm.to_mesh(me)
        bm.free()

        # TODO figure out how bone weights are stored
        # if self.vertex_size == 32 and skel_loader != None:
        #     for i, v in enumerate(self.vertices):
        #         for j in range(4):
        #             b = skel_loader.bones[v.bones[j]]

        #             if not b.name in obj.vertex_groups:
        #                 obj.vertex_groups.new(name=b.name)
        #                 # print(i)
        #                 # print(" ", v.bones[j])
        #                 # print(" ", v.weights[j])
        #                 # print(" ", b.name)

        #             obj.vertex_groups[b.name].add(
        #                 [i], v.weights[j] / 255, 'ADD')

        #     mod = obj.modifiers.new(name="Armature", type='ARMATURE')
        #     mod.object = skel_loader.armature


class GR2Material():
    def __init__(self, fp, offset):
        self.mesh_filepath = fp.name
        r = fp.read

        fp.seek(offset)

        self.offset_name = read_u32(r)

        self.name = read_offset_string(fp, self.offset_name)

        self.textures = {}

    def parse(self):
        art_dir = find_parent_dir(self.mesh_filepath, "art")
        materials_dir = os.path.join(art_dir, "shaders", "materials")
        material_path = os.path.join(materials_dir, f"{self.name}.mat")
        if self.name == "default":
            mesh_filename = os.path.split(self.mesh_filepath)[1][:-4]
            material_path = os.path.join(
                materials_dir, f"{mesh_filename}.mat")
            if not os.path.exists(material_path):
                print("Couldn't find file:", material_path)
                material_path = os.path.join(
                    materials_dir, f"{mesh_filename}_v01.mat")
        if not os.path.exists(material_path):
            print("Couldn't find file:", material_path)
            return

        from xml.etree import ElementTree
        tree = ElementTree.parse(material_path)
        for child in tree.getroot():
            if not child.tag == "input":
                continue
            if not child.findtext("type") == "texture":
                continue
            semantic = child.findtext("semantic")
            value = child.findtext("value")

            self.textures[semantic] = value

    def build(self, import_textures):
        if self.name in bpy.data.materials:
            return

        material = bpy.data.materials.new(name=self.name)
        material.use_nodes = True
        p_bsdf = material.node_tree.nodes["Principled BSDF"]
        p_bsdf.inputs[5].default_value = 0.0

        if import_textures and "DiffuseMap" in self.textures:
            resources_dir = find_parent_dir(
                self.mesh_filepath, "resources")

            tex_node = material.node_tree.nodes.new(
                'ShaderNodeTexImage')
            tex_node.image = bpy.data.images.load(
                os.path.join(resources_dir, f"{self.textures['DiffuseMap']}.dds"))
            material.node_tree.links.new(
                p_bsdf.inputs['Base Color'], tex_node.outputs['Color'])


class GR2Attachment():
    def __init__(self, fp, offset):
        r = fp.read

        fp.seek(offset)

        self.offset_attach_name = read_u32(r)
        self.offset_bone_name = read_u32(r)
        self.matrix = [read_f32(r) for j in range(16)]

        self.attach_name = read_offset_string(fp, self.offset_attach_name)
        self.bone_name = read_offset_string(fp, self.offset_bone_name)


class GR2Bone():
    def __init__(self, fp, offset):
        r = fp.read

        fp.seek(offset)

        self.offset_name = read_u32(r)
        self.parent_index = read_i32(r)
        self.unknown_floats = [read_f32(r) for j in range(32)]

        self.name = read_offset_string(fp, self.offset_name)


class GR2Loader():
    def __init__(self, filepath):
        self.filepath = filepath

    def parse(self):
        with open(self.filepath, 'rb') as fp:
            r = fp.read

            self.header = bytes(read_bytes(r, 4))
            self.major_version = read_u32(r)
            self.minor_version = read_u32(r)
            self.offset_bnry = read_u32(r)

            fp.seek(0x10)

            self.num_cached_offsets = read_u32(r)
            self.gr2_file_type = read_u32(r)
            self.num_meshes = read_u16(r)
            self.num_materials = read_u16(r)
            self.num_bones = read_u16(r)
            self.num_attachs = read_u16(r)

            fp.seek(0x50)

            self.offset_cached_offsets = read_u32(r)
            self.offset_mesh_header = read_u32(r)
            self.offset_material_name_offsets = read_u32(r)
            self.offset_bone_structure = read_u32(r)
            self.offset_attachments = read_u32(r)

            self.meshes = []
            for i in range(self.num_meshes):
                self.meshes.append(
                    GR2Mesh(fp, self.offset_mesh_header + i * 0x28))

            self.materials = []
            fp.seek(self.offset_material_name_offsets)
            for i in range(self.num_materials):
                self.materials.append(GR2Material(fp, fp.tell()))

            self.attachments = []
            fp.seek(self.offset_attachments)
            for i in range(self.num_attachs):
                self.attachments.append(GR2Attachment(fp, fp.tell()))

            self.bones = []
            for i in range(self.num_bones):
                self.bones.append(
                    GR2Bone(fp, self.offset_bone_structure + i * 0x88))

    def build(self, skel_loader=None, import_collision=False):
        for m in self.meshes:
            if "collision" in m.name and not import_collision:
                continue
            m.build(self, skel_loader)

        if len(self.bones) > 0:
            bpy.ops.object.add(type='ARMATURE', enter_editmode=True)
            armature = bpy.context.object.data
            armature.name = os.path.splitext(
                os.path.split(self.filepath)[1])[0]

            for b in self.bones:
                bone = armature.edit_bones.new(b.name)
                bone.tail = [0, 0.01, 0]

            for i, b in enumerate(self.bones):
                bone = armature.edit_bones[i]
                if b.parent_index >= 0:
                    bone.parent = armature.edit_bones[b.parent_index]

            for i, b in enumerate(self.bones):
                bone = armature.edit_bones[i]

                # if b.parent_index >= 0:
                #     matrix = Matrix(
                #         [self.bones[b.parent_index].unknown_floats[j*4:j*4+4]for j in range(4)])
                #     matrix.transpose()
                #     bone.transform(matrix)

                matrix = Matrix([b.unknown_floats[j*4+16:j*4+4+16]
                                 for j in range(4)])
                matrix.transpose()
                bone.transform(matrix.inverted())

            bpy.context.object.name = armature.name
            bpy.context.object.matrix_local = Matrix.Rotation(
                math.pi * 0.5, 4, [1, 0, 0])
            bpy.ops.object.mode_set(mode='OBJECT')

            # for easy access when skinning
            self.armature = bpy.context.object


def convert_dict(o):
    if "__dict__" in dir(o):
        return o.__dict__
    elif isinstance(o, bytes):
        return o.decode()
    else:
        raise TypeError()


def load(operator, context, filepath=""):
    skel_loader = None
    if operator.import_skeleton and "dynamic" in filepath:
        # get the dynamic dir path
        dynamic_dir, mesh_filename = os.path.split(filepath)
        while not dynamic_dir.endswith("dynamic"):
            dynamic_dir = os.path.split(dynamic_dir)[0]

        # go to spec and find matching skeleton
        spec_dir = os.path.join(dynamic_dir, "spec")
        skel_name = mesh_filename.split('_')[0]
        skel_filename = f"{skel_name}_skeleton.gr2"
        skel_filepath = os.path.join(spec_dir, skel_filename)

        # load the skeleton as armature
        skel_loader = GR2Loader(skel_filepath)
        skel_loader.parse()
        print(skel_loader.num_bones)
        skel_loader.build()

    main_loader = GR2Loader(filepath)
    main_loader.parse()
    if operator.import_materials:
        for mat in main_loader.materials:
            print(mat.__dict__)
            mat.parse()
            mat.build(operator.import_textures)
    main_loader.build(skel_loader, operator.import_collision)

    return {'FINISHED'}
