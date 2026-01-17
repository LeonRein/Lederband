import os
import pathlib
from tkinter.filedialog import askopenfilename, asksaveasfilename
from typing import Callable, Optional

import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from PIL.Image import Image

from src.engine import create_band_image
from src.models import Badge, BadgeRow, LeatherBand

DEFAULT_PRESET_PATH = os.path.join(os.getcwd(), "presets/")
DEFAULT_EXPORT_PATH = os.path.join(os.getcwd(), "output/")


class BadgeListElement:
    def __init__(
        self,
        index: int,
        length: int,
        on_up=None,
        on_down=None,
        on_change=None,
        on_delete=None,
    ) -> None:
        self.index = index
        self.length = length
        self.on_up: Optional[Callable[[int], None]] = on_up
        self.on_down: Optional[Callable[[int], None]] = on_down
        self.on_change: Optional[Callable[[None], None]] = on_change
        self.on_delete: Optional[Callable[[int], None]] = on_delete
        self.btn_up = ctk.CTkButton(self, text="↑", width=30, command=self._up)
        self.btn_down = ctk.CTkButton(self, text="↓", width=30, command=self._down)
        self.btn_change = ctk.CTkButton(
            self, text="Change", width=60, command=self._change
        )
        if self.on_delete is not None:
            self.btn_del = ctk.CTkButton(
                self,
                text="X",
                width=30,
                fg_color="red",
                hover_color="darkred",
                command=self._delete,
            )

        BadgeListElement.refresh_ui(self)

    def _refresh_buttons(self):
        if self.index == self.length - 1:
            self.btn_up.configure(state="disabled")
        else:
            self.btn_up.configure(state="normal")
        if self.index == 0:
            self.btn_down.configure(state="disabled")
        else:
            self.btn_down.configure(state="normal")

    def refresh_ui(self):
        self._refresh_buttons()

    def _up(self):
        if self.on_up:
            self.on_up(self.index)

    def _down(self):
        if self.on_down:
            self.on_down(self.index)

    def _change(self):
        if self.on_change:
            self.on_change()

    def _delete(self):
        if self.on_delete:
            self.on_delete(self.index)


class BadgeRowFrame(ctk.CTkFrame, BadgeListElement):
    def __init__(
        self,
        master,
        badge_row,
        index: int,
        length: int,
        on_up,
        on_down,
        on_change,
        on_delete,
    ):
        ctk.CTkFrame.__init__(self, master, fg_color=("gray75", "gray25"))
        BadgeListElement.__init__(
            self, index, length, on_up, on_down, on_change, on_delete
        )
        self.badge_row = badge_row

        self.grid_columnconfigure(0, weight=1)

        # Buttons
        self.btn_up.grid(row=0, column=1, padx=2, pady=(5, 0))

        self.btn_down.grid(row=0, column=2, padx=2, pady=(5, 0))

        self.btn_change.configure(text="", fg_color="transparent", state="hidden")
        self.btn_change.grid(row=0, column=3, padx=2, pady=(5, 0))

        self.btn_del.grid(row=0, column=4, padx=5, pady=(5, 0))

        self.badges_list = ctk.CTkFrame(self, fg_color="transparent")
        self.badges_list.grid(row=1, columnspan=5, padx=0, pady=0, sticky="ew")

        self.badges_list.grid_columnconfigure(0, weight=1)

        self.refresh_ui()

    def _refresh_badges_list(self):
        for widget in self.badges_list.winfo_children():
            widget.destroy()
        for i, badge in enumerate(self.badge_row.badges):
            badge_frame = BadgeFrame(
                self.badges_list,
                badge,
                i,
                len(self.badge_row.badges),
                self._on_badge_up,
                self._on_badge_down,
                self._on_badge_change,
                None,
            )
            if i == 0:
                badge_frame.pack(padx=5, pady=5, side="bottom", fill="x")
            else:
                badge_frame.pack(padx=5, pady=(5, 0), side="bottom", fill="x")

    def refresh_ui(self):
        self._refresh_badges_list()
        self._refresh_buttons()

    def _on_badge_up(self, index):
        if index >= len(self.badge_row.badges) - 1:
            return
        self.badge_row.badges[index], self.badge_row.badges[index + 1] = (
            self.badge_row.badges[index + 1],
            self.badge_row.badges[index],
        )
        self._refresh_badges_list()
        super()._change()

    def _on_badge_down(self, index):
        if index == 0:
            return
        self.badge_row.badges[index], self.badge_row.badges[index - 1] = (
            self.badge_row.badges[index - 1],
            self.badge_row.badges[index],
        )
        self._refresh_badges_list()
        super()._change()

    def _on_badge_change(self):
        BadgeListElement._change(self)


