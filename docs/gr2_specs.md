ripped from http://wiki.xentax.com/index.php/SWTOR:_.gr2_3D_model_file

This article contains a file format specification for the custom .gr2 file format used by the MMORPG ''Star Wars: The Old Republic'' to store the 3D models of the game.

==General information==
All model files can be found in the .tor archives <tt>swtor_main_art_*_1.tor</tt> and they are placed in the folder <tt>/resources/art/</tt>.

There are different kinds of model files:
*'''Dynamic''' files are files that have an animation. They consist of creatures, NPCs, body parts as well as helmets, belts and other clothes.
*'''FX''' (effects) files are used for animations, abilities like detonations or computer screens. 
*'''Static''' files are inanimate models. These include weapons, vehicles, buildings, furniture and small items. Static items are grouped by planet and can be divided into:
**'''Arch''' models are big models like models that are used to create the game world.
**'''Item''' models are smaller models. These can include streetlights, tables, benches, drinking cups, etc.
**'''Speedtree''' models are trees or bushes. Only in a few cases (like branches or dead trees) are .gr2 files used; otherwise, .spt Speedtree files are used to describe the trees.

Each .gr2 file that has textures also references one or more Material files (these .mat files can all be found in <tt>/resources/art/shaders/materials/</tt>). The material files in turn contain the path of the diffuse and normal textures.

==Notes on implementation==
A good file reader should not read the whole file from top to bottom. Instead, it should just read the lengths and offsets in the header and initialize the arrays accordingly. Then, it should seek directly to the positions given in the offsets, and read the file in there.

==File layout==
===Header===
''position:'' 0x00
*<tt>byte[4]</tt>: file identifier, always GAWB (<tt>47 41 57 42</tt>), which stands for <tt>GAWB</tt> = <tt>BWAG</tt> = ''BioWare Austin Geometry''
*<tt>uint32</tt>: major version, always 4
*<tt>uint32</tt>: minor version, always 3
*<tt>uint32 '''offsetBNRY'''</tt>: offset of the <u>BNRY / LTLE section</u>

''position:'' 0x10
*<tt>uint32 '''numCachedOffsets'''</tt>: The number of offsets in the <u>Cached offsets section</u>
*<tt>uint32</tt>: type of .gr2 file:
**<tt>00</tt> = default .gr2 file
**<tt>01</tt> = model has a .clo file. The .clo file has the same path as the .gr2 file, but ends with .clo instead of .gr2
**<tt>02</tt> = this is a skeleton file (see ''/resources/art/dynamic/spec/'')
*<tt>uint16 '''numMeshes'''</tt>: The number of meshes that the model is made up of
*<tt>uint16 '''numMaterials'''</tt>: The number of materials referenced by all meshes of the model
*<tt>uint16 '''numBones'''</tt>: if it is a skeleton files, read the number of skeleton bones here
*<tt>uint16 '''numAttachs'''</tt>: The number of objects that are attached to bones
*<tt>byte[16]</tt>: 16 zero bytes

''position:'' 0x30
*<tt>BoundingBox</tt>: The global bounding box, the whole model is contained inside it

''position:'' 0x50
*<tt>uint32 '''offsetCachedOffsets'''</tt>: Offset of the <u>Cached offsets section</u>
*<tt>uint32 '''offsetMeshHeader'''</tt>: Offset of the <u>Mesh information</u> section, usually 0x70, or zero, if there are no meshes.
*<tt>uint32 '''offsetMaterialNameOffsets'''</tt>: Offset of the <u>Material offsets</u> section where the offsets of the material names are given, or zero if there are no materials.
*<tt>uint32 '''offsetBoneStructure'''</tt>: Offset of the <u>Skeleton structure</u> section (usually 0x70), only when this file is a skeleton file, otherwise zero
*<tt>uint32 '''offsetAttachments'''</tt>: Offset of the <u>Attached objects</u> section, or zero, if there are not attached objects.
*''(zero padding bytes to next 16-byte block)''

===Skeleton structure===
This section is only contained if the file is a skeleton file (the number of bones is given in numBones). Each bone takes up 0x88 = 136 bytes.

''position:'' <tt>'''offsetBoneStructure'''</tt> = 0x70

*LOOP (FOR EACH <tt>'''bone'''</tt> IN <tt>'''numBones'''</tt>) {
**<tt>uint32 '''offsetBoneName'''</tt>: The offset of the bone name, stored as string and terminated by a <tt>00</tt> byte
**<tt>int32 '''parentBoneIndex'''</tt>: The index of the parent bone, or -1 if it is the root. Indices start at zero.
**<tt>float32[16]</tt>: 16 unknown floats, possibly a matrix with bone transform in local space
**<tt>float32[16]</tt>: not sure, but seems to be a matrix with bone transform in world/object space
*} END LOOP
*''(zero padding bytes to next 16-byte block)''

