# account.py
import tkinter as tk
import customtkinter as ctk
from style import *
import database as db

ACCOUNT_TYPES  = ["Kas","Bank","Tabungan","E-Wallet","Investasi","Lainnya"]
ACCOUNT_ICONS  = ["💵","🏦","🏧","💳","📱","💼","🏪","🎯"]
ACCOUNT_COLORS = ["#10B981","#3B82F6","#6366F1","#F59E0B","#EF4444","#EC4899","#8B5CF6","#F97316"]
CAT_ICONS = ["🛍️","💼","📈","💰","🛒","👷","🏠","📣","⚙️","📦",
             "🍔","🚗","✈️","💊","🎓","🏋️","🎮","📸","🔧","💡",
             "🧾","📊","🏷️","🎁","💻","📞","🌐","🧹","🪴","⭐"]


class AccountPage(ctk.CTkFrame):
    def __init__(self, parent, navigate_fn, **kw):
        super().__init__(parent, fg_color=COLORS["bg_primary"], **kw)
        self.navigate_fn = navigate_fn
        self._build_ui()

    def on_show(self):
        self._refresh_profile()
        self._refresh_accounts()
        self._refresh_categories()
        self._refresh_stats()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Topbar
        tb = topbar(self)
        tb.grid(row=0, column=0, sticky="ew")
        tb.columnconfigure(1, weight=1)
        tb.grid_propagate(False)
        left = ctk.CTkFrame(tb, fg_color="transparent")
        left.grid(row=0,column=0,sticky="w",padx=SPACING["2xl"],pady=SPACING["md"])
        label(left,"Profil Bisnis",style="title").pack(anchor="w")
        muted_label(left,"Kelola informasi bisnis dan akun Anda",style="caption").pack(anchor="w")
        secondary_button(tb,text="  ✏  Edit Profil  ",height=34,
                         command=self._open_edit_profile).grid(
            row=0,column=2,sticky="e",padx=SPACING["2xl"])

        # Body
        body = scrollable(self)
        body.grid(row=1,column=0,sticky="nsew")
        body.columnconfigure(0,weight=1)

        wrap = ctk.CTkFrame(body,fg_color="transparent")
        wrap.pack(fill="x",padx=SPACING["2xl"],pady=SPACING["xl"])
        wrap.columnconfigure(0,weight=3); wrap.columnconfigure(1,weight=2)

        left_col = ctk.CTkFrame(wrap,fg_color="transparent")
        left_col.grid(row=0,column=0,sticky="nsew",padx=(0,SPACING["lg"]))
        left_col.columnconfigure(0,weight=1)

        right_col = ctk.CTkFrame(wrap,fg_color="transparent")
        right_col.grid(row=0,column=1,sticky="nsew")
        right_col.columnconfigure(0,weight=1)

        self._build_profile_card(left_col)
        self._build_account_section(left_col)
        self._build_category_section(left_col)
        self._build_stats_card(right_col)

    # ── Profile ──────────────────────────────────────────────────

    def _build_profile_card(self, parent):
        c = card_frame(parent)
        c.grid(row=0,column=0,sticky="ew",pady=(0,SPACING["lg"]))

        inner = ctk.CTkFrame(c,fg_color="transparent")
        inner.pack(fill="x",padx=SPACING["xl"],pady=SPACING["xl"])
        inner.columnconfigure(1,weight=1)

        av = ctk.CTkFrame(inner,width=72,height=72,corner_radius=36,
                           fg_color=COLORS["accent"])
        av.grid(row=0,column=0,rowspan=3,padx=(0,SPACING["xl"]))
        av.pack_propagate(False)
        ctk.CTkLabel(av,text="🏪",font=("Segoe UI",28)).place(relx=0.5,rely=0.5,anchor="center")

        self.lbl_biz_name = label(inner,"UMKM Saya",style="title")
        self.lbl_biz_name.grid(row=0,column=1,sticky="w")
        ctk.CTkLabel(inner,text="  Aktif  ",font=FONTS["caption"],
                     text_color=COLORS["success"],fg_color=COLORS["success_soft"],
                     corner_radius=RADIUS["pill"],padx=8,pady=2).grid(
            row=0,column=2,padx=SPACING["sm"])
        self.lbl_owner = muted_label(inner,"Pemilik: —",style="small")
        self.lbl_owner.grid(row=1,column=1,columnspan=2,sticky="w")
        self.lbl_type  = muted_label(inner,"Jenis Usaha: —",style="small")
        self.lbl_type.grid(row=2,column=1,columnspan=2,sticky="w")

        divider(c).pack(fill="x",padx=SPACING["xl"])
        cr = ctk.CTkFrame(c,fg_color="transparent")
        cr.pack(fill="x",padx=SPACING["xl"],pady=SPACING["md"])
        self.lbl_phone   = muted_label(cr,"📞 —",style="small"); self.lbl_phone.pack(side="left",padx=(0,SPACING["xl"]))
        self.lbl_email   = muted_label(cr,"✉️ —",style="small"); self.lbl_email.pack(side="left",padx=(0,SPACING["xl"]))
        self.lbl_address = muted_label(cr,"📍 —",style="small"); self.lbl_address.pack(side="left")

    def _refresh_profile(self):
        self.lbl_biz_name.configure(text=db.get_setting("business_name","UMKM Saya"))
        self.lbl_owner.configure(text=f"Pemilik: {db.get_setting('owner_name','—')}")
        self.lbl_type.configure(text=f"Jenis Usaha: {db.get_setting('business_type','—')}")
        self.lbl_phone.configure(text=f"📞 {db.get_setting('phone','—')}")
        self.lbl_email.configure(text=f"✉️ {db.get_setting('email','—')}")
        self.lbl_address.configure(text=f"📍 {db.get_setting('address','—')}")

    def _open_edit_profile(self):
        dlg = ctk.CTkToplevel(self)
        dlg.title("Edit Profil"); dlg.geometry("460x560")
        dlg.resizable(False,True)
        dlg.configure(fg_color=COLORS["bg_card"])
        dlg.grab_set(); dlg.lift()
        ctk.CTkFrame(dlg,height=4,fg_color=COLORS["accent"],corner_radius=0).pack(fill="x")
        label(dlg,"Edit Profil Bisnis",style="subtitle").pack(
            anchor="w",padx=SPACING["2xl"],pady=(SPACING["xl"],SPACING["sm"]))
        sa = scrollable(dlg)
        sa.pack(fill="both",expand=True,padx=SPACING["2xl"])
        sa.columnconfigure(0,weight=1)
        fields=[("Nama Bisnis","business_name"),("Nama Pemilik","owner_name"),
                ("Jenis Usaha","business_type"),("No. Telepon","phone"),
                ("Email","email"),("Alamat","address")]
        entries={}
        for r,(lbl_txt,key) in enumerate(fields):
            muted_label(sa,lbl_txt,style="small").grid(row=r*2,column=0,sticky="w",pady=(0,2))
            e=styled_entry(sa,placeholder_text=lbl_txt)
            e.grid(row=r*2+1,column=0,sticky="ew",pady=(0,SPACING["sm"]))
            val=db.get_setting(key,"")
            if val and val != "—": e.insert(0,val)
            entries[key]=e
        def _save():
            for key,e in entries.items(): db.set_setting(key,e.get().strip() or "—")
            self._refresh_profile(); dlg.destroy()
        bo=ctk.CTkFrame(dlg,fg_color=COLORS["bg_card"],height=68)
        bo.pack(fill="x",padx=SPACING["2xl"],pady=(SPACING["sm"],SPACING["xl"]))
        bo.pack_propagate(False)
        primary_button(bo,text="  💾  Simpan  ",command=_save).pack(side="left",fill="x",expand=True,padx=(0,SPACING["sm"]))
        secondary_button(bo,text="  ✖  Batal  ",command=dlg.destroy).pack(side="left",fill="x",expand=True)

    # ── Accounts ─────────────────────────────────────────────────

    def _build_account_section(self, parent):
        c = card_frame(parent)
        c.grid(row=1,column=0,sticky="ew",pady=(0,SPACING["lg"]))
        c.columnconfigure(0,weight=1)
        hdr=ctk.CTkFrame(c,fg_color="transparent")
        hdr.grid(row=0,column=0,sticky="ew",padx=SPACING["xl"],pady=(SPACING["xl"],SPACING["sm"]))
        label(hdr,"Rekening",style="subtitle").pack(side="left")
        self.lbl_total=ctk.CTkLabel(hdr,text="Total: Rp 0",font=FONTS["body_bold"],
                                     text_color=COLORS["success"])
        self.lbl_total.pack(side="right")
        primary_button(hdr,text="  + Tambah  ",height=30,
                       command=lambda: self._open_account_dialog()).pack(
            side="right",padx=(0,SPACING["sm"]))
        self.acc_list=ctk.CTkFrame(c,fg_color="transparent")
        self.acc_list.grid(row=1,column=0,sticky="ew",
                            padx=SPACING["xl"],pady=(0,SPACING["xl"]))
        self.acc_list.columnconfigure(0,weight=1)

    def _open_account_dialog(self, acc=None):
        dlg=ctk.CTkToplevel(self)
        dlg.title("Edit Rekening" if acc else "Tambah Rekening")
        dlg.geometry("440x500"); dlg.resizable(False,True)
        dlg.configure(fg_color=COLORS["bg_card"])
        dlg.grab_set(); dlg.lift()
        ctk.CTkFrame(dlg,height=4,fg_color=COLORS["accent"],corner_radius=0).pack(fill="x")
        label(dlg,"Edit Rekening" if acc else "Tambah Rekening Baru",style="subtitle").pack(
            anchor="w",padx=SPACING["2xl"],pady=(SPACING["xl"],SPACING["sm"]))
        sa=scrollable(dlg)
        sa.pack(fill="both",expand=True,padx=SPACING["2xl"])
        sa.columnconfigure((0,1),weight=1)

        muted_label(sa,"Nama Rekening",style="small").grid(row=0,column=0,columnspan=2,sticky="w",pady=(0,2))
        e_name=styled_entry(sa,placeholder_text="Contoh: Kas Toko")
        e_name.grid(row=1,column=0,columnspan=2,sticky="ew",pady=(0,SPACING["sm"]))
        if acc: e_name.insert(0,acc["name"])

        muted_label(sa,"Tipe",style="small").grid(row=2,column=0,sticky="w",pady=(0,2))
        muted_label(sa,"Saldo Awal (Rp)",style="small").grid(row=2,column=1,sticky="w",pady=(0,2))
        combo_type=styled_combo(sa,values=ACCOUNT_TYPES)
        combo_type.set(acc.get("type",ACCOUNT_TYPES[0]) if acc else ACCOUNT_TYPES[0])
        combo_type.grid(row=3,column=0,sticky="ew",padx=(0,SPACING["sm"]),pady=(0,SPACING["sm"]))
        e_bal=styled_entry(sa,placeholder_text="0")
        e_bal.grid(row=3,column=1,sticky="ew",pady=(0,SPACING["sm"]))
        if acc: e_bal.insert(0,str(int(acc["balance"])))

        # Icon picker
        muted_label(sa,"Pilih Icon",style="small").grid(row=4,column=0,columnspan=2,sticky="w",pady=(0,2))
        ir=ctk.CTkFrame(sa,fg_color="transparent")
        ir.grid(row=5,column=0,columnspan=2,sticky="w",pady=(0,SPACING["sm"]))
        sel_icon=[acc["icon"] if acc else ACCOUNT_ICONS[0]]
        icon_btns={}
        def pick_icon(i):
            sel_icon[0]=i
            for k,b in icon_btns.items():
                b.configure(fg_color=COLORS["accent_soft"] if k==i else COLORS["bg_input"],
                            border_width=2 if k==i else 0)
        for ico in ACCOUNT_ICONS:
            b=ctk.CTkButton(ir,text=ico,width=38,height=38,
                             fg_color=COLORS["accent_soft"] if ico==sel_icon[0] else COLORS["bg_input"],
                             hover_color=COLORS["bg_hover"],corner_radius=RADIUS["sm"],
                             font=("Segoe UI",15),border_width=2 if ico==sel_icon[0] else 0,
                             border_color=COLORS["accent"],
                             command=lambda i=ico: pick_icon(i))
            b.pack(side="left",padx=2); icon_btns[ico]=b

        # Color picker
        muted_label(sa,"Pilih Warna",style="small").grid(row=6,column=0,columnspan=2,sticky="w",pady=(0,2))
        cr=ctk.CTkFrame(sa,fg_color="transparent")
        cr.grid(row=7,column=0,columnspan=2,sticky="w",pady=(0,SPACING["sm"]))
        sel_color=[acc["color"] if acc else ACCOUNT_COLORS[0]]
        color_btns={}
        def pick_color(col):
            sel_color[0]=col
            for k,b in color_btns.items():
                b.configure(border_width=3 if k==col else 0)
        for col in ACCOUNT_COLORS:
            b=ctk.CTkButton(cr,text="",width=26,height=26,fg_color=col,hover_color=col,
                             corner_radius=RADIUS["pill"],
                             border_width=3 if col==sel_color[0] else 0,
                             border_color=COLORS["text_primary"],
                             command=lambda c=col: pick_color(c))
            b.pack(side="left",padx=2); color_btns[col]=b

        lbl_err=ctk.CTkLabel(sa,text="",text_color=COLORS["danger"],font=FONTS["small"],anchor="w")
        lbl_err.grid(row=8,column=0,columnspan=2,sticky="w")

        def _save():
            name=e_name.get().strip()
            if not name: lbl_err.configure(text="❌ Nama wajib diisi"); return
            try: bal=float(e_bal.get().replace(".","").replace(",","") or "0")
            except ValueError: lbl_err.configure(text="❌ Saldo harus angka"); return
            if acc:
                db.update_account(acc["id"],name=name,type_=combo_type.get(),
                                  balance=bal,color=sel_color[0],icon=sel_icon[0])
            else:
                db.add_account(name=name,type_=combo_type.get(),
                               balance=bal,color=sel_color[0],icon=sel_icon[0])
            dlg.destroy(); self._refresh_accounts(); self._refresh_stats()

        bo=ctk.CTkFrame(dlg,fg_color=COLORS["bg_card"],height=68)
        bo.pack(fill="x",padx=SPACING["2xl"],pady=(SPACING["sm"],SPACING["xl"]))
        bo.pack_propagate(False)
        primary_button(bo,text="  💾  Simpan  ",command=_save).pack(side="left",fill="x",expand=True,padx=(0,SPACING["sm"]))
        secondary_button(bo,text="  ✖  Batal  ",command=dlg.destroy).pack(side="left",fill="x",expand=True)

    def _refresh_accounts(self):
        for w in self.acc_list.winfo_children(): w.destroy()
        accs=db.get_accounts()
        total=sum(a["balance"] for a in accs)
        self.lbl_total.configure(
            text=f"Total: {format_currency_full(total)}",
            text_color=COLORS["success"] if total>=0 else COLORS["danger"])
        if not accs:
            ph=elevated_frame(self.acc_list,corner_radius=RADIUS["md"])
            ph.pack(fill="x")
            muted_label(ph,"Belum ada rekening · Klik + Tambah",style="small").pack(pady=SPACING["xl"])
            return
        for a in accs: self._acc_row(a)

    def _acc_row(self, acc):
        row=card_frame(self.acc_list,corner_radius=RADIUS["md"])
        row.pack(fill="x",pady=3)
        row.columnconfigure(1,weight=1)
        circle=ctk.CTkFrame(row,width=44,height=44,corner_radius=22,fg_color=acc.get("color",COLORS["accent"]))
        circle.grid(row=0,column=0,rowspan=2,padx=(SPACING["md"],SPACING["sm"]),pady=SPACING["sm"])
        circle.pack_propagate(False)
        ctk.CTkLabel(circle,text=acc.get("icon","🏦"),font=("Segoe UI",18)).place(relx=0.5,rely=0.5,anchor="center")
        label(row,acc["name"],style="body_bold").grid(row=0,column=1,sticky="w")
        muted_label(row,acc.get("type",""),style="caption").grid(row=1,column=1,sticky="w")
        bc=COLORS["success"] if acc["balance"]>=0 else COLORS["danger"]
        ctk.CTkLabel(row,text=format_currency_full(acc["balance"]),
                     font=FONTS["body_bold"],text_color=bc).grid(row=0,column=2,rowspan=2,padx=SPACING["sm"])
        act=ctk.CTkFrame(row,fg_color="transparent")
        act.grid(row=0,column=3,rowspan=2,padx=(0,SPACING["sm"]))
        ctk.CTkButton(act,text="✏",width=28,height=28,fg_color=COLORS["accent_soft"],
                      hover_color=COLORS["bg_hover"],text_color=COLORS["accent"],
                      corner_radius=RADIUS["sm"],
                      command=lambda a=acc: self._open_account_dialog(a)).pack(pady=2)
        ctk.CTkButton(act,text="🗑",width=28,height=28,fg_color=COLORS["danger_soft"],
                      hover_color=COLORS["bg_hover"],text_color=COLORS["danger"],
                      corner_radius=RADIUS["sm"],
                      command=lambda id_=acc["id"]: self._confirm("Hapus rekening ini?",
                          "Transaksi terkait tidak ikut terhapus.",
                          lambda: [db.delete_account(id_), self._refresh_accounts(), self._refresh_stats()])).pack(pady=2)

    # ── Categories ───────────────────────────────────────────────

    def _build_category_section(self, parent):
        c=card_frame(parent)
        c.grid(row=2,column=0,sticky="ew")
        c.columnconfigure(0,weight=1)
        hdr=ctk.CTkFrame(c,fg_color="transparent")
        hdr.grid(row=0,column=0,sticky="ew",padx=SPACING["xl"],pady=(SPACING["xl"],SPACING["sm"]))
        label(hdr,"Kategori",style="subtitle").pack(side="left")
        primary_button(hdr,text="  + Tambah  ",height=30,
                       command=self._open_cat_dialog).pack(side="right")
        # Tab
        self.cat_tab=tk.StringVar(value="income")
        tab_row=ctk.CTkFrame(c,fg_color="transparent")
        tab_row.grid(row=1,column=0,sticky="ew",padx=SPACING["xl"],pady=(0,SPACING["sm"]))
        toggle=ctk.CTkFrame(tab_row,fg_color=COLORS["bg_elevated"],corner_radius=RADIUS["md"])
        toggle.pack(side="left")
        self.btn_inc=ctk.CTkButton(toggle,text="✅ Pendapatan",height=30,width=110,
                                    fg_color=COLORS["success"],text_color="#FFF",
                                    hover_color=COLORS["success"],corner_radius=RADIUS["sm"],
                                    font=FONTS["small_bold"],command=lambda:self._switch_cat("income"))
        self.btn_inc.pack(side="left",padx=2,pady=2)
        self.btn_exp=ctk.CTkButton(toggle,text="❌ Pengeluaran",height=30,width=110,
                                    fg_color="transparent",text_color=COLORS["text_secondary"],
                                    hover_color=COLORS["bg_hover"],corner_radius=RADIUS["sm"],
                                    font=FONTS["small"],command=lambda:self._switch_cat("expense"))
        self.btn_exp.pack(side="left",padx=2,pady=2)
        self.cat_list=scrollable(c,height=220)
        self.cat_list.grid(row=2,column=0,sticky="ew",padx=SPACING["xl"],pady=(0,SPACING["xl"]))

    def _switch_cat(self, tab):
        self.cat_tab.set(tab)
        if tab=="income":
            self.btn_inc.configure(fg_color=COLORS["success"],text_color="#FFF",font=FONTS["small_bold"])
            self.btn_exp.configure(fg_color="transparent",text_color=COLORS["text_secondary"],font=FONTS["small"])
        else:
            self.btn_exp.configure(fg_color=COLORS["danger"],text_color="#FFF",font=FONTS["small_bold"])
            self.btn_inc.configure(fg_color="transparent",text_color=COLORS["text_secondary"],font=FONTS["small"])
        self._refresh_categories()

    def _open_cat_dialog(self):
        dlg=ctk.CTkToplevel(self)
        dlg.title("Tambah Kategori"); dlg.geometry("440x460")
        dlg.resizable(False,True)
        dlg.configure(fg_color=COLORS["bg_card"])
        dlg.grab_set(); dlg.lift()
        ctk.CTkFrame(dlg,height=4,fg_color=COLORS["accent"],corner_radius=0).pack(fill="x")
        label(dlg,"Tambah Kategori Baru",style="subtitle").pack(
            anchor="w",padx=SPACING["2xl"],pady=(SPACING["xl"],SPACING["sm"]))
        sa=scrollable(dlg)
        sa.pack(fill="both",expand=True,padx=SPACING["2xl"])
        sa.columnconfigure(0,weight=1)
        muted_label(sa,"Nama Kategori",style="small").grid(row=0,column=0,sticky="w",pady=(0,2))
        e_name=styled_entry(sa,placeholder_text="Contoh: Penjualan Online")
        e_name.grid(row=1,column=0,sticky="ew",pady=(0,SPACING["sm"]))
        muted_label(sa,"Tipe",style="small").grid(row=2,column=0,sticky="w",pady=(0,2))
        combo_type=styled_combo(sa,values=["income","expense"])
        combo_type.set("income")
        combo_type.grid(row=3,column=0,sticky="ew",pady=(0,SPACING["sm"]))
        muted_label(sa,"Pilih Icon",style="small").grid(row=4,column=0,sticky="w",pady=(0,2))
        ig=ctk.CTkFrame(sa,fg_color=COLORS["bg_input"],corner_radius=RADIUS["md"])
        ig.grid(row=5,column=0,sticky="ew",pady=(0,SPACING["sm"]))
        sel_ci=[CAT_ICONS[0]]; ci_btns={}
        def pick_ci(i):
            sel_ci[0]=i
            for k,b in ci_btns.items():
                b.configure(fg_color=COLORS["accent_soft"] if k==i else "transparent",
                            border_width=2 if k==i else 0)
        for idx,ico in enumerate(CAT_ICONS):
            r2,c2=divmod(idx,10)
            b=ctk.CTkButton(ig,text=ico,width=34,height=34,
                             fg_color=COLORS["accent_soft"] if ico==sel_ci[0] else "transparent",
                             hover_color=COLORS["bg_hover"],corner_radius=RADIUS["sm"],
                             font=("Segoe UI",14),border_width=2 if ico==sel_ci[0] else 0,
                             border_color=COLORS["accent"],command=lambda i=ico:pick_ci(i))
            b.grid(row=r2,column=c2,padx=1,pady=1); ci_btns[ico]=b
        lbl_err=ctk.CTkLabel(sa,text="",text_color=COLORS["danger"],font=FONTS["small"],anchor="w")
        lbl_err.grid(row=6,column=0,sticky="w")
        def _save():
            name=e_name.get().strip()
            if not name: lbl_err.configure(text="❌ Nama wajib diisi"); return
            cm={"income":COLORS["success"],"expense":COLORS["danger"]}
            db.add_category(name,combo_type.get(),sel_ci[0],cm.get(combo_type.get(),COLORS["accent"]))
            dlg.destroy(); self._refresh_categories(); self._refresh_stats()
        bo=ctk.CTkFrame(dlg,fg_color=COLORS["bg_card"],height=68)
        bo.pack(fill="x",padx=SPACING["2xl"],pady=(SPACING["sm"],SPACING["xl"]))
        bo.pack_propagate(False)
        primary_button(bo,text="  ➕  Tambah  ",command=_save).pack(side="left",fill="x",expand=True,padx=(0,SPACING["sm"]))
        secondary_button(bo,text="  ✖  Batal  ",command=dlg.destroy).pack(side="left",fill="x",expand=True)

    def _refresh_categories(self):
        for w in self.cat_list.winfo_children(): w.destroy()
        cats=db.get_categories(self.cat_tab.get())
        if not cats:
            muted_label(self.cat_list,"Belum ada kategori · Klik + Tambah",style="small").pack(pady=SPACING["xl"]); return
        is_in=self.cat_tab.get()=="income"
        soft=COLORS["success_soft"] if is_in else COLORS["danger_soft"]
        for cat in cats:
            row=ctk.CTkFrame(self.cat_list,fg_color="transparent",corner_radius=RADIUS["sm"])
            row.pack(fill="x",pady=2)
            row.columnconfigure(1,weight=1)
            ibg=ctk.CTkFrame(row,width=36,height=36,corner_radius=8,fg_color=soft)
            ibg.grid(row=0,column=0,padx=(0,SPACING["sm"]),pady=3)
            ibg.pack_propagate(False)
            ctk.CTkLabel(ibg,text=cat.get("icon","📦"),font=("Segoe UI",14)).place(relx=0.5,rely=0.5,anchor="center")
            label(row,cat["name"],style="body_bold").grid(row=0,column=1,sticky="w")
            badge(row,cat["type"],"success" if is_in else "danger").grid(row=0,column=2,padx=SPACING["sm"])
            ctk.CTkButton(row,text="🗑",width=28,height=28,fg_color=COLORS["danger_soft"],
                          hover_color=COLORS["bg_hover"],text_color=COLORS["danger"],
                          corner_radius=RADIUS["sm"],
                          command=lambda id_=cat["id"]: self._confirm(
                              "Hapus kategori ini?","Transaksi terkait tidak ikut terhapus.",
                              lambda: [db.delete_category(id_), self._refresh_categories(), self._refresh_stats()])
                          ).grid(row=0,column=3,padx=(0,SPACING["xs"]))

    # ── Stats card ───────────────────────────────────────────────

    def _build_stats_card(self, parent):
        c=card_frame(parent)
        c.grid(row=0,column=0,sticky="ew")
        label(c,"Ringkasan",style="subtitle").pack(anchor="w",padx=SPACING["xl"],pady=(SPACING["xl"],SPACING["sm"]))
        self.stat_lbls={}
        items=[("total_txn","🔢","Total Transaksi",COLORS["accent"]),
               ("total_omzet","💰","Total Omzet",COLORS["success"]),
               ("total_acc","🏦","Jumlah Rekening",COLORS["info"]),
               ("total_cat","🏷️","Jumlah Kategori",COLORS["warning"])]
        for key,ico,title,color in items:
            row=ctk.CTkFrame(c,fg_color="transparent"); row.pack(fill="x",padx=SPACING["xl"],pady=SPACING["sm"])
            ibg=ctk.CTkFrame(row,width=40,height=40,corner_radius=8,fg_color=COLORS.get(f"{key.split('_')[1]}_soft",COLORS["accent_soft"]))
            # use proper soft color
            soft_map={"total_txn":COLORS["accent_soft"],"total_omzet":COLORS["success_soft"],
                      "total_acc":COLORS["info_soft"],"total_cat":COLORS["warning_soft"]}
            ibg.configure(fg_color=soft_map.get(key,COLORS["accent_soft"]))
            ibg.pack(side="left",padx=(0,SPACING["md"])); ibg.pack_propagate(False)
            ctk.CTkLabel(ibg,text=ico,font=("Segoe UI",16)).place(relx=0.5,rely=0.5,anchor="center")
            txt=ctk.CTkFrame(row,fg_color="transparent"); txt.pack(side="left")
            muted_label(txt,title,style="caption").pack(anchor="w")
            lbl=ctk.CTkLabel(txt,text="—",font=FONTS["number_md"],text_color=color); lbl.pack(anchor="w")
            self.stat_lbls[key]=lbl
            divider(c).pack(fill="x",padx=SPACING["xl"])
        ctk.CTkFrame(c,height=SPACING["sm"],fg_color="transparent").pack()

    def _refresh_stats(self):
        s=db.get_summary(); accs=db.get_accounts(); cats=db.get_categories()
        self.stat_lbls["total_txn"].configure(text=str(s["txn_count"]))
        self.stat_lbls["total_omzet"].configure(text=format_currency(s["income"]))
        self.stat_lbls["total_acc"].configure(text=str(len(accs)))
        self.stat_lbls["total_cat"].configure(text=str(len(cats)))

    # ── Confirm dialog ───────────────────────────────────────────

    def _confirm(self, title, subtitle, on_ok):
        dlg=ctk.CTkToplevel(self)
        dlg.title("Konfirmasi"); dlg.geometry("360x160")
        dlg.resizable(False,False)
        dlg.configure(fg_color=COLORS["bg_card"])
        dlg.grab_set(); dlg.lift()
        ctk.CTkFrame(dlg,height=4,fg_color=COLORS["danger"],corner_radius=0).pack(fill="x")
        label(dlg,title,style="heading").pack(pady=(SPACING["xl"],SPACING["xs"]))
        muted_label(dlg,subtitle,style="small").pack(padx=SPACING["xl"])
        r=ctk.CTkFrame(dlg,fg_color="transparent"); r.pack(pady=SPACING["lg"])
        danger_button(r,text="  Ya, Hapus  ",
                      command=lambda:[on_ok(),dlg.destroy()]).pack(side="left",padx=SPACING["sm"])
        secondary_button(r,text="  Batal  ",command=dlg.destroy).pack(side="left",padx=SPACING["sm"])
