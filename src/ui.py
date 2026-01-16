import os
from tkinter.filedialog import askopenfilename
from typing import Optional

import customtkinter as ctk
from PIL.Image import Image

from src.engine import create_band_image
from src.models import Badge, LeatherBand


class BadgeRow(ctk.CTkFrame):
    def __init__(self, master, badge, index: int, on_up, on_down, on_change, on_delete):
        super().__init__(master)
        self.badge = badge
        self.index = index
        self.on_up = on_up
        self.on_down = on_down
        self.on_change = on_change
        self.on_delete = on_delete

        self.grid_columnconfigure(0, weight=1)

        # Badge name/file
        self.label = ctk.CTkLabel(self, text=badge.name, anchor="w")
        self.label.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Buttons
        self.btn_up = ctk.CTkButton(self, text="↑", width=30, command=self._up)
        self.btn_up.grid(row=0, column=1, padx=2)

        self.btn_down = ctk.CTkButton(self, text="↓", width=30, command=self._down)
        self.btn_down.grid(row=0, column=2, padx=2)

        self.btn_change = ctk.CTkButton(
            self, text="Change", width=60, command=self._change
        )
        self.btn_change.grid(row=0, column=3, padx=2)

        self.btn_del = ctk.CTkButton(
            self,
            text="X",
            width=30,
            fg_color="red",
            hover_color="darkred",
            command=self._delete,
        )
        self.btn_del.grid(row=0, column=4, padx=5)

    def _up(self):
        self.on_up(self.index)

    def _down(self):
        self.on_down(self.index)

    def _change(self):
        self.on_change(self.index)

    def _delete(self):
        self.on_delete(self.index)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.band = LeatherBand("", 10, [])
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
        self.btn_save = ctk.CTkButton(
            self.preset_frame, text="Save Preset", command=self.save_preset
        )
        self.btn_save.grid(
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
            column=0,
            padx=self.padding,
            pady=(self.padding, self.padding / 2),
            sticky="ew",
        )

        self.btn_add = ctk.CTkButton(
            self.badges_frame, text="Add Badge", command=self.add_badge
        )
        self.btn_add.grid(
            row=1, column=0, padx=self.padding, pady=self.padding / 2, sticky="ew"
        )

        self.badges_list = ctk.CTkScrollableFrame(
            self.badges_frame, fg_color="transparent"
        )
        self.badges_list.grid(
            row=2,
            column=0,
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
            badge_row = BadgeRow(
                self.badges_list,
                badge,
                i,
                self._on_badge_up,
                self._on_badge_down,
                self._on_badge_change,
                self._on_badge_delete,
            )
            badge_row.pack(fill="x", side="bottom")

    def refresh_preview(self):
        self.preview_image = create_band_image(self.band)
        if self.preview_image is None:
            return
        ctk_image = ctk.CTkImage(
            light_image=self.preview_image,
            dark_image=self.preview_image,
            size=self.preview_image.size,
        )
        self.lbl_preview.configure(image=ctk_image, text="")

    def refresh_ui(self):
        self.refresh_preview()
        self.refresh_badges_list()

    def load_preset(self):
        # Load preset data from file or database
        pass

    def save_preset(self):
        # Save current state as a preset
        pass

    def select_background(self):
        path = askopenfilename(
            title="Select Background", filetypes=[("PNG Files", "*.png")]
        )
        if path is None or not os.path.exists(path):
            return
        self.band.image_path = path
        self.var_bg_path.set(path)
        self.refresh_preview()

    def on_margin_change(self, event):
        val = int(event)
        self.lbl_margin_val.configure(text=f"{val}px")
        self.band.margin = val
        self.refresh_preview()

    def add_badge(self):
        path = askopenfilename(title="Select Badge", filetypes=[("PNG Files", "*.png")])
        if path is None or not os.path.exists(path):
            return
        self.band.badges.append(Badge(path))
        self.refresh_badges_list()
        self.refresh_preview()

    def _on_badge_change(self, index):
        path = askopenfilename(title="Select Badge", filetypes=[("PNG Files", "*.png")])
        if path is None or not os.path.exists(path):
            return
        self.band.badges[index].image_path = path
        self.refresh_badges_list()
        self.refresh_preview()

    def _on_badge_delete(self, index):
        del self.band.badges[index]
        self.refresh_badges_list()
        self.refresh_preview()

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
        # Export the current image
        pass
