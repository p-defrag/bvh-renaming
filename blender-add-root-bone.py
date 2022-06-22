import sys
import bpy

argv = sys.argv
argv = argv[argv.index("--") + 1:]  # get all args after "—"
bvh_in = argv[0]
fbx_out = argv[1]

# imports the .bvh, adds root, then export the file as .fbx

# TO RUN:
# <blender.exe-path> -b --python blender-api-conversion.py -- <path-to-source-bvh> <path-to-dest-fbx>

bpy.ops.import_anim.bvh(filepath = bvh_in, filter_glob = "*.bvh", global_scale = 1, frame_start = 1,
                        use_fps_scale = False, use_cyclic = False, rotate_mode = 'NATIVE',
                        axis_forward = '-Z',axis_up = 'Y')

bpy.ops.object.mode_set(mode='EDIT', toggle=False)
obArm = bpy.context.active_object #get the armature object
pelvis_bone_edit = obArm.data.edit_bones
pelvis_bone_edit = pelvis_bone_edit.new("pelvis")
pelvis_bone_edit.head = (0, 0, 0) # if the head and tail are the same, the bone is deleted
pelvis_bone_edit.tail = (0, 0, 3)    # upon returning to object mode

root_bone_edit = obArm.data.edit_bones["root"]
pelvis_bone_edit.parent = root_bone_edit

spine_bone_edit = obArm.data.edit_bones["spine_01"]
tigh_l_bone_edit = obArm.data.edit_bones["thigh_l"]
tigh_r_bone_edit = obArm.data.edit_bones["thigh_r"]

spine_bone_edit.parent = pelvis_bone_edit
tigh_l_bone_edit.parent = pelvis_bone_edit
tigh_r_bone_edit.parent = pelvis_bone_edit

root_bone_edit.head[2] = -110

bpy.ops.object.mode_set(mode='OBJECT', toggle=False)


bpy.ops.export_scene.fbx(filepath = fbx_out,
                         axis_forward = '-Z', axis_up = 'Y',
                         use_selection = True, bake_anim = True)