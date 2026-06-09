# insight.py — Premium v2
import tkinter as tk
import customtkinter as ctk
from datetime import date
from style import *
import database as db


class InsightPage(ctk.CTkFrame):
    def __init__(self, parent, navigate_fn, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg_primary"], **kwargs)
        self.navigate_fn = navigate_fn
        self._build_ui()

    def on_show(self):
        self._refresh()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Top bar
        tb = topbar(self)
        tb.grid(row=0, column=0, sticky="ew")
        tb.columnconfigure(1, weight=1)
        tb.grid_propagate(False)

        left = ctk.CTkFrame(tb, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w",
                  padx=SPACING["2xl"], pady=SPACING["md"])
        label(left, "Insight & Analitik", style="title").pack(anchor="w")
        muted_label(left, "Analisis mendalam keuangan bisnis Anda",
                    style="caption").pack(anchor="w")

        right = ctk.CTkFrame(tb, fg_color="transparent")
        right.grid(row=0, column=2, sticky="e", padx=SPACING["2xl"])
        muted_label(right, "Periode:", style="small").pack(
            side="left", padx=(0,SPACING["sm"]))
        months = self._month_opts()
        self.sel_month = tk.StringVar(value=months[0])
        combo = styled_combo(right, values=months, variable=self.sel_month,
                              width=170, command=lambda v: self._refresh())
        combo.set(months[0]); combo.pack(side="left")

        # Scrollable body
        body = scrollable(self)
        body.grid(row=1, column=0, sticky="nsew")
        body.columnconfigure(0, weight=1)

        wrap = ctk.CTkFrame(body, fg_color="transparent")
        wrap.pack(fill="x", padx=SPACING["2xl"], pady=SPACING["xl"])
        wrap.columnconfigure(0, weight=1)

        # KPI row
        kr = ctk.CTkFrame(wrap, fg_color="transparent")
        kr.pack(fill="x", pady=(0, SPACING["xl"]))
        for i in range(3): kr.columnconfigure(i, weight=1)

        self.kpi = {}
        for col, (key, ico, title, color, soft) in enumerate([
            ("margin",  "📊", "Margin Laba",               COLORS["accent"],  COLORS["accent_soft"]),
            ("avg_in",  "📈", "Rata-rata Transaksi Masuk",  COLORS["success"], COLORS["success_soft"]),
            ("avg_out", "📉", "Rata-rata Transaksi Keluar", COLORS["danger"],  COLORS["danger_soft"]),
        ]):
            c = card_frame(kr)
            c.grid(row=0, column=col, sticky="nsew",
                   padx=(0,SPACING["md"]) if col<2 else 0)
            inner = ctk.CTkFrame(c, fg_color="transparent")
            inner.pack(fill="both", padx=SPACING["xl"], pady=SPACING["xl"])

            ibg = ctk.CTkFrame(inner, width=40, height=40,
                                corner_radius=10, fg_color=soft)
            ibg.pack(side="left", padx=(0,SPACING["md"]))
            ibg.pack_propagate(False)
            ctk.CTkLabel(ibg, text=ico, font=("Segoe UI",18)).place(
                relx=0.5, rely=0.5, anchor="center")

            txt = ctk.CTkFrame(inner, fg_color="transparent")
            txt.pack(side="left")
            muted_label(txt, title, style="caption").pack(anchor="w")
            lbl = ctk.CTkLabel(txt, text="—", font=FONTS["number_md"],
                                text_color=color)
            lbl.pack(anchor="w")
            self.kpi[key] = lbl

        # Trend chart
        tc = card_frame(wrap)
        tc.pack(fill="x", pady=(0, SPACING["xl"]))
        ti = ctk.CTkFrame(tc, fg_color="transparent")
        ti.pack(fill="both", padx=SPACING["xl"], pady=SPACING["xl"])

        hdr = ctk.CTkFrame(ti, fg_color="transparent"); hdr.pack(fill="x")
        label(hdr, "Tren Arus Kas 6 Bulan", style="subtitle").pack(side="left")
        leg = ctk.CTkFrame(hdr, fg_color="transparent"); leg.pack(side="right")
        for col, txt in [(COLORS["success"],"Pendapatan"),
                         (COLORS["danger"],"Pengeluaran")]:
            dot = ctk.CTkFrame(leg,width=8,height=8,corner_radius=4,fg_color=col)
            dot.pack(side="right",padx=(SPACING["md"],2)); dot.pack_propagate(False)
            muted_label(leg,txt,style="caption").pack(side="right")

        self.cashflow_canvas = tk.Canvas(ti, height=230,
                                          bg=COLORS["bg_card"],
                                          highlightthickness=0)
        self.cashflow_canvas.pack(fill="x", pady=(SPACING["sm"],0))

        # Breakdown row
        br = ctk.CTkFrame(wrap, fg_color="transparent")
        br.pack(fill="x", pady=(0, SPACING["xl"]))
        br.columnconfigure(0, weight=1); br.columnconfigure(1, weight=1)

        # Income breakdown
        ic = card_frame(br)
        ic.grid(row=0, column=0, sticky="nsew",
                padx=(0,SPACING["md"]))
        ii = ctk.CTkFrame(ic, fg_color="transparent")
        ii.pack(fill="both", padx=SPACING["xl"], pady=SPACING["xl"])
        label(ii, "Sumber Pendapatan", style="subtitle").pack(anchor="w")
        muted_label(ii,"bulan ini",style="caption").pack(
            anchor="w", pady=(2,SPACING["md"]))
        self.inc_list = scrollable(ii, height=230)
        self.inc_list.pack(fill="x")

        # Expense breakdown
        ec = card_frame(br)
        ec.grid(row=0, column=1, sticky="nsew")
        ei = ctk.CTkFrame(ec, fg_color="transparent")
        ei.pack(fill="both", padx=SPACING["xl"], pady=SPACING["xl"])
        label(ei, "Rincian Pengeluaran", style="subtitle").pack(anchor="w")
        muted_label(ei,"per kategori bulan ini",style="caption").pack(
            anchor="w", pady=(2,SPACING["md"]))
        # Table header
        th = ctk.CTkFrame(ei, fg_color=COLORS["bg_elevated"],
                           corner_radius=RADIUS["sm"])
        th.pack(fill="x")
        for txt,side in [("Kategori","left"),("Jumlah","right"),("%","right")]:
            ctk.CTkLabel(th, text=txt, font=FONTS["caption_bold"],
                         text_color=COLORS["text_secondary"],
                         anchor="w" if side=="left" else "e").pack(
                side=side, padx=SPACING["sm"], pady=SPACING["sm"])
        self.exp_scroll = scrollable(ei, height=200)
        self.exp_scroll.pack(fill="x", pady=(SPACING["xs"],0))

        # Daily bars
        dc = card_frame(wrap)
        dc.pack(fill="x")
        di = ctk.CTkFrame(dc, fg_color="transparent")
        di.pack(fill="both", padx=SPACING["xl"], pady=SPACING["xl"])
        label(di, "Arus Kas Harian (14 Hari Terakhir)",
              style="subtitle").pack(anchor="w")
        muted_label(di,"  🟢 surplus    🔴 defisit",
                    style="caption").pack(anchor="w", pady=(2,SPACING["md"]))
        self.daily_canvas = tk.Canvas(di, height=160,
                                       bg=COLORS["bg_card"],
                                       highlightthickness=0)
        self.daily_canvas.pack(fill="x")

    def _month_opts(self):
        today = date.today(); opts = []
        for i in range(12):
            m = today.month - i; y = today.year
            while m <= 0: m += 12; y -= 1
            opts.append(f"{y}-{m:02d}")
        return opts

    def _refresh(self):
        month = self.sel_month.get()[:7]
        s     = db.get_summary(month)
        inc, exp = s["income"], s["expense"]
        profit   = s["profit"]

        margin = (profit/inc*100) if inc > 0 else 0
        self.kpi["margin"].configure(
            text=f"{margin:.1f}%",
            text_color=COLORS["success"] if margin>=0 else COLORS["danger"])

        it = db.get_transactions(type_="income",  month=month, limit=1000)
        et = db.get_transactions(type_="expense", month=month, limit=1000)
        self.kpi["avg_in"].configure(
            text=format_currency(inc/len(it) if it else 0))
        self.kpi["avg_out"].configure(
            text=format_currency(exp/len(et) if et else 0))

        self.after(80, self._draw_cashflow)
        self._draw_income(month)
        self._draw_expense(month)
        self.after(80, self._draw_daily)

    def _draw_cashflow(self):
        c = self.cashflow_canvas; c.delete("all"); c.update_idletasks()
        W = c.winfo_width() or 600; H = 230
        pl,pr,pt,pb = 50,16,22,36
        data = db.get_monthly_trend(6)
        if not data:
            c.create_text(W//2,H//2,text="Belum ada data",
                          fill=COLORS["text_muted"],font=("Segoe UI",12)); return
        max_v = max(max(d["income"],d["expense"]) for d in data) or 1
        n = len(data); cw=W-pl-pr; ch=H-pt-pb
        step = cw/(n-1) if n>1 else cw
        def y(v): return pt+ch-(v/max_v)*ch
        for i in range(5):
            yy=pt+ch/4*i; v=max_v*(1-i/4)
            c.create_line(pl,yy,W-pr,yy,fill=COLORS["border_light"],
                          width=1,dash=(3,5))
            lv=f"{v/1e6:.1f}jt" if v>=1e6 else f"{v/1e3:.0f}k"
            c.create_text(pl-6,yy,text=lv,fill=COLORS["text_muted"],
                          font=("Segoe UI",8),anchor="e")
        inc_pts=[(pl+i*step,y(d["income"]))  for i,d in enumerate(data)]
        exp_pts=[(pl+i*step,y(d["expense"])) for i,d in enumerate(data)]
        if len(inc_pts)>=2:
            poly=[pl,pt+ch]+[v2 for p in inc_pts for v2 in p]+[pl+cw,pt+ch]
            c.create_polygon(poly,fill=COLORS["success_soft"],outline="")
        for pts,col in [(inc_pts,COLORS["success"]),(exp_pts,COLORS["danger"])]:
            for i in range(len(pts)-1):
                c.create_line(*pts[i],*pts[i+1],fill=col,width=2,smooth=True)
            if pts:
                px,py2=pts[-1]
                c.create_oval(px-4,py2-4,px+4,py2+4,
                              fill=col,outline=COLORS["bg_card"],width=2)
        for i,d in enumerate(data):
            mo=d.get("month","")
            lb=f"{mo[-2:]}/{mo[:4][2:]}" if len(mo)>=7 else mo
            c.create_text(pl+i*step,H-14,text=lb,
                          fill=COLORS["text_muted"],font=("Segoe UI",8))

    def _draw_income(self, month):
        for w in self.inc_list.winfo_children(): w.destroy()
        cats = db.get_category_breakdown("income", month)
        if not cats:
            muted_label(self.inc_list,"Belum ada data",style="small").pack(
                pady=SPACING["xl"]); return
        total=sum(d["total"] or 0 for d in cats) or 1
        pal=[COLORS["success"],COLORS["accent"],COLORS["warning"],
             COLORS["info"],COLORS["danger"]]
        for i,d in enumerate(cats):
            pct=(d["total"] or 0)/total; col=pal[i%len(pal)]
            row=ctk.CTkFrame(self.inc_list,fg_color="transparent")
            row.pack(fill="x",pady=3)
            top=ctk.CTkFrame(row,fg_color="transparent"); top.pack(fill="x")
            ico=d.get("icon") or d.get("cat_icon") or ""
            nm=(d.get("name") or d.get("cat_name") or "?")[:16]
            ctk.CTkLabel(top,text=f"{ico} {nm}",font=FONTS["small"],
                         text_color=COLORS["text_primary"],anchor="w").pack(side="left")
            ctk.CTkLabel(top,text=f"{pct*100:.1f}%",font=FONTS["small_bold"],
                         text_color=col).pack(side="right")
            bg=ctk.CTkFrame(row,height=5,corner_radius=3,
                             fg_color=COLORS["bg_elevated"])
            bg.pack(fill="x",pady=(2,0))
            ctk.CTkFrame(bg,height=5,corner_radius=3,fg_color=col).place(
                relx=0,rely=0,relwidth=pct,relheight=1)
            muted_label(row,format_currency_full(d["total"] or 0),
                        style="caption").pack(anchor="w")

    def _draw_expense(self, month):
        for w in self.exp_scroll.winfo_children(): w.destroy()
        cats=db.get_category_breakdown("expense",month)
        if not cats:
            muted_label(self.exp_scroll,"Belum ada data",style="small").pack(
                pady=SPACING["xl"]); return
        total=sum(d["total"] or 0 for d in cats) or 1
        pal=[COLORS["danger"],COLORS["warning"],"#EC4899",
             COLORS["accent"],"#F97316"]
        for i,d in enumerate(cats):
            pct=(d["total"] or 0)/total*100; col=pal[i%len(pal)]
            row=ctk.CTkFrame(self.exp_scroll,
                              fg_color=COLORS["bg_elevated"] if i%2==0
                              else "transparent",
                              corner_radius=RADIUS["sm"])
            row.pack(fill="x",pady=1)
            dot=ctk.CTkFrame(row,width=8,height=8,corner_radius=4,fg_color=col)
            dot.pack(side="left",padx=(SPACING["sm"],4),pady=SPACING["sm"])
            dot.pack_propagate(False)
            ico=d.get("icon") or d.get("cat_icon") or ""
            nm=(d.get("name") or d.get("cat_name") or "?")[:16]
            ctk.CTkLabel(row,text=f"{ico} {nm}",font=FONTS["small"],
                         text_color=COLORS["text_primary"],anchor="w").pack(
                side="left",fill="x",expand=True)
            ctk.CTkLabel(row,text=format_currency(d["total"] or 0),
                         font=FONTS["small"],text_color=COLORS["text_secondary"],
                         anchor="e").pack(side="right",padx=(0,SPACING["xs"]))
            ctk.CTkLabel(row,text=f"{pct:.1f}%",font=FONTS["small_bold"],
                         text_color=col,width=40,anchor="e").pack(
                side="right",padx=(0,SPACING["sm"]))

    def _draw_daily(self):
        c=self.daily_canvas; c.delete("all"); c.update_idletasks()
        W=c.winfo_width() or 600; H=160
        data=db.get_daily_cashflow(14)
        if not data:
            c.create_text(W//2,H//2,text="Belum ada data",
                          fill=COLORS["text_muted"],font=("Segoe UI",11)); return
        pl,pr,pt,pb=10,10,20,28; ch=H-pt-pb; cw=W-pl-pr
        n=len(data); step=cw/n; bw=max(6,step*0.65)
        nets=[d["income"]-d["expense"] for d in data]
        mx=max(abs(v) for v in nets) or 1
        zero=pt+ch/2
        c.create_line(pl,zero,W-pr,zero,fill=COLORS["border_light"],
                      width=1,dash=(4,4))
        for i,(d,net) in enumerate(zip(data,nets)):
            cx=pl+i*step+step/2; bh=abs(net/mx)*(ch/2)
            col=COLORS["success"] if net>=0 else COLORS["danger"]
            y1=zero-bh if net>=0 else zero
            y2=zero     if net>=0 else zero+bh
            # Rounded bar effect
            c.create_rectangle(cx-bw/2,y1,cx+bw/2,y2,
                                fill=col,outline="")
            if i%3==0:
                c.create_text(cx,H-12,text=d["date"][-5:],
                               fill=COLORS["text_muted"],
                               font=("Segoe UI",7))
