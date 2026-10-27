from pathlib import Path
import base64
from io import BytesIO

import matplotlib
matplotlib.use("agg")  # GUI不要バックエンド
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from stl import mesh as stlmesh
import numpy as np


def render_stl_to_png_b64(
    stl_path: Path | str,
    elev: float = 20,
    azim: float = 45,
    width: int = 900,
    height: int = 600,
    face_color: str = "#855723",
    edge_color: str = "#120B0B",
    bg_color: str = "#EAE6E6",
) -> str:
    """
    STLを読み込み、matplotlibで描画したPNGをBase64文字列で返す。
    """
    stl_path = Path(stl_path)
    m = stlmesh.Mesh.from_file(str(stl_path))
    verts = m.vectors  # (N, 3, 3)

    dpi = 100
    fig = plt.figure(figsize=(width / dpi, height / dpi), dpi=dpi)
    ax = fig.add_subplot(111, projection="3d")
    ax.set_facecolor(bg_color)
    fig.patch.set_facecolor(bg_color)

    coll = Poly3DCollection(verts, linewidths=0.2, alpha=1.0)
    coll.set_facecolor(face_color)
    coll.set_edgecolor(edge_color)
    ax.add_collection3d(coll)

    pts = m.points.reshape(-1, 3)
    xyz_min = pts.min(axis=0)
    xyz_max = pts.max(axis=0)
    center = (xyz_min + xyz_max) / 2.0
    radius = float(np.max(xyz_max - xyz_min)) / 2.0*0.8

    ax.set_xlim(center[0] - radius, center[0] + radius)
    ax.set_ylim(center[1] - radius, center[1] + radius)
    ax.set_zlim(center[2] - radius, center[2] + radius)

    ax.view_init(elev=elev, azim=azim)
    ax.axis("off")
    plt.tight_layout(pad=0)

    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("ascii")
