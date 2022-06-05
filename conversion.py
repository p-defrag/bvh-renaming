import re
import os
from fbx import *
from bvh import Bvh,BvhNode

bones_map = {
    "Hips": "root",
    "Spine": "spine_01",
    "Spine1": "spine_02",
    "Neck": "neck",
    "Head": "head",
    "LeftShoulder": "clavicle_l",
    "LeftArm": "upperarm_l",
    "LeftForeArm": "lowerarm_l",
    "LeftHand": "hand_l",
    "RightShoulder": "clavicle_r",
    "RightArm": "upperarm_r",
    "RightForeArm": "lowerarm_r",
    "RightHand": "hand_r",
    "LeftUpLeg": "tigh_l",
    "LeftLeg": "calf_l",
    "LeftFoot": "foot_l",
    "LeftToeBase": "ball_l",
    "RightUpLeg": "tigh_r",
    "RightLeg": "calf_r",
    "RightFoot": "foot_r",
    "RightToeBase": "ball_r"
}


def rename(bvh_path, out_path):
    source_file = open(bvh_path)

    fh = source_file.read()
    for i, (k, v) in enumerate(bones_map.items()):
        source = "JOINT " + "[A-Z]*[a-z]*:" + k + "\n"
        dst = "JOINT " + v + "\n"
        res = re.sub(source, dst, fh, 1)
        if res != fh:
            print("Renaming bone " + k + " to " + v)
        else:
            source = "ROOT " + "[A-Z]*[a-z]*:" + k + "\n"
            dst = "ROOT " + v + "\n"
            res = re.sub(source, dst, fh, 1)
            if res != fh:
                print("Renaming root " + k + " to " + v)
        fh = res

    with open(out_path, "w") as file:
        file.write(fh)

def create_skeleton_from_bvh(source_file,output_file):
    lSdkManager = FbxManager.Create()
    mainScene = FbxScene.Create(lSdkManager,"Main Scene")
    animStack = FbxAnimStack.Create(mainScene, "Anim stack")
    animBaseLayer = FbxAnimLayer.Create(mainScene, "Base Layer")
    animStack.AddMember(animBaseLayer)

    with open(source_file) as f:
        mocap = Bvh(f.read())

    bvh_skeleton_root = mocap.search('ROOT')[0]

    created_nodes = []

    # Create skeleton root.
    lRootName = FbxString(bvh_skeleton_root.value[1])
    lSkeletonRootAttribute = FbxSkeleton.Create(mainScene, "Root");
    lSkeletonRootAttribute.SetSkeletonType(FbxSkeleton.eRoot);
    lSkeletonRoot = FbxNode.Create(mainScene,lRootName.Buffer());
    lSkeletonRoot.SetNodeAttribute(lSkeletonRootAttribute);
    lSkeletonRoot.LclTranslation.Set(FbxDouble4(0.0, -40.0, 0.0,1.0));

    created_nodes.append(lSkeletonRoot)

    # Create skeleton limbs nodes, following the bvh file
    for node in mocap.search('JOINT') :
        limbName = node.value[1];
        limbNodeAttribute = FbxSkeleton.Create(mainScene,limbName);
        limbNodeAttribute.SetSkeletonType(FbxSkeleton.eLimbNode);
        limbNodeAttribute.Size.Set(1.0);
        limbFbxNode = FbxNode.Create(mainScene,limbName);
        limbFbxNode.SetNodeAttribute(limbNodeAttribute);
        offsets = mocap.joint_offset(limbName)
        limbFbxNode.LclTranslation.Set(FbxDouble4(offsets[0],offsets[1],offsets[2],1.0));

        if "End Site" in node.children:
            endSiteNodeAttribute = FbxSkeleton.Create(mainScene,"End Site");
            endSiteNodeAttribute.SetSkeletonType(FbxSkeleton.eEffector);
            endSiteNodeAttribute.Size.Set(1.0);
            endSiteFbxNode = FbxNode.Create(mainScene,"End Site");
            endSiteFbxNode.SetNodeAttribute(endSiteNodeAttribute);
            limbFbxNode.AddChild(endSiteFbxNode)

        parentFbxNode = None
        for fbx_file_node in created_nodes:
            if node.parent.name == fbx_file_node.GetName():
                parentFbxNode = fbx_file_node
        if parentFbxNode != None:
            parentFbxNode.AddChild(limbFbxNode)

        created_nodes.append(limbFbxNode)

    rootNode = mainScene.GetRootNode()
    rootNode.AddChild(lSkeletonRoot)

    lAnimStack = FbxAnimStack.Create(mainScene,"Animation Stack")
    lAnimLayer = FbxAnimLayer.Create(mainScene, "Base Layer");
    lAnimStack.AddMember(lAnimLayer);
    
    lCurve = lSkeletonRoot.LclRotation.GetCurve(lAnimLayer, "Z", True);
    lTime = FbxTime()
    if (lCurve) :
        lCurve.KeyModifyBegin();
        lTime.SetSecondDouble(0.0);
        lKeyIndex = lCurve.KeyAdd(lTime);
        lCurve.KeySetValue(lKeyIndex[0], 0.0);
        lCurve.KeySetInterpolation(lKeyIndex[0], FbxAnimCurveDef.eInterpolationCubic);
        lCurve.KeyModifyEnd();

    SaveScene(lSdkManager,mainScene,output_file,0,False)