===Mesh information===
The mesh headers contain information on each mesh (the number of meshes is given in numMeshes). Each mesh takes up 0x28 = 40 bytes.

''position:'' <tt>'''offsetMeshHeader'''</tt> = 0x70

*LOOP (FOR EACH <tt>'''mesh'''</tt> IN <tt>'''numMeshes'''</tt>) {
**<tt>uint32 '''offsetMeshName'''</tt>: The offset of the mesh name, stored as string and terminated by a <tt>00</tt> byte
**<tt>float32</tt>: unknown
**<tt>uint16 '''numPieces'''</tt>: The number of pieces this mesh is made up, equal to the number of materials used by this mesh <small>(required for reading <u>mesh piece information</u> section)</small>
**<tt>uint16 '''numUsedBones'''</tt>: The number of bones from the whole skeleton that are connected to this mesh
**<tt>uint16</tt>: unknown, seems to be related to bones
**<tt>uint16 '''vertexSize'''</tt>: The number of bytes used for storing a vertex (required for reading vertex section)
***12 = just the X/Y/Z coordinates of this vertex (e.g. for collision meshes)
***24 = X/Y/Z coordinates and texture positions of this vertex (e.g. for static models)
***32 = X/Y/Z coordinates, texture positions and bone connections of this vertex (e.g. for dynamic, animated models)
**<tt>uint32 '''numVertices'''</tt>: The total number of vertices used by this mesh <small>(not required for reading model since this information is also given in <u>mesh piece information</u>)</small>
**<tt>uint32 '''numIndices'''</tt>: The total number of vertex indices used by this mesh. Divide this number by 3 to get number of faces <small>(not required for reading model since this information is also given in <u>mesh piece information</u>)</small>
**<tt>uint32 '''offsetMeshVertices'''</tt>: The start address (offset) of the <u>vertices</u> of this mesh <small>(required for reading vertices)</small>
**<tt>uint32 '''offsetMeshPieces'''</tt>: The start address (offset) of the <u>Mesh piece information</u> of this mesh <small>(required for reading models with textures)</small>
**<tt>uint32 '''offsetIndices'''</tt>: The start address (offset) of the <u>indices</u> of this mesh <small>(required for reading face indices)</small>
**<tt>uint32 '''offsetBones'''</tt>: The start address (offset) of the <u>bone list</u> of this mesh
*} END LOOP

*''(zero padding bytes to next 16-byte block)''

===Mesh piece information===
This section contains information on which faces of the mesh display which material/texture. Keep in mind that the number of faces given here stands for the faces; if you need the number of vertices for your model viewer, you'll have to multiple the values by 3. To get the material names, you also need to read the <u>Material offsets</u> section.

*LOOP (FOR EACH <tt>'''mesh'''</tt> IN <tt>'''numMeshes'''</tt>) {
*''position:'' <tt>'''mesh.offsetMeshPieces'''</tt>
**LOOP (FOR EACH <tt>'''piece'''</tt> IN <tt>'''mesh.numPieces'''</tt>) {
***<tt>uint32</tt>: The starting index where the faces for this piece start, values range from 0 to <tt>'''mesh.numFaces'''/3 - 1</tt>
***<tt>uint32</tt>: The number of faces that this piece is made up of
***<tt>int32</tt>: If this piece is textured, this field specifies the id <small>(related to the <u>Material offsets</u> section)</small> for this material, otherwise -1
***<tt>int32</tt>: This field is just an enumerator/loop index. It starts with 0 for each mesh and increases by 1 for each piece, or is set to -1, if it is not textured
***<tt>BoundingBox</tt>: The bounding box for this mesh piece
**} END LOOP
*} END LOOP

===Material name offsets===
This section contains a list of the offsets to the material names.

*''position:'' <tt>'''offsetMaterialNameOffsets'''</tt>
*LOOP (FOR EACH <tt>'''texture'''</tt> IN <tt>'''numTextures'''</tt>) {
**<tt>uint32 '''offsetMaterialName'''</tt>: The offset where the material name is stored, terminated by a <tt>00</tt> byte
*} END LOOP
*''(zero padding bytes to next 16-byte block)''

===Attached objects===
This section is optional. It contains a list of objects that are attached to certain bones.

