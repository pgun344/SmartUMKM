# dashboard.py — Premium Dashboard v2
import tkinter as tk
import customtkinter as ctk
from datetime import date
from style import *
import database as db


class DashboardPage(ctk.CTkFrame):
    def __init__(self, parent, navigate_fn, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg_primary"], **kwargs)
        self.navigate_fn = navigate_fn
        self._build_ui()

    def on_show(self):
        self._refresh()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # ── Top bar ──────────────────────────────────────────────
        tb = topbar(self)
        tb.grid(row=0, column=0, sticky="ew")
        tb.columnconfigure(1, weight=1)
        tb.grid_propagate(False)

        left = ctk.CTkFrame(tb, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w",
                  padx=SPACING["2xl"], pady=SPACING["md"])
        self.lbl_greet = label(left, "Selamat Datang 👋",
                                style="caption",
                                color=COLORS["text_secondary"])
        self.lbl_greet.pack(anchor="w")
        self.lbl_biz = label(left, "UMKM Saya", style="title")
        self.lbl_biz.pack(anchor="w")

        right = ctk.CTkFrame(tb, fg_color="transparent")
        right.grid(row=0, column=2, sticky="e",
                   padx=SPACING["2xl"])
        muted_label(right, "Periode:", style="small").pack(
            side="left", padx=(0, SPACING["sm"]))
        months = self._month_opts()
        self.sel_month = tk.StringVar(value=months[0])
        self.combo_period = styled_combo(
            right, values=months, variable=self.sel_month,
            width=170, command=lambda v: self._refresh())
        self.combo_period.pack(side="left")
        primary_button(right, text="  ＋  Transaksi Baru  ",
                        height=38,
                        command=lambda: self.navigate_fn("transaction")).pack(
            side="left", padx=(SPACING["lg"], 0))

        # ── Scrollable body ──────────────────────────────────────
        body = scrollable(self)
        body.grid(row=1, column=0, sticky="nsew")
        body.columnconfigure(0, weight=1)

        wrap = ctk.CTkFrame(body, fg_color="transparent")
        wrap.pack(fill="x", padx=SPACING["2xl"], pady=SPACING["xl"])
        wrap.columnconfigure((0,1,2,3), weight=1)

        # ── KPI row ──────────────────────────────────────────────
        self.kpi = {}
        kpi_cfg = [
            ("saldo",   "💳", "Total Saldo",    COLORS["accent"],   COLORS["accent_soft"]),
            ("income",  "📈", "Pendapatan",     COLORS["success"],  COLORS["success_soft"]),
            ("expense", "📉", "Pengeluaran",    COLORS["danger"],   COLORS["danger_soft"]),
            ("profit",  "💰", "Laba Bersih",    COLORS["info"],     COLORS["info_soft"]),
        ]
        for col, (key, ico, title, color, soft) in enumerate(kpi_cfg):
            c = card_frame(wrap)
            c.grid(row=0, column=col, sticky="nsew",
                   padx=(0, SPACING["md"]) if col < 3 else 0,
                   pady=(0, SPACING["xl"]))
            self.kpi[key] = self._kpi_card(c, ico, title, color, soft)

        # ── Charts ───────────────────────────────────────────────
        ch_row = ctk.CTkFrame(wrap, fg_color="transparent")
        ch_row.grid(row=1, column=0, columnspan=4, sticky="ew",
                    pady=(0, SPACING["xl"]))
        ch_row.columnconfigure(0, weight=3)
        ch_row.columnconfigure(1, weight=2)

        self._build_trend(ch_row)
        self._build_donut(ch_row)

        # ── Bottom ───────────────────────────────────────────────
        bot = ctk.CTkFrame(wrap, fg_color="transparent")
        bot.grid(row=2, column=0, columnspan=4, sticky="ew")
        bot.columnconfigure(0, weight=3)
        bot.columnconfigure(1, weight=2)

        self._build_recent(bot)
        self._build_accounts_summary(bot)

    # ── KPI card ─────────────────────────────────────────────────

    def _kpi_card(self, parent, ico, title, color, soft):
        inner = ctk.CTkFrame(parent, fg_color="transparent")
        inner.pack(fill="both", expand=True,
                   padx=SPACING["xl"], pady=SPACING["xl"])

        # Top row: icon + title
        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.pack(fill="x")

        ico_bg = ctk.CTkFrame(top, width=42, height=42,
                               corner_radius=12, fg_color=soft)
        ico_bg.pack(side="left", padx=(0, SPACING["md"]))
        ico_bg.pack_propagate(False)
        ctk.CTkLabel(ico_bg, text=ico,
                     font=("Segoe UI", 18)).place(
            relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(top, text=title, font=FONTS["small"],
                     text_color=COLORS["text_secondary"],
                     anchor="w").pack(side="left")

        # Amount
        lbl_val = ctk.CTkLabel(inner, text="Rp 0",
                                font=FONTS["number_md"],
                                text_color=color)
        lbl_val.pack(anchor="w", pady=(SPACING["sm"], SPACING["xs"]))

        # Progress bar
        bar_bg = ctk.CTkFrame(inner, height=3, corner_radius=2,
                               fg_color=soft)
        bar_bg.pack(fill="x")
        bar_fg = ctk.CTkFrame(bar_bg, height=3, corner_radius=2,
                               fg_color=color)
        bar_fg.place(relx=0, rely=0, relwidth=0.0, relheight=1.0)

        return {"value": lbl_val, "bar": bar_fg, "color": color}

    # ── Trend chart ──────────────────────────────────────────────

    def _build_trend(self, parent):
        c = card_frame(parent)
        c.grid(row=0, column=0, sticky="nsew",
               padx=(0, SPACING["md"]))
        inner = ctk.CTkFrame(c, fg_color="transparent")
        inner.pack(fill="both", expand=True,
                   padx=SPACING["xl"], pady=SPACING["xl"])

        hdr = ctk.CTkFrame(inner, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, SPACING["md"]))
        label(hdr, "Tren Pertumbuhan Bisnis", style="subtitle").pack(side="left")

        leg = ctk.CTkFrame(hdr, fg_color="transparent")
        leg.pack(side="right")
        for col, txt in [(COLORS["success"], "Pendapatan"),
                         (COLORS["danger"],  "Pengeluaran"),
                         (COLORS["accent"],  "Laba")]:
            dot = ctk.CTkFrame(leg, width=8, height=8,
                                corner_radius=4, fg_color=col)
            dot.pack(side="left", padx=(SPACING["md"], 3))
            dot.pack_propagate(False)
            muted_label(leg, txt, style="caption").pack(side="left")

        self.trend_canvas = tk.Canvas(
            inner, height=210,
            bg=COLORS["bg_card"], highlightthickness=0)
        self.trend_canvas.pack(fill="x")

    # ── Donut chart ──────────────────────────────────────────────

    def _build_donut(self, parent):
        c = card_frame(parent)
        c.grid(row=0, column=1, sticky="nsew")
        inner = ctk.CTkFrame(c, fg_color="transparent")
        inner.pack(fill="both", expand=True,
                   padx=SPACING["xl"], pady=SPACING["xl"])

        label(inner, "Kategori Pendapatan", style="subtitle").pack(anchor="w")
        muted_label(inner, "bulan ini", style="caption").pack(
            anchor="w", pady=(2, SPACING["md"]))

        self.donut_canvas = tk.Canvas(
            inner, width=150, height=150,
            bg=COLORS["bg_card"], highlightthickness=0)
        self.donut_canvas.pack()

        self.donut_legend = ctk.CTkFrame(inner, fg_color="transparent")
        self.donut_legend.pack(fill="x", pady=(SPACING["sm"], 0))

    # ── Recent transactions ──────────────────────────────────────

    def _build_recent(self, parent):
        c = card_frame(parent)
        c.grid(row=0, column=0, sticky="nsew",
               padx=(0, SPACING["md"]))
        c.columnconfigure(0, weight=1)

        hdr = ctk.CTkFrame(c, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew",
                 padx=SPACING["xl"], pady=(SPACING["xl"], SPACING["sm"]))
        label(hdr, "Transaksi Terbaru", style="subtitle").pack(side="left")
        secondary_button(
            hdr, text="Lihat Semua  →", height=32,
            command=lambda: self.navigate_fn("transaction")).pack(side="right")

        self.recent_wrap = ctk.CTkFrame(c, fg_color="transparent")
        self.recent_wrap.grid(row=1, column=0, sticky="ew",
                               padx=SPACING["xl"],
                               pady=(0, SPACING["xl"]))
        self.recent_wrap.columnconfigure(0, weight=1)

    # ── Accounts summary ─────────────────────────────────────────

    def _build_accounts_summary(self, parent):
        c = card_frame(parent)
        c.grid(row=0, column=1, sticky="nsew")
        c.columnconfigure(0, weight=1)

        hdr = ctk.CTkFrame(c, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew",
                 padx=SPACING["xl"], pady=(SPACING["xl"], SPACING["sm"]))
        label(hdr, "Rekening", style="subtitle").pack(side="left")
        secondary_button(
            hdr, text="Kelola  →", height=32,
            command=lambda: self.navigate_fn("account")).pack(side="right")

        self.acc_wrap = ctk.CTkFrame(c, fg_color="transparent")
        self.acc_wrap.grid(row=1, column=0, sticky="ew",
                            padx=SPACING["xl"],
                            pady=(0, SPACING["xl"]))
        self.acc_wrap.columnconfigure(0, weight=1)

    # ── Data ─────────────────────────────────────────────────────

    def _month_opts(self):
        today = date.today(); opts = []
        for i in range(12):
            m = today.month - i
            y = today.year
            while m <= 0: m += 12; y -= 1
            opts.append(f"{y}-{m:02d}")
        return opts

    def _refresh(self):
        biz = db.get_setting("business_name", "UMKM Saya")
        self.lbl_biz.configure(text=biz)

        month = self.sel_month.get()[:7]
        s     = db.get_summary(month)
        accs  = db.get_accounts()
        saldo = sum(a["balance"] for a in accs)

        vals = {"saldo": saldo, "income": s["income"],
                "expense": s["expense"], "profit": s["profit"]}
        maxv = max(abs(v) for v in vals.values()) or 1
        for key, val in vals.items():
            self.kpi[key]["value"].configure(
                text=format_currency(val),
                text_color=self.kpi[key]["color"]
                if val >= 0 else COLORS["danger"])
            w = max(0.05, min(1.0, abs(val) / maxv))
            self.kpi[key]["bar"].place(relwidth=w, relheight=1.0)

        self.after(80, self._draw_trend)
        self._draw_donut(month)
        self._draw_recent()
        self._draw_accs(accs)

    def _draw_trend(self):
        c = self.trend_canvas; c.delete("all"); c.update_idletasks()
        W = c.winfo_width() or 480; H = 210
        pl,pr,pt,pb = 48,16,20,36
        data = db.get_monthly_trend(6)
        if not data:
            c.create_text(W//2, H//2, text="Belum ada data",
                          fill=COLORS["text_muted"],
                          font=("Segoe UI", 12)); return

        max_v = max(max(d["income"], d["expense"]) for d in data) or 1
        cw = W-pl-pr; ch = H-pt-pb
        n  = len(data)
        step = cw/(n-1) if n > 1 else cw

        def y(v): return pt + ch - (v/max_v)*ch

        # Grid
        for i in range(5):
            yy = pt + ch/4*i
            v  = max_v*(1-i/4)
            c.create_line(pl, yy, W-pr, yy,
                          fill=COLORS["border_light"], width=1, dash=(3,4))
            lv = f"{v/1e6:.1f}jt" if v >= 1e6 else f"{v/1e3:.0f}k"
            c.create_text(pl-6, yy, text=lv,
                          fill=COLORS["text_muted"],
                          font=("Segoe UI", 8), anchor="e")

        inc_pts  = [(pl+i*step, y(d["income"]))  for i,d in enumerate(data)]
        exp_pts  = [(pl+i*step, y(d["expense"])) for i,d in enumerate(data)]
        laba_pts = [(pl+i*step, y(max(0, d["income"]-d["expense"])))
                    for i,d in enumerate(data)]

        # Filled income area
        if len(inc_pts) >= 2:
            poly = [pl, pt+ch]
            for px,py2 in inc_pts: poly += [px, py2]
            poly += [pl+cw, pt+ch]
            c.create_polygon(poly, fill=COLORS["success_soft"], outline="")

        # Lines
        for pts, col, w2 in [(inc_pts, COLORS["success"], 2),
                              (exp_pts, COLORS["danger"],  2),
                              (laba_pts,COLORS["accent"],  2)]:
            for i in range(len(pts)-1):
                c.create_line(*pts[i], *pts[i+1],
                              fill=col, width=w2, smooth=True)
            if pts:
                px,py2 = pts[-1]
                c.create_oval(px-4,py2-4,px+4,py2+4,
                              fill=col, outline=COLORS["bg_card"], width=2)

        # X labels
        for i, d in enumerate(data):
            mo = d.get("month","")
            lb = f"{mo[-2:]}/{mo[:4][2:]}" if len(mo)>=7 else mo
            c.create_text(pl+i*step, H-14, text=lb,
                          fill=COLORS["text_muted"],
                          font=("Segoe UI", 8))

    def _draw_donut(self, month):
        c = self.donut_canvas; c.delete("all")
        for w in self.donut_legend.winfo_children(): w.destroy()

        cats = db.get_category_breakdown("income", month)
        if not cats:
            c.create_text(75, 75, text="Tidak ada\ndata",
                          fill=COLORS["text_muted"],
                          font=("Segoe UI",10), justify="center"); return

        total  = sum(d["total"] or 0 for d in cats) or 1
        pal    = [COLORS["success"], COLORS["accent"], COLORS["warning"],
                  COLORS["info"], COLORS["danger"], "#A78BFA"]
        start  = -90
        cx,cy,r,ri = 75, 75, 64, 38

        for i,d in enumerate(cats[:6]):
            pct = (d["total"] or 0)/total
            deg = pct*360
            col = pal[i % len(pal)]
            c.create_arc(cx-r, cy-r, cx+r, cy+r,
                         start=start, extent=deg,
                         fill=col, outline=COLORS["bg_card"], width=3)
            start += deg

        c.create_oval(cx-ri,cy-ri,cx+ri,cy+ri,
                      fill=COLORS["bg_card"], outline="")
        s = db.get_summary(month)
        c.create_text(cx, cy-9, text=format_currency(s["income"]),
                      fill=COLORS["text_primary"],
                      font=("Segoe UI",9,"bold"))
        c.create_text(cx, cy+9, text="pendapatan",
                      fill=COLORS["text_muted"],
                      font=("Segoe UI",7))

        for i,d in enumerate(cats[:5]):
            col = pal[i % len(pal)]
            row = ctk.CTkFrame(self.donut_legend, fg_color="transparent")
            row.pack(fill="x", pady=1)
            dot = ctk.CTkFrame(row, width=8, height=8,
                                corner_radius=4, fg_color=col)
            dot.pack(side="left", padx=(0,4)); dot.pack_propagate(False)
            nm  = (d.get("name") or d.get("cat_name") or "?")[:14]
            ico = d.get("icon") or d.get("cat_icon") or ""
            ctk.CTkLabel(row, text=f"{ico} {nm}",
                         font=FONTS["caption"],
                         text_color=COLORS["text_secondary"],
                         anchor="w").pack(side="left")
            pct = (d["total"] or 0)/total*100
            ctk.CTkLabel(row, text=f"{pct:.0f}%",
                         font=FONTS["caption_bold"],
                         text_color=col).pack(side="right")

    def _draw_recent(self):
        for w in self.recent_wrap.winfo_children(): w.destroy()
        txns = db.get_transactions(limit=5)
        if not txns:
            ph = elevated_frame(self.recent_wrap, corner_radius=RADIUS["lg"])
            ph.pack(fill="x", pady=SPACING["xl"])
            muted_label(ph, "Belum ada transaksi  ·  Tekan '＋ Transaksi Baru'",
                        style="small").pack(pady=SPACING["xl"]); return
        for i,t in enumerate(txns):
            self._recent_row(t, i)

    def _recent_row(self, t, idx):
        is_in = t["type"] == "income"
        color = COLORS["success"] if is_in else COLORS["danger"]
        soft  = COLORS["success_soft"] if is_in else COLORS["danger_soft"]
        sign  = "+" if is_in else "−"

        row = ctk.CTkFrame(
            self.recent_wrap,
            fg_color=COLORS["bg_elevated"] if idx%2 else "transparent",
            corner_radius=RADIUS["md"])
        row.pack(fill="x", pady=2)
        row.columnconfigure(1, weight=1)

        ico_f = ctk.CTkFrame(row, width=38, height=38,
                              corner_radius=10, fg_color=soft)
        ico_f.grid(row=0, column=0, rowspan=2,
                   padx=(SPACING["md"],SPACING["sm"]),
                   pady=SPACING["sm"])
        ico_f.pack_propagate(False)
        ctk.CTkLabel(ico_f,
                     text=t.get("cat_icon") or ("💰" if is_in else "💸"),
                     font=("Segoe UI",14)).place(
            relx=0.5, rely=0.5, anchor="center")

        label(row, t.get("description") or "—",
              style="body_bold").grid(row=0, column=1, sticky="w")
        muted_label(row,
                    f"{t.get('cat_name','?')}  ·  {t['date']}",
                    style="caption").grid(row=1, column=1, sticky="w")

        ctk.CTkLabel(row, text=f"{sign} {format_currency(t['amount'])}",
                     font=FONTS["body_bold"],
                     text_color=color).grid(
            row=0, column=2, rowspan=2, padx=SPACING["md"])

    def _draw_accs(self, accs):
        for w in self.acc_wrap.winfo_children(): w.destroy()
        if not accs:
            ph = elevated_frame(self.acc_wrap, corner_radius=RADIUS["lg"])
            ph.pack(fill="x")
            muted_label(ph,"Belum ada rekening",
                        style="small").pack(pady=SPACING["xl"]); return
        for acc in accs[:5]:
            row = ctk.CTkFrame(self.acc_wrap, fg_color="transparent")
            row.pack(fill="x", pady=3)
            row.columnconfigure(1, weight=1)

            ic = ctk.CTkFrame(row, width=36, height=36,
                               corner_radius=10,
                               fg_color=acc.get("color",COLORS["accent"])+"44" if False
                               else COLORS["accent_soft"])
            ic.grid(row=0, column=0, padx=(0,SPACING["sm"]))
            ic.pack_propagate(False)
            ctk.CTkLabel(ic, text=acc.get("icon","🏦"),
                         font=("Segoe UI",14)).place(
                relx=0.5, rely=0.5, anchor="center")

            label(row, acc["name"], style="body_bold").grid(
                row=0, column=1, sticky="w")
            muted_label(row, acc.get("type",""),
                        style="caption").grid(row=1, column=1, sticky="w")

            bc = COLORS["success"] if acc["balance"] >= 0 else COLORS["danger"]
            ctk.CTkLabel(row, text=format_currency(acc["balance"]),
                         font=FONTS["body_bold"],
                         text_color=bc).grid(
                row=0, column=2, rowspan=2, padx=(SPACING["sm"],0))

            divider(self.acc_wrap).pack(fill="x", pady=2)