# copied from  https://help.autodesk.com/cloudhelp/2018/ENU/FBX-Developer-Help/cpp_ref/_common_2_common_8cxx-example.html
# just adapted to python syntax
def SaveScene(pManager,pScene,pFilename,pFileFormat,pEmbedMedia):
    lMajor = 0
    lMinor = 0
    lRevision = 0
    lStatus = True;
    # Create an exporter.
    lExporter = FbxExporter.Create(pManager, "");
    """
    if( pFileFormat < 0 || pFileFormat >= pManager->GetIOPluginRegistry()->GetWriterFormatCount() )
    {
        // Write in fall back format in less no ASCII format found
        pFileFormat = pManager->GetIOPluginRegistry()->GetNativeWriterFormat();
        //Try to export in ASCII if possible
        int lFormatIndex, lFormatCount = pManager->GetIOPluginRegistry()->GetWriterFormatCount();
        for (lFormatIndex=0; lFormatIndex<lFormatCount; lFormatIndex++)
        {
            if (pManager->GetIOPluginRegistry()->WriterIsFBX(lFormatIndex))
            {
                FbxString lDesc =pManager->GetIOPluginRegistry()->GetWriterFormatDescription(lFormatIndex);
                const char *lASCII = "ascii";
                if (lDesc.Find(lASCII)>=0)
                {
                    pFileFormat = lFormatIndex;
                    break;
                }
            }
        } 
    }
    """
    # Set the export states. By default, the export states are always set to
    # true except for the option eEXPORT_TEXTURE_AS_EMBEDDED. The code below
    # shows how to change these states.
    IOS_REF = FbxIOSettings.Create(pManager,"IOSRoot")
    IOS_REF.SetBoolProp(EXP_FBX_MATERIAL,        True);
    IOS_REF.SetBoolProp(EXP_FBX_TEXTURE,         True);
    IOS_REF.SetBoolProp(EXP_FBX_EMBEDDED,        pEmbedMedia);
    IOS_REF.SetBoolProp(EXP_FBX_SHAPE,           True);
    IOS_REF.SetBoolProp(EXP_FBX_GOBO,            True);
    IOS_REF.SetBoolProp(EXP_FBX_ANIMATION,       True);
    IOS_REF.SetBoolProp(EXP_FBX_GLOBAL_SETTINGS, True);
    # Initialize the exporter by providing a filename.
    if(lExporter.Initialize(pFilename, pFileFormat, pManager.GetIOSettings()) == False):
        print("Call to FbxExporter::Initialize() failed.\n")
        print("Error returned: %s\n\n", lExporter.GetStatus().GetErrorString())
        return False

    # lMajor, lMinor, lRevision = FbxManager.GetFileFormatVersion()
    # we want to use the 7.5.0 version, corresponding to FBX 2016/2017
    lMajor = 7
    lMinor = 5
    lRevision = 0
    print("FBX file format version {}.{}.{}\n".format(lMajor, lMinor, lRevision))
    # Export the scene.
    lStatus = lExporter.Export(pScene);
    # Destroy the exporter.
    lExporter.Destroy()
    return lStatus

