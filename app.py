# app.py
import tkinter as tk
import customtkinter as ctk
from style import *
import database as db
from dashboard   import DashboardPage
from transaction import TransactionPage
from insight     import InsightPage
from account     import AccountPage


class NavButton(ctk.CTkFrame):
    def __init__(self, parent, icon, text, key, on_click, **kw):
        super().__init__(parent, fg_color="transparent",
                         cursor="hand2", corner_radius=RADIUS["md"], **kw)
        self.key=key; self.on_click=on_click; self._active=False
        self.columnconfigure(1, weight=1)
        self.bar = ctk.CTkFrame(self, width=3, corner_radius=2, fg_color="transparent")
        self.bar.place(x=0, rely=0, relheight=1)
        self.ico = ctk.CTkLabel(self, text=icon, font=("Segoe UI",16),
                                 text_color=COLORS["sidebar_text"], width=30)
        self.ico.grid(row=0,column=0,padx=(SPACING["lg"],SPACING["sm"]),pady=SPACING["md"])
        self.lbl = ctk.CTkLabel(self, text=text, font=FONTS["nav"],
                                 text_color=COLORS["sidebar_text"], anchor="w")
        self.lbl.grid(row=0,column=1,sticky="ew")
        for w in (self,self.ico,self.lbl):
            w.bind("<Button-1>", lambda e: self.on_click(self.key))
            w.bind("<Enter>",    lambda e: self._hover(True))
            w.bind("<Leave>",    lambda e: self._hover(False))

    def _hover(self, on):
        if not self._active:
            self.configure(fg_color="#2A3550" if on else "transparent")

    def set_active(self, v):
        self._active = v
        if v:
            self.configure(fg_color=COLORS["sidebar_active"])
            self.ico.configure(text_color=COLORS["sidebar_active_text"])
            self.lbl.configure(text_color=COLORS["sidebar_active_text"], font=FONTS["nav_bold"])
            self.bar.configure(fg_color="#FFFFFF")
        else:
            self.configure(fg_color="transparent")
            self.ico.configure(text_color=COLORS["sidebar_text"])
            self.lbl.configure(text_color=COLORS["sidebar_text"], font=FONTS["nav"])
            self.bar.configure(fg_color="transparent")