class BadgeFrame(ctk.CTkFrame, BadgeListElement):
    def __init__(
        self,
        master,
        badge,
        index: int,
        length: int,
        on_up,
        on_down,
        on_change,
        on_delete,
    ):
        ctk.CTkFrame.__init__(self, master)
        BadgeListElement.__init__(
            self, index, length, on_up, on_down, on_change, on_delete
        )
        self.badge = badge

        self.grid_columnconfigure(0, weight=1)

        # Badge name/file
        self.label = ctk.CTkLabel(self, text=badge.name, anchor="w")
        self.label.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Buttons
        self.btn_up.grid(row=0, column=1, padx=(0, 5))

        self.btn_down.grid(row=0, column=2, padx=(0, 5))

        self.btn_change.grid(row=0, column=3, padx=(0, 5))

        if self.on_delete is not None:
            self.btn_del.grid(row=0, column=4, padx=(0, 5))

    def _change(self):
        path = askopenfilename(title="Select Badge", filetypes=[("PNG Files", "*.png")])
        if path is None or not os.path.exists(path):
            return
        self.badge.image_path = path
        super()._change()


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.band = LeatherBand()
        self.preview_image: Optional[Image] = None

        self.title("LeatherBand")
        self.geometry("600x800")

        self.padding = 10
        self.heading_font = ctk.CTkFont(family="Roboto", size=14, weight="bold")

        # --- UI Layout ---
        self.grid_columnconfigure(0, weight=0)  # Config panel
        self.grid_columnconfigure(1, weight=1)  # Preview panel (dynamic)
        self.grid_rowconfigure(0, weight=1)

        # Left Panel (Controls)
        self.left_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.left_panel.grid(row=0, column=0, sticky="nsew")
        self.left_panel.grid_rowconfigure(3, weight=1)  # Scrollable area expands

        # Presets
        self.preset_frame = ctk.CTkFrame(self.left_panel)
        self.preset_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=self.padding,
            pady=(self.padding, self.padding / 2),
        )
        self.preset_frame.grid_columnconfigure(0, weight=1)

        self.lbl_preset = ctk.CTkLabel(
            self.preset_frame,
            text="Preset",
            font=self.heading_font,
            fg_color="gray30",
            corner_radius=6,
        )
        self.lbl_preset.grid(
            row=0,
            columnspan=2,
            padx=self.padding,
            pady=(self.padding, self.padding / 2),
            sticky="ew",
        )
        self.var_preset = ctk.StringVar(value="No Preset Selected")
        self.ent_preset = ctk.CTkEntry(
            self.preset_frame, textvariable=self.var_preset, state="readonly"
        )
        self.ent_preset.grid(
            row=1, columnspan=2, sticky="ew", padx=self.padding, pady=self.padding / 2
        )
        self.btn_load = ctk.CTkButton(
            self.preset_frame, text="Load Preset", command=self.load_preset
        )
        self.btn_load.grid(
            row=2,
            column=0,
            padx=(self.padding, self.padding / 2),
            pady=(self.padding / 2, self.padding),
        )
        self.btn_new = ctk.CTkButton(
            self.preset_frame, text="New Preset", command=self.new_preset
        )
        self.btn_new.grid(
            row=2,
            column=1,
            padx=(self.padding / 2, self.padding),
            pady=(self.padding / 2, self.padding),
        )

        # Background
        self.bg_frame = ctk.CTkFrame(self.left_panel)
        self.bg_frame.grid(
            row=1, column=0, sticky="ew", padx=self.padding, pady=self.padding / 2
        )
        self.bg_frame.grid_columnconfigure(0, weight=1)

        self.lbl_bg = ctk.CTkLabel(
            self.bg_frame,
            text="Background",
            font=self.heading_font,
            fg_color="gray30",
            corner_radius=6,
        )
        self.lbl_bg.grid(
            row=0,
            column=0,
            padx=self.padding,
            pady=(self.padding, self.padding / 2),
            sticky="ew",
        )
        self.var_bg_path = ctk.StringVar(value="No file selected")
        self.ent_bg = ctk.CTkEntry(
            self.bg_frame, textvariable=self.var_bg_path, state="readonly"
        )
        self.ent_bg.grid(
            row=1, column=0, padx=self.padding, pady=self.padding / 2, sticky="ew"
        )
        self.btn_sel_bg = ctk.CTkButton(
            self.bg_frame, text="Select", width=50, command=self.select_background
        )
        self.btn_sel_bg.grid(
            row=2,
            column=0,
            padx=self.padding,
            pady=(self.padding / 2, self.padding),
            sticky="ew",
        )

        # Margin
        self.margin_frame = ctk.CTkFrame(self.left_panel)
        self.margin_frame.grid(
            row=2, column=0, sticky="ew", padx=self.padding, pady=self.padding / 2
        )
        self.margin_frame.grid_columnconfigure(0, weight=1)
        self.margin_frame.grid_columnconfigure(1, weight=1)

        self.lbl_margin = ctk.CTkLabel(
            self.margin_frame,
            text="Margin",
            font=self.heading_font,
            fg_color="gray30",
            corner_radius=6,
        )
        self.lbl_margin.grid(
            row=0,
            columnspan=2,
            padx=self.padding,
            pady=(self.padding, self.padding / 2),
            sticky="ew",
        )
        self.slider_margin = ctk.CTkSlider(
            self.margin_frame, from_=0, to=50, command=self.on_margin_change
        )
        self.slider_margin.set(10)
        self.slider_margin.grid(
            row=1,
            column=0,
            padx=(self.padding, 0),
            pady=(self.padding / 2, self.padding),
            sticky="ew",
        )
        self.lbl_margin_val = ctk.CTkLabel(self.margin_frame, text="10")
        self.lbl_margin_val.grid(
            row=1,
            column=1,
            padx=(0, self.padding),
            pady=(self.padding / 2, self.padding),
            sticky="ew",
        )

        # Badges
        self.badges_frame = ctk.CTkFrame(self.left_panel)
        self.badges_frame.grid(
            row=3, column=0, sticky="nsew", padx=self.padding, pady=self.padding / 2
        )
        self.badges_frame.grid_rowconfigure(2, weight=1)
        self.badges_frame.grid_columnconfigure(0, weight=1)

        self.lbl_badges = ctk.CTkLabel(
            self.badges_frame,
            text="Badges",
            font=self.heading_font,
            fg_color="gray30",
            corner_radius=6,
        )
        self.lbl_badges.grid(
            row=0,
            columnspan=2,
            padx=self.padding,
            pady=(self.padding, self.padding / 2),
            sticky="ew",
        )

        self.btn_add_badge = ctk.CTkButton(
            self.badges_frame, text="Add Badge", command=self.add_badge
        )
        self.btn_add_badge.grid(
            row=1,
            column=0,
            padx=(self.padding, self.padding / 2),
            pady=self.padding / 2,
            sticky="ew",
        )

        self.btn_add_badge_row = ctk.CTkButton(
            self.badges_frame, text="Add Badge Row", command=self.add_badge_row
        )
        self.btn_add_badge_row.grid(
            row=1,
            column=1,
            padx=(self.padding / 2, self.padding),
            pady=self.padding / 2,
            sticky="ew",
        )

        self.badges_list = ctk.CTkScrollableFrame(
            self.badges_frame, fg_color="transparent"
        )
        self.badges_list.grid(
            row=2,
            columnspan=2,
            padx=0,
            pady=(self.padding / 2, 0),
            sticky="nsew",
        )

        # 3. Bottom Section - Export
        self.btn_export = ctk.CTkButton(
            self.left_panel,
            text="Export Image",
            fg_color="green",
            hover_color="darkgreen",
            command=self.export_image,
        )
        self.btn_export.grid(
            row=6,
            column=0,
            padx=self.padding,
            pady=(self.padding / 2, self.padding),
            sticky="ew",
        )

        # Right Panel - Preview
        self.preview_panel = ctk.CTkFrame(self)
        self.preview_panel.grid(
            row=0, column=1, sticky="nsew", padx=(0, self.padding), pady=self.padding
        )
        self.preview_panel.grid_rowconfigure(0, weight=1)
        self.preview_panel.grid_columnconfigure(0, weight=1)

        self.lbl_preview = ctk.CTkLabel(self.preview_panel, text="Preview")
        self.lbl_preview.grid(row=0, column=0, padx=5, pady=5)

    def refresh_badges_list(self):
        for widget in self.badges_list.winfo_children():
            widget.destroy()
        for i, badge in enumerate(self.band.badges):
            if isinstance(badge, Badge):
                badge_ui = BadgeFrame(
                    self.badges_list,
                    badge,
                    i,
                    len(self.band.badges),
                    self._on_badge_up,
                    self._on_badge_down,
                    self._on_badge_change,
                    self._on_badge_delete,
                )
            else:
                badge_ui = BadgeRowFrame(
                    self.badges_list,
                    badge,
                    i,
                    len(self.band.badges),
                    self._on_badge_up,
                    self._on_badge_down,
                    self._on_badge_change,
                    self._on_badge_delete,
                )
            badge_ui.pack(fill="x", side="bottom", pady=5)

    def refresh_preview(self):
        if (
            self.band.image_path is None
            or self.band.image_path == ""
            or self.band.image_path == ()
        ):
            self.preview_image = None
            self.lbl_preview.configure(image=None, text="No Background image selected")
            return
        try:
            self.preview_image = create_band_image(self.band)
        except FileNotFoundError as e:
            self.preview_image = None
            self.lbl_preview.configure(image=None, text="No Preview")
            CTkMessagebox(title="Error", message=str(e), icon="cancel")
            return
        if self.preview_image is None:
            self.lbl_preview.configure(image=None, text="No Preview")
        else:
            ctk_image = ctk.CTkImage(
                light_image=self.preview_image,
                dark_image=self.preview_image,
                size=self.preview_image.size,
            )
            self.lbl_preview.configure(image=ctk_image, text="")

    def refresh_elements(self):
        self.var_bg_path.set(self.band.image_path)
        self.slider_margin.set(self.band.margin)
        self.lbl_margin_val.configure(text=f"{self.band.margin}px")

    def refresh_ui(self):
        self.refresh_elements()
        self.refresh_preview()
        self.refresh_badges_list()

    def load_preset(self):
        path = askopenfilename(
            filetypes=[("JSON Files", "*.json")],
            initialdir=DEFAULT_PRESET_PATH,
            title="Load Preset",
        )
        if path is None:
            return
        self.var_preset.set(path)
        try:
            self.band = LeatherBand.load_from_file(path)
        except Exception as e:
            CTkMessagebox(
                title="Error", message=f"Failed to load preset: {e}", icon="cancel"
            )
        self.refresh_ui()

    def new_preset(self):
        path = asksaveasfilename(
            filetypes=[("json", "*.json")],
            initialdir=DEFAULT_PRESET_PATH,
            title="Save Preset",
        )
        if path is None:
            return
        self.var_preset.set(path)
        self.band = LeatherBand()
        try:
            self.band.save_to_file(path)
        except Exception as e:
            CTkMessagebox(
                title="Error", message=f"Failed to save preset: {e}", icon="cancel"
            )
        self.refresh_ui()

    def select_background(self):
        path = askopenfilename(
            title="Select Background", filetypes=[("PNG Files", "*.png")]
        )
        if path is None or path == "" or path == ():
            return
        if not os.path.exists(path):
            CTkMessagebox(
                title="Error", message=f"File not found: {path}", icon="cancel"
            )
            return
        self.band.image_path = path
        self.var_bg_path.set(path)
        self.refresh_preview()

    def on_margin_change(self, event):
        val = int(event)
        self.band.margin = val
        self.refresh_preview()
        self.refresh_elements()

    def add_badge(self):
        path = askopenfilename(title="Select Badge", filetypes=[("PNG Files", "*.png")])
        if path is None or not os.path.exists(path):
            return
        self.band.badges.append(Badge(path))
        self.refresh_badges_list()
        self.refresh_preview()

    def add_badge_row(self):
        path1 = askopenfilename(
            title="Select Badge", filetypes=[("PNG Files", "*.png")]
        )
        if path1 is None or not os.path.exists(path1):
            return
        path2 = askopenfilename(
            title="Select Badge", filetypes=[("PNG Files", "*.png")]
        )
        if path2 is None or not os.path.exists(path2):
            return
        self.band.badges.append(BadgeRow.from_paths(path1, path2))
        self.refresh_badges_list()
        self.refresh_preview()

    def _on_badge_delete(self, index):
        del self.band.badges[index]
        self.refresh_badges_list()
        self.refresh_preview()

    def _on_badge_change(self):
        self.refresh_preview()
        self.refresh_badges_list()

    def _on_badge_up(self, index):
        if index >= len(self.band.badges) - 1:
            return
        self.band.badges[index], self.band.badges[index + 1] = (
            self.band.badges[index + 1],
            self.band.badges[index],
        )
        self.refresh_preview()
        self.refresh_badges_list()

    def _on_badge_down(self, index):
        if index <= 0:
            return
        self.band.badges[index], self.band.badges[index - 1] = (
            self.band.badges[index - 1],
            self.band.badges[index],
        )
        self.refresh_preview()
        self.refresh_badges_list()

    def export_image(self):
        if self.preview_image is None:
            CTkMessagebox(title="Export Error", message="No image to export")
            return
        if os.path.exists(self.var_preset.get()):
            try:
                self.band.save_to_file(self.var_preset.get())
                preset_name = pathlib.Path(self.var_preset.get()).stem
            except Exception as e:
                CTkMessagebox(
                    title="Export Error", message=f"Failed to save preset: {e}"
                )
                return
        else:
            CTkMessagebox(title="Export Error", message="Preset file not found")
            preset_name = "default"

        path = os.path.join(DEFAULT_EXPORT_PATH, preset_name + ".png")
        try:
            self.preview_image.save(path, format="PNG")
        except Exception as e:
            CTkMessagebox(title="Export Error", message=f"Failed to export image: {e}")
            return

        CTkMessagebox(title="Export", message=f"Image exported to {path}")
        pass
