from bvh import Bvh,BvhNode

def rename(bvh_path,fbx_path):
	source_file = open(bvh_path)
	dest_file = open(fbx_path,'w')

	mocap = Bvh(source_file.read())
	for name in mocap.get_joints_names():
		print(f"Renaming{name}")
		