class App(ctk.CTk):
    NAV = [("🏠","Dashboard","dashboard"),("💸","Transaksi","transaction"),
           ("📊","Insight","insight"),("👤","Profil","account")]

    def __init__(self):
        super().__init__()
        self.title("SMARTUMKM — Finance Tracker")
        self.geometry("1300x800")
        self.minsize(1050,660)
        self.configure(fg_color=COLORS["bg_primary"])
        self.update_idletasks()
        sw,sh = self.winfo_screenwidth(),self.winfo_screenheight()
        self.geometry(f"1300x800+{(sw-1300)//2}+{(sh-800)//2}")
        self._btns={}; self._pages={}
        self._build_layout(); self._build_sidebar(); self._build_pages()
        self.navigate("dashboard")

    def _build_layout(self):
        self.columnconfigure(0, minsize=SIDEBAR_WIDTH, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.sidebar = ctk.CTkFrame(self, fg_color=COLORS["sidebar_bg"],
                                     width=SIDEBAR_WIDTH, corner_radius=0)
        self.sidebar.grid(row=0,column=0,sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.columnconfigure(0,weight=1)
        self.content = ctk.CTkFrame(self, fg_color=COLORS["bg_primary"], corner_radius=0)
        self.content.grid(row=0,column=1,sticky="nsew")
        self.content.columnconfigure(0,weight=1)
        self.content.rowconfigure(0,weight=1)

    def _build_sidebar(self):
        # Brand
        brand = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand.grid(row=0,column=0,sticky="ew",padx=SPACING["lg"],
                   pady=(SPACING["2xl"],SPACING["2xl"]))
        logo = ctk.CTkFrame(brand,width=40,height=40,corner_radius=10,
                             fg_color=COLORS["accent"])
        logo.pack(side="left",padx=(0,SPACING["md"]))
        logo.pack_propagate(False)
        ctk.CTkLabel(logo,text="⚡",font=("Segoe UI",20,"bold"),
                     text_color="#FFF").place(relx=0.5,rely=0.5,anchor="center")
        bt = ctk.CTkFrame(brand,fg_color="transparent"); bt.pack(side="left")
        ctk.CTkLabel(bt,text="SMARTUMKM",font=("Segoe UI",13,"bold"),
                     text_color="#FFFFFF").pack(anchor="w")
        ctk.CTkLabel(bt,text="Finance Tracker",font=FONTS["caption"],
                     text_color=COLORS["sidebar_text"]).pack(anchor="w")

        ctk.CTkLabel(self.sidebar,text="  MENU",font=("Segoe UI",9,"bold"),
                     text_color="#485580",anchor="w").grid(
            row=1,column=0,sticky="ew",padx=SPACING["xl"],pady=(0,SPACING["sm"]))

        nav = ctk.CTkFrame(self.sidebar,fg_color="transparent")
        nav.grid(row=2,column=0,sticky="ew",padx=SPACING["sm"])
        nav.columnconfigure(0,weight=1)
        for i,(ico,txt,key) in enumerate(self.NAV):
            b = NavButton(nav,ico,txt,key,on_click=self.navigate)
            b.grid(row=i,column=0,sticky="ew",pady=2)
            self._btns[key]=b

        sp=ctk.CTkFrame(self.sidebar,fg_color="transparent")
        sp.grid(row=3,column=0,sticky="nsew"); self.sidebar.rowconfigure(3,weight=1)

        ctk.CTkFrame(self.sidebar,height=1,fg_color="#2A3550").grid(
            row=4,column=0,sticky="ew",padx=SPACING["lg"],pady=SPACING["md"])

        # User card
        uc=ctk.CTkFrame(self.sidebar,fg_color="#131929",corner_radius=RADIUS["lg"],
                         border_width=1,border_color="#2A3550")
        uc.grid(row=5,column=0,sticky="ew",padx=SPACING["lg"],pady=(0,SPACING["xl"]))
        av=ctk.CTkFrame(uc,width=32,height=32,corner_radius=16,fg_color=COLORS["accent_soft"])
        av.pack(side="left",padx=(SPACING["md"],SPACING["sm"]),pady=SPACING["md"])
        av.pack_propagate(False)
        ctk.CTkLabel(av,text="👤",font=("Segoe UI",14)).place(relx=0.5,rely=0.5,anchor="center")
        info=ctk.CTkFrame(uc,fg_color="transparent"); info.pack(side="left")
        self.lbl_biz=ctk.CTkLabel(info,text="UMKM Saya",font=FONTS["small_bold"],
                                   text_color="#FFFFFF",anchor="w")
        self.lbl_biz.pack(anchor="w")
        ctk.CTkLabel(info,text="Finance Tracker",font=FONTS["caption"],
                     text_color=COLORS["sidebar_text"],anchor="w").pack(anchor="w")

    def _build_pages(self):
        for key,Cls in [("dashboard",DashboardPage),("transaction",TransactionPage),
                        ("insight",InsightPage),("account",AccountPage)]:
            f=Cls(self.content,navigate_fn=self.navigate)
            f.grid(row=0,column=0,sticky="nsew")
            self._pages[key]=f

    def navigate(self, key):
        if key not in self._pages: return
        for k,b in self._btns.items(): b.set_active(k==key)
        self._pages[key].tkraise()
        if hasattr(self._pages[key],"on_show"): self._pages[key].on_show()
        self.lbl_biz.configure(text=db.get_setting("business_name","UMKM Saya")[:18])


def main():
    print("🚀 SMARTUMKM starting...")
    db.init_db(); print("✅ DB ready")
    App().mainloop()

if __name__=="__main__":
    main()
