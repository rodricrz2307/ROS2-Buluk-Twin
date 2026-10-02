import pymeshlab, os


for f in sorted(os.listdir('.')):
    if not f.endswith('.stl'): continue
    ms = pymeshlab.MeshSet(); ms.load_new_mesh(f)
    n = ms.current_mesh().face_number()
    
    if n > 100000:
        ms.meshing_decimation_quadric_edge_collapse(targetfacenum=100000, preservenormal=True)
        ms.save_current_mesh(f, binary=True)
    bb = ms.current_mesh().bounding_box()

    print(f"{f}: {n} -> {ms.current_mesh().face_number()} caras | tamaño "
          f"{bb.dim_x():.3f} x {bb.dim_y():.3f} x {bb.dim_z():.3f} | "
          f"min {bb.min()} max {bb.max()}")