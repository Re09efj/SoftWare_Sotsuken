import trimesh
import numpy as np

def create_plate(width=65, depth=300, height=10):
    # 中心原点で作成
    plate = trimesh.creation.box(extents=[width,depth,height])
    # plate.apply_translation([0,0,width/2+5])
    return plate

def rotater(mesh, angle, axis=[0,1,0]):
    R = trimesh.transformations.rotation_matrix(
        angle=np.radians(angle),
        direction=axis,
        point=[-22.5,0,0]  # 端点を中心に回る
    )
    mesh.apply_transform(R)

def create_roof(angle_deg,depth):
    tumatani = 65
    thickness=2
    plate1 = trimesh.creation.box(extents=[tumatani,depth,thickness])
    plate2 = trimesh.creation.box(extents=[tumatani,depth,thickness])
    rotater(plate1, (180-angle_deg)/2, axis=[0,1,0])
    rotater(plate2, (180-angle_deg)/2+angle_deg, axis=[0,1,0])    
    yane =  plate1.union(plate2, engine='manifold')
    return yane