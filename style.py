# style.py — Light Mode Premium Design System
import customtkinter as ctk

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

COLORS = {
    "bg_primary":     "#F4F6FB",
    "bg_secondary":   "#FFFFFF",
    "bg_card":        "#FFFFFF",
    "bg_elevated":    "#F8F9FE",
    "bg_hover":       "#F0F2FA",
    "bg_input":       "#F4F6FB",

    "accent":         "#6366F1",
    "accent_hover":   "#4F52D9",
    "accent_soft":    "#EEF0FF",
    "accent_2":       "#06B6D4",
    "accent_2_soft":  "#E0F9FF",

    "success":        "#10B981",
    "success_soft":   "#ECFDF5",
    "danger":         "#EF4444",
    "danger_soft":    "#FEF2F2",
    "warning":        "#F59E0B",
    "warning_soft":   "#FFFBEB",
    "info":           "#3B82F6",
    "info_soft":      "#EFF6FF",

    "text_primary":   "#111827",
    "text_secondary": "#6B7280",
    "text_muted":     "#9CA3AF",
    "text_white":     "#FFFFFF",

    "sidebar_bg":     "#1E2B4A",
    "sidebar_active": "#6366F1",
    "sidebar_text":   "#94A3B8",
    "sidebar_active_text": "#FFFFFF",

    "border":         "#E5E7EB",
    "border_light":   "#F3F4F6",
    "border_accent":  "#6366F1",
}

FONTS = {
    "display":      ("Segoe UI", 28, "bold"),
    "title":        ("Segoe UI", 20, "bold"),
    "subtitle":     ("Segoe UI", 15, "bold"),
    "heading":      ("Segoe UI", 13, "bold"),
    "body":         ("Segoe UI", 12),
    "body_bold":    ("Segoe UI", 12, "bold"),
    "small":        ("Segoe UI", 11),
    "small_bold":   ("Segoe UI", 11, "bold"),
    "caption":      ("Segoe UI", 10),
    "caption_bold": ("Segoe UI", 10, "bold"),
    "nav":          ("Segoe UI", 12),
    "nav_bold":     ("Segoe UI", 12, "bold"),
    "number_xl":    ("Segoe UI", 28, "bold"),
    "number_lg":    ("Segoe UI", 22, "bold"),
    "number_md":    ("Segoe UI", 17, "bold"),
}

SPACING = {"xs":4,"sm":8,"md":12,"lg":16,"xl":20,"2xl":28,"3xl":44}
RADIUS  = {"sm":6,"md":10,"lg":14,"xl":18,"pill":50}
SIDEBAR_WIDTH = 220


def card_frame(parent, **kw):
    d = dict(fg_color=COLORS["bg_card"], corner_radius=RADIUS["xl"],
             border_width=1, border_color=COLORS["border"])
    d.update(kw); return ctk.CTkFrame(parent, **d)

def elevated_frame(parent, **kw):
    d = dict(fg_color=COLORS["bg_elevated"], corner_radius=RADIUS["xl"],
             border_width=1, border_color=COLORS["border"])
    d.update(kw); return ctk.CTkFrame(parent, **d)

def primary_button(parent, **kw):
    d = dict(fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
             text_color="#FFFFFF", corner_radius=RADIUS["md"],
             font=FONTS["body_bold"], height=38)
    d.update(kw); return ctk.CTkButton(parent, **d)

def secondary_button(parent, **kw):
    d = dict(fg_color=COLORS["bg_elevated"], hover_color=COLORS["bg_hover"],
             text_color=COLORS["text_secondary"], border_width=1,
             border_color=COLORS["border"], corner_radius=RADIUS["md"],
             font=FONTS["body"], height=38)
    d.update(kw); return ctk.CTkButton(parent, **d)

def danger_button(parent, **kw):
    d = dict(fg_color=COLORS["danger_soft"], hover_color="#FECACA",
             text_color=COLORS["danger"], border_width=1,
             border_color=COLORS["danger"], corner_radius=RADIUS["md"],
             font=FONTS["body_bold"], height=38)
    d.update(kw); return ctk.CTkButton(parent, **d)

def styled_entry(parent, **kw):
    d = dict(fg_color=COLORS["bg_input"], border_color=COLORS["border"],
             border_width=1, text_color=COLORS["text_primary"],
             placeholder_text_color=COLORS["text_muted"],
             corner_radius=RADIUS["md"], font=FONTS["body"], height=38)
    d.update(kw); return ctk.CTkEntry(parent, **d)

def styled_combo(parent, **kw):
    d = dict(fg_color=COLORS["bg_input"], border_color=COLORS["border"],
             border_width=1, text_color=COLORS["text_primary"],
             button_color=COLORS["bg_elevated"],
             button_hover_color=COLORS["bg_hover"],
             dropdown_fg_color=COLORS["bg_card"],
             dropdown_text_color=COLORS["text_primary"],
             dropdown_hover_color=COLORS["bg_hover"],
             corner_radius=RADIUS["md"], font=FONTS["body"], height=38)
    d.update(kw); return ctk.CTkComboBox(parent, **d)

def label(parent, text, style="body", color=None, **kw):
    return ctk.CTkLabel(parent, text=text,
                        font=FONTS.get(style, FONTS["body"]),
                        text_color=color or COLORS["text_primary"], **kw)

def muted_label(parent, text, style="small", **kw):
    return label(parent, text, style=style, color=COLORS["text_secondary"], **kw)

def divider(parent, **kw):
    return ctk.CTkFrame(parent, height=1, fg_color=COLORS["border"], **kw)

def badge(parent, text, color_key="accent", **kw):
    bg = COLORS.get(f"{color_key}_soft", COLORS["accent_soft"])
    fg = COLORS.get(color_key, COLORS["accent"])
    return ctk.CTkLabel(parent, text=text, font=FONTS["caption_bold"],
                        text_color=fg, fg_color=bg,
                        corner_radius=RADIUS["pill"], padx=10, pady=3, **kw)

def scrollable(parent, **kw):
    d = dict(fg_color="transparent",
             scrollbar_button_color=COLORS["border"],
             scrollbar_button_hover_color=COLORS["accent"])
    d.update(kw); return ctk.CTkScrollableFrame(parent, **d)

def topbar(parent, height=68):
    return ctk.CTkFrame(parent, fg_color=COLORS["bg_card"],
                        corner_radius=0, height=height,
                        border_width=1, border_color=COLORS["border"])

def format_currency(amount: float) -> str:
    a = abs(amount)
    if a >= 1_000_000_000: return f"Rp {a/1_000_000_000:.1f}M"
    if a >= 1_000_000:     return f"Rp {a/1_000_000:.1f}Jt"
    return f"Rp {a:,.0f}".replace(",", ".")

def format_currency_full(amount: float) -> str:
    return f"Rp {abs(amount):,.0f}".replace(",", ".")
