import os.path
import re
import sys

import bpy


def rename(bvh_path, out_path):
    bones_map = {
        'Root': 'root',
        'Hips': 'root',
        'Spine': 'spine_01',
        'Spine1': 'spine_02',
        'Spine2': 'spine_03',
        'LeftShoulder': 'clavicle_l',
        'LeftArm': 'upperarm_l',
        'LeftForeArm': 'lowerarm_l',
        'LeftHand': 'hand_l',
        'RightShoulder': 'clavicle_r',
        'RightArm': 'upperarm_r',
        'RightForeArm': 'lowerarm_r',
        'RightHand': 'hand_r',
        'Neck1': 'neck_01',
        'Neck': 'neck_01',
        'Head': 'head',
        'LeftUpLeg': 'thigh_l',
        'LeftLeg': 'calf_l',
        'LeftFoot': 'foot_l',
        'RightUpLeg': 'thigh_r',
        'RightLeg': 'calf_r',
        'RightFoot': 'foot_r',
        'LeftHandIndex1': 'index_01_l',
        'LeftHandIndex2': 'index_02_l',
        'LeftHandIndex3': 'index_03_l',
        'LeftHandMiddle1': 'middle_01_l',
        'LeftHandMiddle2': 'middle_02_l',
        'LeftHandMiddle3': 'middle_03_l',
        'LeftHandPinky1': 'pinky_01_l',
        'LeftHandPinky2': 'pinky_02_l',
        'LeftHandPinky3': 'pinky_03_l',
        'LeftHandRing1': 'ring_01_l',
        'LeftHandRing2': 'ring_02_l',
        'LeftHandRing3': 'ring_03_l',
        'LeftHandThumb1': 'thumb_01_l',
        'LeftHandThumb2': 'thumb_02_l',
        'LeftHandThumb3': 'thumb_03_l',
        'RightHandIndex1': 'index_01_r',
        'RightHandIndex2': 'index_02_r',
        'RightHandIndex3': 'index_03_r',
        'RightHandMiddle1': 'middle_01_r',
        'RightHandMiddle2': 'middle_02_r',
        'RightHandMiddle3': 'middle_03_r',
        'RightHandPinky1': 'pinky_01_r',
        'RightHandPinky2': 'pinky_02_r',
        'RightHandPinky3': 'pinky_03_r',
        'RightHandRing1': 'ring_01_r',
        'RightHandRing2': 'ring_02_r',
        'RightHandRing3': 'ring_03_r',
        'RightHandThumb1': 'thumb_01_r',
        'RightHandThumb2': 'thumb_02_r',
        'RightHandThumb3': 'thumb_03_r',
        'LeftToeBase': 'ball_l',
        'RightToeBase': 'ball_r'
    }

    source_file = open(bvh_path)

    fh = source_file.read()
    for i, (k, v) in enumerate(bones_map.items()):
        # note: if there are ':' in the bone names, this regex breaks
        # but if we add the ':', it breaks with the captures from motive
        source = "JOINT " + "[A-Z]*[a-z]*" + k + "\n"
        dst = "JOINT " + v + "\n"
        res = re.sub(source, dst, fh, 1)
        if res != fh:
            print("Renaming bone " + k + " to " + v)
        else:
            source = "ROOT " + "[A-Z]*[a-z]*" + k + "\n"
            dst = "ROOT " + v + "\n"
            res = re.sub(source, dst, fh, 1)
            if res != fh:
                print("Renaming root " + k + " to " + v)
        fh = res

    with open(out_path, "w") as file:
        file.write(fh)


argv = sys.argv
argv = argv[argv.index("--") + 1:]
bvh_in = argv[0]
fbx_out = argv[1]

# TO RUN:
# <blender.exe-path> -b --python motive-ue5-bridge.py -- <path-to-source-bvh> <path-to-dest-fbx>
bvh_renamed = os.path.dirname(bvh_in) + "\\renamed_cache.bvh"

rename(bvh_in, bvh_renamed)

print("\nImporting renamed .bvh")
bpy.ops.import_anim.bvh(filepath = bvh_renamed, filter_glob = "*.bvh", global_scale = 1, frame_start = 1,
                        use_fps_scale = False, use_cyclic = False, rotate_mode = 'NATIVE',
                        axis_forward = '-Z', axis_up = 'Y')

print("Creating pelvis and adjusting root\n")
bpy.ops.object.mode_set(mode = 'EDIT', toggle = False)
obArm = bpy.context.active_object
pelvis_bone_edit = obArm.data.edit_bones
pelvis_bone_edit = pelvis_bone_edit.new("pelvis")
pelvis_bone_edit.head = (0, 0, 0)
pelvis_bone_edit.tail = (0, 0, 3)

root_bone_edit = obArm.data.edit_bones["root"]
pelvis_bone_edit.parent = root_bone_edit

spine_bone_edit = obArm.data.edit_bones["spine_01"]
tigh_l_bone_edit = obArm.data.edit_bones["thigh_l"]
tigh_r_bone_edit = obArm.data.edit_bones["thigh_r"]

spine_bone_edit.parent = pelvis_bone_edit
tigh_l_bone_edit.parent = pelvis_bone_edit
tigh_r_bone_edit.parent = pelvis_bone_edit

bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)

root_bone = obArm.pose.bones["root"]
pelvis_bone = obArm.pose.bones["pelvis"]
pelvis_bone.location = (0, 0, 0)

# action = bpy.data.actions[0]
# scene = bpy.context.scene
# scene.frame_end = len(action.fcurves[0].keyframe_points)
#
# x_c = next(x for x in action.groups if x.name == "root")
#
# for frame in range(scene.frame_end):
#     scene.frame_current = frame
#     x_c.channels[1].keyframe_points[frame].co[1] -= 91.349998
#     # root_loc = (x_c.channels[0].keyframe_points[frame].co[1], x_c.channels[1].keyframe_points[frame].co[1], x_c.channels[2].keyframe_points[frame].co[1])
#     # root_rot = (x_c.channels[3].keyframe_points[frame].co[1], x_c.channels[4].keyframe_points[frame].co[1], x_c.channels[5].keyframe_points[frame].co[1])
#     # root_rot = [i * 57.2958 for i in root_rot]
#     # print(str(frame) + ":" + str(root_rot))
#     # pelvis_bone.location = root_loc
#     # pelvis_bone.location[1] -= 91.349998
#     # pelvis_bone.rotation_euler = root_rot
#     # # print(root_bone.location)
#     # pelvis_bone.keyframe_insert("location")
#     # pelvis_bone.keyframe_insert("rotation_euler")

print("\nExporting .fbx")
bpy.ops.export_scene.fbx(filepath = fbx_out, axis_forward = 'X', axis_up = 'Z', use_selection = True, bake_anim = True)
print("\nExported to :" + fbx_out)

os.remove(bvh_renamed)
