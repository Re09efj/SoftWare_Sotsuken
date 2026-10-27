def supporter_generator(shiteikaku):
    import trimesh
    import numpy as np
    import math
    from pathlib import Path
    height=10
    outer_cyl = trimesh.creation.cylinder(radius=34, height=height, sections=128)
    eps = 1e-3
    inner_cyl = trimesh.creation.cylinder(radius=26, height=height+eps*2, sections=128)
    inner_cyl.apply_translation([0, 0, -eps])

    donut = outer_cyl.difference(inner_cyl, engine='manifold')
    # print("donut:", donut.is_volume, donut.is_watertight, donut.euler_number)
    hako0 = trimesh.creation.box(extents=[10.1, 10.1, 20])
    hako0.apply_translation([25, 0,0]) 
    hakoVar = trimesh.creation.box(extents=[10.1, 10.1, 20])
    hakoVar.apply_translation([25, 0, 0])
    hakoDeleter = trimesh.creation.box(extents=[20, 5, 10])
    hakoDeleter.apply_translation([25, 0, 0])
    # hako.show()
    def rotater(mesh,angle):
        R = trimesh.transformations.rotation_matrix(
            angle=np.radians(angle),        # ラジアン
            direction=[0, 0, 1],     # 回転軸（Z軸）
            point=[0, 0, 0]          # 回転の中心（原点）
        )
        mesh.apply_transform(R)

    rotater(hakoVar, shiteikaku)
    washer = donut.difference(hako0, engine='manifold')
    washer = washer.difference(hakoVar, engine='manifold')
    rotater(hakoDeleter, -20)
    for _ in range(math.floor((315-shiteikaku)//5)):
        rotater(hakoDeleter, -5)
        washer = washer.difference(hakoDeleter, engine='manifold')
    
    spPath= Path(__file__).resolve().parent/"supporter"
    for item in (spPath).iterdir():
        if item.is_file():
            item.unlink()
    washer.apply_scale(1.05)
    wnt = "washer"+str(int(shiteikaku))+".stl"
    washer.export(spPath/wnt)
    print("Supporter Exported")
