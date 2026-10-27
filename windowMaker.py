from pathlib import Path
import flet as ft
import flet_video as fv
import random
import STLMaker
from STLMaker import (
    export_house_stl,
    DEFAULT_WIDTH,
    DEFAULT_HEIGHT,
    DEFAULT_DEPTH,
    DEFAULT_ROOF_ANGLE,
)
from mpl_previewer import render_stl_to_png_b64
from supporter_generator import supporter_generator
INITIAL_STL_PATH = Path(r"assets\Demo.stl")
OUTPUT_DIR = Path("STL_cache")


def app(page: ft.Page):
    page.title = "House STL Maker"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 800
    page.window_height = 600
    page.padding = 16

    OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

    # ------------------------------------------------------------
    # 左ペイン: 視点スライダー（上）＋ プレビュー（下）
    # ------------------------------------------------------------
    elev = ft.Slider(
        min=-90, max=90, divisions=15, value=20, label="縦回転: {value}"
    )
    azim = ft.Slider(
        min=0, max=360, divisions=15, value=45, label="横回転: {value}"
    )

    # 初期は空のスロット（Image は生成/読み込み後にだけ入れる）
    preview_slot = ft.Container(
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
        border_radius=12,
        padding=8,
        expand=True,  # 左カラムの残り領域いっぱいに広げる
    )

    info = ft.Text(size=12, color=ft.Colors.GREY)

    # 直近のSTLパス（再描画用）
    last_stl: Path | None = None

    def set_preview_from(stl_path: Path):
        nonlocal last_stl
        if not stl_path.exists():
            info.value = f"ファイルが見つかりません: {stl_path}"
            page.update()
            return
        w = max(int(page.window_width // 2) - 48, 420)   # 左半分の幅を概算
        h = max(int(page.window_height) - 240, 360)      # 高さを概算
        b64 = render_stl_to_png_b64(
            stl_path,
            elev=float(elev.value),
            azim=float(360-azim.value),
            width=w,
            height=h,
        )
        preview_slot.content = ft.Image(src_base64=b64, expand=True)
        last_stl = stl_path
        # info.value = f"表示中: {stl_path.resolve()}"
        page.update()

    # ------------------------------------------------------------
    # 右ペイン: パラメータスライダー + 作成ボタン
    # ------------------------------------------------------------
    sl_roof = ft.Slider(
        min=80, max=150, divisions=70, value=DEFAULT_ROOF_ANGLE, label="屋根角度: {value}°"
    )
    sl_height = ft.Slider(
        min=5, max=10, divisions=5, value=DEFAULT_HEIGHT, label="家の高さ: {value}"
    )
    sl_depth = ft.Slider(
        min=1, max=5, divisions=4, value=DEFAULT_DEPTH, label="奥行: {value}"
    )

    def on_create_click(e: ft.ControlEvent):
        STLMaker.params = STLMaker.HouseParams(
            roof_angle_deg=float(sl_roof.value),
            house_height=float(sl_height.value),
            house_depth=float(sl_depth.value),
            house_width=float(DEFAULT_WIDTH),  # 幅は固定
        )
        stl_path = export_house_stl(
            STLMaker.params,
            out_dir=OUTPUT_DIR,
            filename_prefix="house",
        )
        set_preview_from(stl_path)

    def on_confirm(e):
        supporter_generator(sl_roof.value)
        page.controls.clear()
        make_inst_ui()

    create_btn = ft.FilledButton(text="プレビュー作成", icon=ft.Icons.WIFI_PROTECTED_SETUP, on_click=on_create_click)
    exp_btn = ft.FilledButton(text="ダウンロード・組み立て操作へ", icon=ft.Icons.CHECK, on_click=on_confirm)
    # ------------------------------------------------------------
    def rerender_on_view_change(e: ft.ControlEvent):
        if last_stl and last_stl.exists() and preview_slot.content is not None:
            set_preview_from(last_stl)

    elev.on_change = rerender_on_view_change
    azim.on_change = rerender_on_view_change

    def on_window_event(e: ft.WindowEvent):
        if e.data in ("resized", "maximize", "restore"):
            rerender_on_view_change(e)

    page.on_window_event = on_window_event

    # ------------------------------------------------------------
    # 初期STLのプレビュー（存在するときのみ）
    # ------------------------------------------------------------
    if INITIAL_STL_PATH.exists():
        set_preview_from(INITIAL_STL_PATH)
    else:
        info.value = f"初期STLが見つかりません: {INITIAL_STL_PATH}"

    # ------------------------------------------------------------
    # レイアウト構築
    LEAD = ft.Container(width=24)
    GAP  = ft.Container(width=8)
    left_col = ft.Column(
        [
            ft.Row(
                [
                    ft.Icon(name=ft.Icons.REMOVE_RED_EYE_ROUNDED),
                    ft.Text("視点操作", weight=ft.FontWeight.BOLD,size=25),
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Row([LEAD,GAP,ft.Text("縦回転", weight=ft.FontWeight.NORMAL),],alignment=ft.MainAxisAlignment.START,vertical_alignment=ft.CrossAxisAlignment.CENTER),
            elev,
            ft.Row([LEAD,GAP,ft.Text("横回転", weight=ft.FontWeight.NORMAL),],alignment=ft.MainAxisAlignment.START,vertical_alignment=ft.CrossAxisAlignment.CENTER),
            azim,
            preview_slot,
            ft.Container(height=8),
            info,
        ],
        expand=True,
        spacing=8,
    )

    right_col = ft.Column(
        [
            ft.Row(
                [
                    ft.Icon(name="home"),
                    ft.Text("家のパラメータ", weight=ft.FontWeight.BOLD,size=25),
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Row([LEAD,GAP,ft.Text("屋根角度", weight=ft.FontWeight.NORMAL),],alignment=ft.MainAxisAlignment.START,vertical_alignment=ft.CrossAxisAlignment.CENTER),
            sl_roof,
            ft.Row([LEAD,GAP,ft.Text("高さ", weight=ft.FontWeight.NORMAL),],alignment=ft.MainAxisAlignment.START,vertical_alignment=ft.CrossAxisAlignment.CENTER),
            sl_height,
            ft.Row([LEAD,GAP,ft.Text("奥行", weight=ft.FontWeight.NORMAL),],alignment=ft.MainAxisAlignment.START,vertical_alignment=ft.CrossAxisAlignment.CENTER),
            sl_depth,
            ft.Container(height=8),
            ft.Container(
                height=50,
                width=600,
                content=create_btn,
                # expand=True,             # 親カラム幅いっぱいに
            ),
            ft.Container(height=8),
            ft.Container(
                height=50,
                width=600,
                content=exp_btn,
                # expand=True,             # 親カラム幅いっぱいに
            )
        ],
        expand=True,
        spacing=12,
    )

    page.add(
        ft.Row(
            [
                ft.Container(content=left_col, expand=True),
                ft.VerticalDivider(width=1),
                ft.Container(content=right_col, expand=True),
            ],
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )
    )






    def make_inst_ui():
        page.theme_mode = ft.ThemeMode.DARK
        page.title = "サポータの使用方法"
        page.window.always_on_top = False
        page.spacing = 20
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        def handle_next(e):
            video.next()
            # print("Video.next()")

        def handle_previous(e):
            video.previous()
            # print("Video.previous()")

        def handle_playback_rate_change(e):
            video.playback_rate = e.control.value
            rate_text.value = f"再生速度: {e.control.value}×"
            page.update()
            print(f"Video.playback_rate = {e.control.value}")

        def normal_button(moji,func):
            text = ft.Text(moji,size=30,weight=ft.FontWeight.BOLD,)
            a =ft.FilledButton(content=text,on_click=func,
            style=ft.ButtonStyle(padding=ft.padding.symmetric(horizontal=24, vertical=12)))
            return a
        
        rate_text = ft.Text("再生速度: 1.0×",size=20,weight=ft.FontWeight.BOLD,)
        sample_media = [
            fv.VideoMedia(resource="assets/towerKumitate.mp4"),
            fv.VideoMedia(resource="assets/90kousa.mp4"),
            fv.VideoMedia(resource="assets/itaExp.mp4"),
            fv.VideoMedia(resource="assets/kumiawase.mp4"),
            fv.VideoMedia(resource="assets/yane.mp4"),
        ]


        left_panel = ft.Column(
                        expand=7,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            video := fv.Video(
                                expand=True,
                                playlist=sample_media,
                                playlist_mode=fv.PlaylistMode.LOOP,
                                fill_color=ft.Colors.BLACK87,
                                aspect_ratio=16 / 9,
                                volume=100,
                                autoplay=False,
                                filter_quality=ft.FilterQuality.HIGH,
                                muted=True,
                            ),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[
                                    normal_button("前の動画へ", handle_previous),
                                    normal_button("次の動画へ", handle_next),
                                ],
                            ),
                            ft.Container(height=16),
                            rate_text,
                            ft.Slider(
                                height=6,
                                min=0.5,
                                value=1,
                                max=2,
                                divisions=3,
                                width=400,
                                on_change=handle_playback_rate_change,
                            ),
                            ft.Container(height=16),
                        ],
                    )
        print(STLMaker.params.house_depth)
        right_panel = ft.Column(
                        expand=3,
                        spacing=8,
                        controls=[
                            ft.Text("高さ:  "+str(int(STLMaker.params.house_height))+"本",size=25,weight=ft.FontWeight.BOLD),
                            ft.Divider(),
                            ft.Text("奥行:  "+str(int(STLMaker.params.house_depth))+"面",size=25,weight=ft.FontWeight.BOLD),
                            ft.Divider(),
                            ft.Text("屋根の角度:  "+str(int(STLMaker.params.roof_angle_deg))+"°",size=25,weight=ft.FontWeight.BOLD),
                            ft.Divider(),                            
                        ],  
                    )



        page.add(
            ft.Row(
                expand=True,
                controls=[
                    left_panel,
                    ft.VerticalDivider(width=1),
                    right_panel,
                ],
            )
        )




if __name__ == "__main__":
    ft.app(target=app,assets_dir="assets")

for item in OUTPUT_DIR.iterdir():
    if item.is_file():
        item.unlink()

