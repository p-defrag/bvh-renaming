from conversion import rename,create_skeleton_from_bvh

if __name__ == '__main__':
	rename('tests/matteo_spiderman.bvh', 'tests/test_renamed.bvh')
	create_skeleton_from_bvh('tests/test_renamed.bvh','test_output.fbx')