*''position:'' <tt>'''offsetAttachments'''</tt>
*LOOP (FOR EACH <tt>'''attachedObject'''</tt> IN <tt>'''numAttachs'''</tt>) {
**<tt>uint32</tt>: offset where the name of the attached object is stored, string of variable length, terminated by a <tt>00</tt> byte
**<tt>uint32</tt>: offset where the name of the bone the object attaches to is stored, string of variable length, terminated by a <tt>00</tt> byte
**<tt>float32[16]</tt>: 16 floats for a 4x4 matrix
*} END LOOP
*''(zero padding bytes to next 16-byte block)''

===Vertices===
Depending on the vertex length (given in numVertexBytes), each vertex takes up 12, 24 and 32 bytes. This section contains not only the x/y/z positions, but also (for textured meshes) the texture u/v coordinates as well as the normals and tangents.

*LOOP (FOR EACH <tt>'''mesh'''</tt> IN <tt>'''numMeshes'''</tt>) {
*''position:'' <tt>'''mesh.offsetVertices'''</tt>
**LOOP (FOR EACH <tt>'''vertex'''</tt> IN <tt>'''mesh.numVertices'''</tt>) {
***IF (<tt>'''mesh.vertexSize'''</tt> == 12) {
****<tt>float32</tt>: a float value specifying the x coordinate of the vertex
****<tt>float32</tt>: a float value specifying the y coordinate of the vertex
****<tt>float32</tt>: a float value specifying the z coordinate of the vertex
***} ELSE IF (<tt>'''mesh.vertexSize'''</tt> == 24) {
****<tt>float32</tt>: a float value specifying the x coordinate of the vertex
****<tt>float32</tt>: a float value specifying the y coordinate of the vertex
****<tt>float32</tt>: a float value specifying the z coordinate of the vertex
****<tt>byte[4]</tt>: normal xyzw (0 to 255) w seems to always be 255
****<tt>byte[4]</tt>: possibly tangents in an unknown encoding
****<tt>float16</tt>: specifying the u coordinate for the texture
****<tt>float16</tt>: specifying the v coordinate for the texture
***} ELSE IF (<tt>'''mesh.vertexSize'''</tt> == 32) {
****<tt>float32</tt>: a float value specifying the x coordinate of the vertex
****<tt>float32</tt>: a float value specifying the y coordinate of the vertex
****<tt>float32</tt>: a float value specifying the z coordinate of the vertex
****<tt>byte</tt>: weight of the first bone joint (0 to 255)
****<tt>byte</tt>: weight of the second bone joint (0 to 255)
****<tt>byte</tt>: weight of the third bone joint (0 to 255)
****<tt>byte</tt>: weight of the fourth bone joint (0 to 255)
****<tt>byte</tt>: index of the first bone joint that influences the vertex's position
****<tt>byte</tt>: index of the second bone joint that influences the vertex's position
****<tt>byte</tt>: index of the third bone joint that influences the vertex's position
****<tt>byte</tt>: index of the fourth bone joint that influences the vertex's position
****<tt>byte[4]</tt>: normal xyzw (0 to 255) w seems to always be 255
****<tt>byte[4]</tt>: possibly tangents in an unknown encoding
****<tt>float16</tt>: specifying the u coordinate for the texture
****<tt>float16</tt>: specifying the v coordinate for the texture
***} END IF
**} END LOOP
*} END LOOP
*''(zero padding bytes to next 16-byte block)''

===Faces===
This section contains the faces, that is the number of surfaces of the model. Three vertices (= three point) generate one face, so for each face you will have to read three integers to get the index for each point.

