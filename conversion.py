import re

bones_map = {
    "Hips": "root",
    "Spine": "spine_01",
    "Spine1": "spine_02",
    "Neck": "neck_01",
    "Head": "head",
    "LeftShoulder": "clavicle_l",
    "LeftArm": "upperarm_l",
    "LeftForeArm": "lowerarm_l",
    "LeftHand": "hand_l",
    "RightShoulder": "clavicle_r",
    "RightArm": "upperarm_r",
    "RightForeArm": "lowerarm_r",
    "RightHand": "hand_r",
    "LeftUpLeg": "thigh_l",
    "LeftLeg": "calf_l",
    "LeftFoot": "foot_l",
    "LeftToeBase": "ball_l",
    "RightUpLeg": "thigh_r",
    "RightLeg": "calf_r",
    "RightFoot": "foot_r",
    "RightToeBase": "ball_r"
}


def rename(bvh_path, out_path):
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
