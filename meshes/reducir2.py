import trimesh, fast_simplification as fs
for f in ['RobotBase.stl', 'Roller.stl', 'Tambor.stl']:
    m = trimesh.load(f)
    n = len(m.faces)
    if n > 100000:
        v, fa = fs.simplify(m.vertices, m.faces, target_reduction=1 - 100000/n)
        m = trimesh.Trimesh(v, fa)
        m.export(f)
    print(f, n, '->', len(m.faces), 'caras | min', m.bounds[0].round(3), 'max', m.bounds[1].round(3))