Note that <tt>'''mesh.numFaces'''</tt> given under <u>Mesh information</u> stands for the number of indices, so you'll have to divide it by 3 if you want to get the number of faces. In the <u>Mesh piece information</u> section howver, <tt>'''mesh.piece.numFaces'''</tt> stands for the number of the faces. To get the number of indices, multiply it by three.

Please note that the vertex indices are zero-based (that is, the first vertex is numbered 0 and not 1). Some programs (for example Wavefront .obj files) start counting the index at 1, so you'll have to increase the indices by one if you are using such a program.

*LOOP (FOR EACH <tt>'''mesh'''</tt> IN <tt>'''numMeshes'''</tt>) {
*''position:'' <tt>'''mesh.offsetFaces'''</tt>
**LOOP (FOR EACH <tt>'''face'''</tt> in <tt>'''mesh.numFaces'''/3</tt>) {
***<tt>uint16</tt>: index of first vertex
***<tt>uint16</tt>: index of second vertex
***<tt>uint16</tt>: index of third vertex
**} END LOOP
**''(zero padding bytes to next 16-byte block)''
*} END LOOP

===Bone list===
If this file is a normal file, not a skeleton file, but is animated (like humans or creatures), the file will contain a list of the bones used by the current model.

*''position:'' <tt>'''offsetBones'''</tt>
*LOOP (FOR EACH <tt>'''bone'''</tt> IN <tt>'''numBones'''</tt>) {
**<tt>uint32</tt>: offset of bone name as string, terminated by <tt>00</tt>
**<tt>float32[6]</tt>: six unknown floats, maybe related to position/rotation of bone
*} END LOOP
*''(zero padding bytes to next 16-byte block)''

===List of strings===
This section contains multiple strings. It is not necessary to try and read this whole section by itself; instead, it is best to just seek here whenever you encounter a string offset.

*LOOP (FOR EACH <tt>string</tt>) {
**''position:'' different for each string
**string of variable length, but always terminated by a <tt>00</tt> byte
**the <tt>00</tt> byte
*} END LOOP
*''(zero padding bytes to next 16-byte block)''

===Cached offsets section===
This section contains a list of offset addresses along with the value that is found at that address. Each of these values is in turn an offset again. The first offset is always <tt>50 00 00 00</tt>, which is the offset of this section.

This section may be important for reading the bones, but right now it appears to be redundant to me.

*''position:'' offsetCachedOffsets
*LOOP (for each tmpOffset in numCachedOffsets) {
**uint32 offsetAddress: An offset in the value
**uint32 offsetValue: The value that is stored at that offset, always another offset
*} END LOOP
**''(zero padding bytes to next 16-byte block)''

===BNRY / LTLE section===
This section is only present if the model contains a collision mesh. To be on the safe side, read the first length field. If it is zero, you can ignore this section, otherwise you can read it.

This section is completely unknown to me. The specification will allow you to parse the BNRY section without errors, but there is not much to do with the data yet, so you can just as well skip this section.

Regarding the BNRY / LTLE acronym, the only meaningful words I could come up with were ''binary / little'' but I am not sure about that.

====BNRY header====
*''position:'' bnryOffset
*uint32 bnryLength: length of the whole BNRY section<s>, excluding these four bytes</s>
*bytes(4): always BNRY (<tt>42 4E 52 59</tt>)
*bytes(4): always <tt>00 00 00 02</tt>
*bytes(4): always LTLE (<tt>4C 54 4C 45</tt>)

----

*''position:'' bnryOffset + 16
*uint32: always <tt>01 00 00 00</tt>
*uint32: always <tt>02 00 00 00</tt>
*uint32 numBNRYsections: number of sections in the BNRY section
*uint32: some unknown offset/length


*uint32 numLongLines: the number of long lines in the BNRY section
*uint32 totalNum21Lines: the total number of lines starting with 0x21/0xA1; this number is the sum of the 0x21 lines from each BNRY section
*uint32: always <tt>01 00 00 00</tt>
*uint32: always <tt>01 00 00 00</tt>


*float32: unknown, x coordinate?
*float32: unknown, y coordinate?
*float32: unknown, z coordinate?
*uint32: always <tt>01 00 00 00</tt>


*float32: unknown, x coordinate?
*float32: unknown, y coordinate?
*float32: unknown, z coordinate?
*uint32: always <tt>00 00 00 00</tt>

----

*''position:'' bnryOffset + 80
*uint32: always <tt>01 00 00 00</tt>
*uint32: always <tt>04 00 00 00</tt>
*uint32: always <tt>01 00 00 00</tt>
*uint32: always <tt>01 00 00 00</tt>


*uint32: unknown
*uint32 totalNum21Lines: the total number of lines starting with 0x21/0xA1; same as above
*uint32: always <tt>01 00 00 00</tt>
*uint32: always <tt>01 00 00 00</tt>


*float32: unknown, x coordinate?
*float32: unknown, y coordinate?
*float32: unknown, z coordinate?
*uint32: always <tt>01 00 00 00</tt>


*float32: unknown, x coordinate?
*float32: unknown, y coordinate?
*float32: unknown, z coordinate?
*uint32: numBNRYsections: number of sections in the BNRY section; same as above

----

*''position:'' bnryOffset + 128
*uint32: numBNRYsections: number of sections in the BNRY section; same as above
*uint32 totalNum21Lines: the total number of lines starting with 0x21/0xA1; same as above
*uint32 totalNum21Lines: the total number of lines starting with 0x21/0xA1; same as above
*uint32: always <tt>00 00 00 00</tt>


*uint32: some unknown offset/length
*uint32: always <tt>10 00 00 00</tt>
*uint16: always <tt>00 00</tt>
*uint16: always <tt>80 00</tt>
*byte: always <tt>01</tt>
*uint32: always <tt>01 00 00 00</tt>


*uint32 numLongLines: the number of long lines in the BNRY section; same as above
*uint32 totalNum21Lines: the total number of lines starting with 0x21/0xA1; same as above
*uint32: always <tt>01 00 00 00</tt>
*uint32: always <tt>01 00 00 00</tt>


*float32: unknown, x coordinate?
*float32: unknown, y coordinate?
*float32: unknown, z coordinate?
*uint32: always <tt>01 00 00 00</tt>


*float32: unknown, x coordinate?
*float32: unknown, y coordinate?
*float32: unknown, z coordinate?
*uint32: always <tt>01 00 00 00</tt>

====long lines====
*''position:'' bnryOffset + 209
*LOOP (for each tmpLongLine in numLongLines) {
**uint32: some id
**uint32: some id or small integer
**uint32: always <tt>01 00 00 00</tt>
**int32: parent id? either <tt>FF FF FF FF</tt> or an id
*uint32: unknown
**int32: parent id? either <tt>FF FF FF FF</tt> or an id
*uint32: unknown
*float32: unknown
*float32: unknown
*} END LOOP

====BNRY sections====
*uint32: always <tt>00 00 00 00</tt>
*uint32: always <tt>01 00 00 00</tt>


*LOOP (for each tmpBNRYsection in numBNRYsections) {
**uint32 tmpBNRYsectionOffset: offset of the BNRY section from the beginning of the following loop
*} END LOOP


*LOOP (for each tmpBNRYsection in numBNRYsections) {
**uint16 curNum21Lines: number of 21/A1 lines in this BNRY section
**uint16 lengthNum21Lines: length of the 21/A1 lines section in this BNRY section
**uint16 numVertexLines: number of vertex lines in the BNRY section
**uint16 numVertexLines: number of vertex lines in the BNRY section; same as above
**uint16: unknown offset/length
**byte: always 00
**uint16 numVertexLines: number of vertex lines in the BNRY section; same as above
----
**uint32: always <tt>01 00 00 00</tt>
**LOOP (for each tmpVertexLine in numVertexLines) {
***float32: x coordinate
***float32: y coordinate
***float32: z coordinate
**} END LOOP
----
**uint32: always <tt>01 00 00 00</tt>
**LOOP (for each tmp21Line in curNum21Lines) {
***byte: either 0x21 or 0xA1
***IF (first byte == 0x21) {
****read 6 more unknown bytes
***} ELSE IF (first byte == 0xA1) {
****read 7 more unknown bytes
***} END IF
**} END LOOP
*} END LOOP
*uint32: often, but not always <tt>01 00 00 00</tt>

====String section====
According to the length of the BNRY section, this section is no longer part of the BNRY section. However, this section is only present in the .gr2 file if the BNRY section exists.

*uint32 numStrings: number of strings in this section
*LOOP (for each tmpString in numStrings) {
**uint32: tmpStringLength: length of this string
**string with given length, terminated by a <tt>00</tt> byte
*} END LOOP

===Unknown mesh floats===
Not yet confirmed, but this section seems to contain the bounding box for each mesh, as opposed to the global bounding box given at the beginning of the value.

*LOOP (for each tmpMesh in numMeshes) {
**float32: The minimum X value of the bounding box of this mesh
**float32: The minimum Y value of the bounding box of this mesh
**float32: The minimum Z value of the bounding box of this mesh
**float32: The maximum X value of the bounding box of this mesh
**float32: The maximum Y value of the bounding box of this mesh
**float32: The maximum Z value of the bounding box of this mesh
*} END LOOP
*byte[4]: four zero bytes

===EGCD section===
*bytes(4): always EGCD (<tt>45 47 43 44</tt>)
*uint32: unknown, sometimes <tt>05 00 00 00</tt>
*uint32: offset of BNRY/LTLE section

[END OF FILE]

==Custom structures==
===BoundingBox===
*float32: The minimum X value of the bounding box of this mesh
*float32: The minimum Y value of the bounding box of this mesh
*float32: The minimum Z value of the bounding box of this mesh
*float32: Always 1.0 (<tt>00 00 80 3F</tt>)
*float32: The maximum X value of the bounding box of this mesh
*float32: The maximum Y value of the bounding box of this mesh
*float32: The maximum Z value of the bounding box of this mesh
*float32: Always 1.0 (<tt>00 00 80 3F</tt>)

[[Category:Model formats]]
[[Category:Platform PC]]
[[Category:Little-endian formats]]
[[Category:Complete Almost Done]]
