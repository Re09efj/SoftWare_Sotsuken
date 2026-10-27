from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import time
from typing import Tuple
from crossplate import create_roof
import trimesh
# ===============================
# パラメータ定義（UIが触るのは基本ここ）
# ===============================
@dataclass
class HouseParams:
    roof_angle_deg: float   # 屋根角度（UI右側スライダー）
    house_height: float     # 家の高さ（軒高）（UI右側スライダー）
    house_depth: float      # 家の奥行（UI右側スライダー）
    house_width: float      # 家の幅（固定で良い／必要ならUIから変更してもOK）

params: HouseParams

# ===============================
# 便利関数（屋根の上がり量などの派生量）
# ===============================
def calc_roof_rise(roof_angle_deg):
    import math
    A = math.radians(roof_angle_deg)
    b = 2 * 55 * math.sin(A / 2)     # 底辺
    H = 55 * math.cos(A / 2)   
    h = H * (1 - 65 / b)             # 底辺からの高さ
    return h, H


def bbox_centered(extents: Tuple[float, float, float]) -> trimesh.Trimesh:
    """
    extents=(x,y,z) の直方体を“原点中心”に作るユーティリティ。
    """
    box = trimesh.creation.box(extents=extents)
    # trimesh.creation.box はデフォルトで原点中心
    return box


# ===============================
# メイン：家メッシュの組み立て（TODOに屋根を実装）
# ===============================
def build_house_mesh(params: HouseParams) -> trimesh.Trimesh:
    """
    参照変数：
      params.roof_angle_deg  -> 屋根の角度を使用（TODOで活用）
      params.house_height    -> 軒高（Z方向寸法の基準）
      params.house_depth     -> Y方向寸法
      params.house_width     -> X方向寸法
      params.wall_thickness  -> 壁厚（>0 なら中抜きなどの処理を想定、TODO）

    原点は床面中心とするため、
      - “箱の中心”を原点に置いたあとに、Z方向へ半高さだけ上げる必要がある点に注意。
    """
    W = float(params.house_width)
    D = W+float((params.house_depth-1)*(W-20))
    H = float(params.house_height*5)

    

    # --- ベース（軒までの箱） ---
    base = bbox_centered((W, D, H))
    kabehakoake = trimesh.creation.box(extents=[W-10, D-10, 50])
    base = base.difference(kabehakoake, engine='manifold')

    roof_rise, roof_H = calc_roof_rise(params.roof_angle_deg)
    roof = create_roof(params.roof_angle_deg, D)
    roof.apply_translation((22.5, 0, H*0.5 + (roof_H - roof_rise)))

    base = base.union(roof, engine='manifold')
    house = base.copy()
    return house


# ===============================
# STL 書き出しのインターフェース（windowMaker から呼ぶ）
# ===============================
def export_house_stl(
    params: HouseParams,
    out_dir = "STL_cache",
    filename_prefix = "house",
    ):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    mesh = build_house_mesh(params)

    from supporter_generator import supporter_generator
    # supporter_generator(params.roof_angle_deg)

    ts = time.strftime("%Y%m%d_%H%M%S")
    out_path = out_dir / f"{filename_prefix}_H{int(params.house_height)}_D{int(params.house_depth)}_A{int(params.roof_angle_deg)}_{ts}.stl"
    mesh.export(out_path)
    return out_path


# ===============================
# デフォルト値（UIと合わせると分かりやすい）
# ===============================
DEFAULT_WIDTH = 65    # 固定幅（UIで固定にするならここを使う）
DEFAULT_HEIGHT = 7    # 初期 高さ
DEFAULT_DEPTH = 3     # 初期 奥行
DEFAULT_ROOF_ANGLE = 80  # 初期 屋根角度[deg]


# ===============================
# 単体テスト的な実行（任意）
# ===============================
if __name__ == "__main__":
    p = HouseParams(
        roof_angle_deg=DEFAULT_ROOF_ANGLE,
        house_height=DEFAULT_HEIGHT,
        house_depth=DEFAULT_DEPTH,
        house_width=DEFAULT_WIDTH,
    )
    path = export_house_stl(p, out_dir="STL_cache", filename_prefix="house_demo")
    #--------------------------------------
    print("Washer exported:", path.resolve())
    
