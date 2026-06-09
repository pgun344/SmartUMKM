# transaction.py — Premium v2
# Modifikasi struktur halaman transaksi oleh Philip
import tkinter as tk
import customtkinter as ctk
from datetime import date, datetime
from style import *
import database as db


class TransactionPage(ctk.CTkFrame):
    def __init__(self, parent, navigate_fn, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg_primary"], **kwargs)
        self.navigate_fn = navigate_fn
        self._edit_id    = None
        self._active_tab = tk.StringVar(value="Semua")
        self._build_ui()

    def on_show(self):
        self._refresh_list()

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
        label(left, "Transaksi Keuangan", style="title").pack(anchor="w")
        muted_label(left,
                    "Kelola semua transaksi pendapatan dan pengeluaran",
                    style="caption").pack(anchor="w")

        right = ctk.CTkFrame(tb, fg_color="transparent")
        right.grid(row=0, column=2, sticky="e", padx=SPACING["2xl"])
        primary_button(right, text="  ＋  Tambah Transaksi  ",
                        command=self._open_dialog).pack(side="right")

        # ── Content ──────────────────────────────────────────────
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew",
                  padx=SPACING["2xl"], pady=SPACING["xl"])
        body.columnconfigure(0, weight=1)
        body.rowconfigure(2, weight=1)

        # Summary mini-cards
        sc = ctk.CTkFrame(body, fg_color="transparent")
        sc.grid(row=0, column=0, sticky="ew", pady=(0, SPACING["lg"]))
        for i in range(4): sc.columnconfigure(i, weight=1)

        self.sum_lbl = {}
        for col, (key, ico, title, color) in enumerate([
            ("income",  "📈", "Total Pendapatan",  COLORS["success"]),
            ("expense", "📉", "Total Pengeluaran", COLORS["danger"]),
            ("txn",     "🔢", "Total Transaksi",   COLORS["accent"]),
            ("period",  "📅", "Periode",           COLORS["info"]),
        ]):
            c = card_frame(sc)
            c.grid(row=0, column=col, sticky="nsew",
                   padx=(0,SPACING["md"]) if col<3 else 0)
            row = ctk.CTkFrame(c, fg_color="transparent")
            row.pack(fill="both", padx=SPACING["lg"], pady=SPACING["md"])

            ibg = ctk.CTkFrame(row, width=34, height=34,
                                corner_radius=8,
                                fg_color=COLORS.get(f"{key}_soft",
                                                    COLORS["accent_soft"]))
            ibg.pack(side="left", padx=(0,SPACING["sm"]))
            ibg.pack_propagate(False)
            ctk.CTkLabel(ibg, text=ico,
                         font=("Segoe UI",14)).place(
                relx=0.5, rely=0.5, anchor="center")

            txt = ctk.CTkFrame(row, fg_color="transparent")
            txt.pack(side="left")
            muted_label(txt, title, style="caption").pack(anchor="w")
            lbl = ctk.CTkLabel(txt, text="—", font=FONTS["number_md"],
                                text_color=color)
            lbl.pack(anchor="w")
            self.sum_lbl[key] = lbl

        # Filter bar
        fb = card_frame(body)
        fb.grid(row=1, column=0, sticky="ew", pady=(0,SPACING["md"]))
        bar = ctk.CTkFrame(fb, fg_color="transparent")
        bar.pack(fill="x", padx=SPACING["lg"], pady=SPACING["sm"])

        # Tab buttons
        tab_bg = ctk.CTkFrame(bar, fg_color=COLORS["bg_elevated"],
                               corner_radius=RADIUS["md"])
        tab_bg.pack(side="left", padx=(0,SPACING["md"]))
        self._tab_btns = {}
        for txt in ["Semua","Pendapatan","Pengeluaran"]:
            b = ctk.CTkButton(
                tab_bg, text=txt, height=32, width=100,
                fg_color=COLORS["accent"] if txt=="Semua" else "transparent",
                text_color=COLORS["text_primary"] if txt=="Semua"
                           else COLORS["text_secondary"],
                hover_color=COLORS["accent_hover"] if txt=="Semua"
                            else COLORS["bg_hover"],
                corner_radius=RADIUS["sm"], font=FONTS["small"],
                command=lambda t=txt: self._set_tab(t))
            b.pack(side="left", padx=2, pady=2)
            self._tab_btns[txt] = b

        self.ent_search = styled_entry(
            bar, placeholder_text="🔍  Cari transaksi...", width=210, height=36)
        self.ent_search.pack(side="left", padx=(0,SPACING["sm"]))
        self.ent_search.bind("<KeyRelease>", lambda e: self._refresh_list())

        months = self._month_opts()
        self.combo_month = styled_combo(
            bar, values=["Semua Bulan"]+months,
            width=155, height=36,
            command=lambda v: self._refresh_list())
        self.combo_month.set("Semua Bulan")
        self.combo_month.pack(side="left")

        danger_button(bar, text="🗑  Hapus Semua", height=36,
                      command=self._confirm_delete_all).pack(side="right")

        # List card
        lc = card_frame(body)
        lc.grid(row=2, column=0, sticky="nsew")
        lc.columnconfigure(0, weight=1)
        lc.rowconfigure(1, weight=1)

        # Table header
        th = ctk.CTkFrame(lc, fg_color=COLORS["bg_elevated"],
                           corner_radius=0)
        th.grid(row=0, column=0, sticky="ew",
                padx=2, pady=(2,0))
        th.columnconfigure(1, weight=1)
        for ci, (txt, anchor) in enumerate([
            ("", "w"),("Keterangan","w"),("Kategori","center"),
            ("Tanggal","center"),("Jumlah","e"),("Aksi","center")
        ]):
            ctk.CTkLabel(th, text=txt, font=FONTS["caption_bold"],
                         text_color=COLORS["text_secondary"],
                         anchor=anchor).grid(
                row=0, column=ci,
                sticky="ew" if ci==1 else "",
                padx=SPACING["sm"], pady=SPACING["sm"])

        self.scroll_list = scrollable(lc)
        self.scroll_list.grid(row=1, column=0, sticky="nsew",
                               padx=2, pady=(0,2))
        self.scroll_list.columnconfigure(0, weight=1)

    # ── Tab ──────────────────────────────────────────────────────

    def _set_tab(self, tab):
        self._active_tab.set(tab)
        for txt, b in self._tab_btns.items():
            on = txt == tab
            b.configure(
                fg_color=COLORS["accent"] if on else "transparent",
                text_color=COLORS["text_primary"] if on
                           else COLORS["text_secondary"],
                hover_color=COLORS["accent_hover"] if on
                            else COLORS["bg_hover"])
        self._refresh_list()

    # ── Dialog ───────────────────────────────────────────────────

    def _open_dialog(self, txn=None):
        self._edit_id = txn["id"] if txn else None
        dlg = ctk.CTkToplevel(self)
        dlg.title("Edit Transaksi" if txn else "Tambah Transaksi")
        dlg.geometry("500x640")
        dlg.resizable(False, True)
        dlg.configure(fg_color=COLORS["bg_card"])
        dlg.grab_set(); dlg.lift()

        # Header stripe
        ctk.CTkFrame(dlg, height=4, corner_radius=0,
                     fg_color=COLORS["accent"]).pack(fill="x")

        # Title
        label(dlg,
              "Edit Transaksi" if txn else "Tambah Transaksi Baru",
              style="subtitle").pack(
            anchor="w", padx=SPACING["2xl"],
            pady=(SPACING["xl"], SPACING["sm"]))

        # Type toggle
        type_var = tk.StringVar(value=txn["type"] if txn else "income")
        tbar = ctk.CTkFrame(dlg, fg_color=COLORS["bg_elevated"],
                             corner_radius=RADIUS["md"])
        tbar.pack(fill="x", padx=SPACING["2xl"],
                  pady=(0, SPACING["md"]))
        tbar.columnconfigure((0,1), weight=1)

        def set_type(t):
            type_var.set(t)
            btn_in.configure(
                fg_color=COLORS["success"] if t=="income" else "transparent",
                text_color="#FFF" if t=="income" else COLORS["text_secondary"])
            btn_ex.configure(
                fg_color=COLORS["danger"] if t=="expense" else "transparent",
                text_color="#FFF" if t=="expense" else COLORS["text_secondary"])
            _reload_cats()

        btn_in = ctk.CTkButton(
            tbar, text="✅  Pendapatan", height=36,
            fg_color=COLORS["success"] if (not txn or txn["type"]=="income")
                     else "transparent",
            text_color="#FFF" if (not txn or txn["type"]=="income")
                       else COLORS["text_secondary"],
            hover_color=COLORS["success"],
            corner_radius=RADIUS["sm"], font=FONTS["body_bold"],
            command=lambda: set_type("income"))
        btn_in.grid(row=0, column=0, padx=3, pady=3, sticky="ew")

        btn_ex = ctk.CTkButton(
            tbar, text="❌  Pengeluaran", height=36,
            fg_color=COLORS["danger"] if (txn and txn["type"]=="expense")
                     else "transparent",
            text_color="#FFF" if (txn and txn["type"]=="expense")
                       else COLORS["text_secondary"],
            hover_color=COLORS["danger"],
            corner_radius=RADIUS["sm"], font=FONTS["body_bold"],
            command=lambda: set_type("expense"))
        btn_ex.grid(row=0, column=1, padx=3, pady=3, sticky="ew")

        # Scrollable form
        sa = scrollable(dlg)
        sa.pack(fill="both", expand=True, padx=SPACING["2xl"])
        sa.columnconfigure(0, weight=1)

        def fld(r, t):
            muted_label(sa, t, style="small").grid(
                row=r, column=0, sticky="w", pady=(0,2))

        fld(0, "Tanggal (YYYY-MM-DD)")
        e_date = styled_entry(sa, placeholder_text="2026-01-01")
        e_date.grid(row=1, column=0, sticky="ew", pady=(0,SPACING["sm"]))
        e_date.insert(0, txn["date"] if txn else date.today().isoformat())

        fld(2, "Jumlah (Rp)")
        e_amt = styled_entry(sa, placeholder_text="500000")
        e_amt.grid(row=3, column=0, sticky="ew", pady=(0,SPACING["sm"]))
        if txn: e_amt.insert(0, str(int(txn["amount"])))

        fld(4, "Keterangan")
        e_desc = styled_entry(sa, placeholder_text="Deskripsi singkat")
        e_desc.grid(row=5, column=0, sticky="ew", pady=(0,SPACING["sm"]))
        if txn: e_desc.insert(0, txn.get("description") or "")

        fld(6, "Kategori")
        cats    = db.get_categories(type_var.get())
        cat_map = {f"{c['icon']} {c['name']}": c["id"] for c in cats}
        combo_cat = styled_combo(sa, values=list(cat_map.keys()) or ["—"])
        combo_cat.grid(row=7, column=0, sticky="ew", pady=(0,SPACING["sm"]))
        if txn:
            for k,v in cat_map.items():
                if v == txn.get("category_id"): combo_cat.set(k); break
        elif cat_map: combo_cat.set(list(cat_map.keys())[0])

        def _reload_cats():
            nonlocal cat_map
            cats2 = db.get_categories(type_var.get())
            cat_map = {f"{c['icon']} {c['name']}": c["id"] for c in cats2}
            combo_cat.configure(values=list(cat_map.keys()) or ["—"])
            if cat_map: combo_cat.set(list(cat_map.keys())[0])

        fld(8, "Akun")
        accs    = db.get_accounts()
        acc_map = {f"{a['icon']} {a['name']}": a["id"] for a in accs}
        combo_acc = styled_combo(
            sa, values=list(acc_map.keys()) or ["— Buat akun dulu —"])
        combo_acc.grid(row=9, column=0, sticky="ew", pady=(0,SPACING["sm"]))
        if txn:
            for k,v in acc_map.items():
                if v == txn.get("account_id"): combo_acc.set(k); break
        elif acc_map: combo_acc.set(list(acc_map.keys())[0])

        lbl_err = ctk.CTkLabel(sa, text="",
                                text_color=COLORS["danger"],
                                font=FONTS["small"], anchor="w")
        lbl_err.grid(row=10, column=0, sticky="w", pady=(0,SPACING["sm"]))

        def _save():
            try: datetime.strptime(e_date.get().strip(), "%Y-%m-%d")
            except ValueError:
                lbl_err.configure(text="❌ Format tanggal: YYYY-MM-DD"); return
            try:
                amt = float(e_amt.get().replace(".","").replace(",",""))
                if amt <= 0: raise ValueError
            except ValueError:
                lbl_err.configure(text="❌ Jumlah harus angka positif"); return
            if combo_cat.get() not in cat_map:
                lbl_err.configure(text="❌ Pilih kategori yang valid"); return
            if combo_acc.get() not in acc_map:
                lbl_err.configure(
                    text="❌ Pilih akun  (buat akun dulu di menu Profil)"); return

            if self._edit_id:
                db.update_transaction(
                    self._edit_id, e_date.get().strip(),
                    type_var.get(), amt,
                    cat_map[combo_cat.get()],
                    acc_map[combo_acc.get()],
                    e_desc.get().strip())
            else:
                db.add_transaction(
                    e_date.get().strip(), type_var.get(), amt,
                    cat_map[combo_cat.get()],
                    acc_map[combo_acc.get()],
                    e_desc.get().strip())
            dlg.destroy()
            self._refresh_list()

        # Fixed bottom buttons
        btn_out = ctk.CTkFrame(dlg, fg_color=COLORS["bg_card"], height=72)
        btn_out.pack(fill="x", padx=SPACING["2xl"],
                     pady=(SPACING["sm"], SPACING["xl"]))
        btn_out.pack_propagate(False)
        primary_button(btn_out, text="  💾  Simpan  ",
                        command=_save).pack(
            side="left", fill="x", expand=True,
            padx=(0,SPACING["sm"]))
        secondary_button(btn_out, text="  ✖  Batal  ",
                          command=dlg.destroy).pack(
            side="left", fill="x", expand=True)

    # ── Helpers ──────────────────────────────────────────────────

    def _month_opts(self):
        today = date.today(); opts = []
        for i in range(12):
            m = today.month - i; y = today.year
            while m <= 0: m += 12; y -= 1
            opts.append(f"{y}-{m:02d}")
        return opts

    def _confirm_delete_all(self):
        if not db.get_transactions(limit=1): return
        self._confirm_dlg(
            "Hapus SEMUA transaksi?",
            "Semua saldo akun akan direset ke 0. Tidak bisa dibatalkan.",
            lambda: [db.delete_all_transactions(), self._refresh_list()])

    def _delete_txn(self, id_):
        self._confirm_dlg(
            "Hapus transaksi ini?",
            "Saldo akun akan disesuaikan kembali.",
            lambda: [db.delete_transaction(id_), self._refresh_list()])

    def _confirm_dlg(self, title, subtitle, on_ok):
        dlg = ctk.CTkToplevel(self)
        dlg.title("Konfirmasi"); dlg.geometry("360x160")
        dlg.resizable(False,False)
        dlg.configure(fg_color=COLORS["bg_card"])
        dlg.grab_set(); dlg.lift()
        ctk.CTkFrame(dlg, height=4, fg_color=COLORS["danger"],
                     corner_radius=0).pack(fill="x")
        label(dlg, title, style="heading").pack(
            pady=(SPACING["xl"], SPACING["xs"]))
        muted_label(dlg, subtitle, style="small").pack(
            padx=SPACING["xl"])
        r = ctk.CTkFrame(dlg, fg_color="transparent")
        r.pack(pady=SPACING["lg"])
        danger_button(r, text="  Ya, Hapus  ",
                      command=lambda:[on_ok(), dlg.destroy()]).pack(
            side="left", padx=SPACING["sm"])
        secondary_button(r, text="  Batal  ",
                         command=dlg.destroy).pack(
            side="left", padx=SPACING["sm"])

    def _refresh_list(self):
        for w in self.scroll_list.winfo_children(): w.destroy()

        tab   = self._active_tab.get()
        type_f = {"Pendapatan":"income","Pengeluaran":"expense"}.get(tab)
        mv    = self.combo_month.get()
        month = mv if mv != "Semua Bulan" else None
        search= self.ent_search.get().strip() or None

        txns = db.get_transactions(
            limit=300, type_=type_f, month=month, search=search)
        s    = db.get_summary(month)

        self.sum_lbl["income"].configure(text=format_currency(s["income"]))
        self.sum_lbl["expense"].configure(text=format_currency(s["expense"]))
        self.sum_lbl["txn"].configure(text=str(s["txn_count"]))
        self.sum_lbl["period"].configure(
            text=month or date.today().strftime("%B %Y"))

        if not txns:
            f = ctk.CTkFrame(self.scroll_list, fg_color="transparent")
            f.pack(fill="x", pady=SPACING["3xl"])
            muted_label(f, "Tidak ada transaksi ditemukan",
                        style="subtitle").pack(); return

        for i,t in enumerate(txns):
            self._txn_row(t, i)

    def _txn_row(self, t, idx):
        is_in = t["type"] == "income"
        color = COLORS["success"] if is_in else COLORS["danger"]
        soft  = COLORS["success_soft"] if is_in else COLORS["danger_soft"]
        sign  = "+" if is_in else "−"

        row = ctk.CTkFrame(
            self.scroll_list,
            fg_color=COLORS["bg_elevated"] if idx%2 else COLORS["bg_card"],
            corner_radius=0)
        row.pack(fill="x")
        row.columnconfigure(1, weight=1)

        ico = ctk.CTkFrame(row, width=36, height=36,
                            corner_radius=8, fg_color=soft)
        ico.grid(row=0, column=0, rowspan=2,
                 padx=(SPACING["md"],SPACING["sm"]),
                 pady=SPACING["sm"])
        ico.pack_propagate(False)
        ctk.CTkLabel(ico,
                     text=t.get("cat_icon") or ("💰" if is_in else "💸"),
                     font=("Segoe UI",14)).place(
            relx=0.5, rely=0.5, anchor="center")

        label(row, t.get("description") or "—",
              style="body_bold").grid(row=0, column=1, sticky="w")
        muted_label(row, t.get("acc_name","?"),
                    style="caption").grid(row=1, column=1, sticky="w")

        badge(row, t.get("cat_name","?"),
              "success" if is_in else "danger").grid(
            row=0, column=2, rowspan=2, padx=SPACING["sm"])

        muted_label(row, t["date"], style="caption").grid(
            row=0, column=3, rowspan=2, padx=SPACING["sm"])

        ctk.CTkLabel(row,
                     text=f"{sign} {format_currency(t['amount'])}",
                     font=FONTS["body_bold"],
                     text_color=color).grid(
            row=0, column=4, rowspan=2, padx=SPACING["sm"])

        act = ctk.CTkFrame(row, fg_color="transparent")
        act.grid(row=0, column=5, rowspan=2,
                 padx=(0,SPACING["sm"]))
        ctk.CTkButton(
            act, text="✏", width=30, height=30,
            fg_color=COLORS["accent_soft"],
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["accent"],
            corner_radius=RADIUS["sm"],
            command=lambda t=t: self._open_dialog(t)).pack(
            side="left", padx=1)
        ctk.CTkButton(
            act, text="🗑", width=30, height=30,
            fg_color=COLORS["danger_soft"],
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["danger"],
            corner_radius=RADIUS["sm"],
            command=lambda id_=t["id"]: self._delete_txn(id_)).pack(
            side="left", padx=1)

        ctk.CTkFrame(self.scroll_list, height=1,
                     fg_color=COLORS["border"]).pack(fill="x")
