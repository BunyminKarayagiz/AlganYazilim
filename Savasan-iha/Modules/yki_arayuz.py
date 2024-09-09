import customtkinter,os
import tkinter as tk
from typing import Union,Callable
from Modules.Cprint import cp
#from Cprint import cp

customtkinter.set_appearance_mode("dark")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("green")  # Themes: blue (default), dark-blue, green

class MyCheckboxFrame(customtkinter.CTkFrame):
    def __init__(self, master, title, values):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.values = values
        self.title = title
        self.checkboxes = []

        self.title = customtkinter.CTkLabel(self, text=self.title, fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")

        for i, value in enumerate(self.values):
            checkbox = customtkinter.CTkCheckBox(self, text=value)
            checkbox.grid(row=i+1, column=0, padx=10, pady=(10, 0), sticky="w")
            self.checkboxes.append(checkbox)

    def get(self):
        checked_checkboxes = []
        for checkbox in self.checkboxes:
            if checkbox.get() == 1:
                checked_checkboxes.append(checkbox.cget("text"))
        return checked_checkboxes
class MyRadiobuttonFrame(customtkinter.CTkFrame):
    def __init__(self, master, title, values):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.values = values
        self.title = title
        self.radiobuttons = []
        self.variable = customtkinter.StringVar(value="")

        self.title = customtkinter.CTkLabel(self, text=self.title, fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")

        for i, value in enumerate(self.values):
            radiobutton = customtkinter.CTkRadioButton(self, text=value, value=value, variable=self.variable)
            radiobutton.grid(row=i + 1, column=0, padx=10, pady=(10, 0), sticky="w")
            self.radiobuttons.append(radiobutton)

    def get(self):
        return self.variable.get()

    def set(self, value):
        self.variable.set(value)
class MyScrollableCheckboxFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, title, values):
        super().__init__(master, label_text=title)
        self.grid_columnconfigure(0, weight=1)
        self.values = values
        self.checkboxes = []

        for i, value in enumerate(self.values):
            checkbox = customtkinter.CTkCheckBox(self, text=value)
            checkbox.grid(row=i, column=0, padx=10, pady=(10, 0), sticky="w")
            self.checkboxes.append(checkbox)

    def get(self):
        checked_checkboxes = []
        for checkbox in self.checkboxes:
            if checkbox.get() == 1:
                checked_checkboxes.append(checkbox.cget("text"))
        return checked_checkboxes
class FloatSpinbox(customtkinter.CTkFrame):
    def __init__(self, *args,
                 width: int = 100,
                 height: int = 32,
                 step_size: Union[int, float] = 1,
                 command: Callable = None,
                 **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)

        self.step_size = step_size
        self.command = command

        self.configure(fg_color=("gray78", "gray28"))  # set frame color

        self.grid_columnconfigure((0, 2), weight=0)  # buttons don't expand
        self.grid_columnconfigure(1, weight=1)  # entry expands

        self.subtract_button = customtkinter.CTkButton(self, text="-", width=height-6, height=height-6,
                                                       command=self.subtract_button_callback)
        self.subtract_button.grid(row=0, column=0, padx=(3, 0), pady=3)

        self.entry = customtkinter.CTkEntry(self, width=width-(2*height), height=height-6, border_width=0)
        self.entry.grid(row=0, column=1, columnspan=1, padx=3, pady=3, sticky="ew")

        self.add_button = customtkinter.CTkButton(self, text="+", width=height-6, height=height-6,
                                                  command=self.add_button_callback)
        self.add_button.grid(row=0, column=2, padx=(0, 3), pady=3)

        # default value
        self.entry.insert(0, "0.0")

    def add_button_callback(self):
        if self.command is not None:
            self.command()
        try:
            value = float(self.entry.get()) + self.step_size
            self.entry.delete(0, "end")
            self.entry.insert(0, value)
        except ValueError:
            return

    def subtract_button_callback(self):
        if self.command is not None:
            self.command()
        try:
            value = float(self.entry.get()) - self.step_size
            self.entry.delete(0, "end")
            self.entry.insert(0, value)
        except ValueError:
            return

    def get(self) -> Union[float, None]:
        try:
            return float(self.entry.get())
        except ValueError:
            return None

    def set(self, value: float):
        self.entry.delete(0, "end")
        self.entry.insert(0, str(float(value)))

#?  LAYER-1
class MAIN_GUI_FRAME(customtkinter.CTkFrame):
    def __init__(self, master,Yer_istasyonu_obj,**kwargs):
        
        self.Yer_istasyonu_obj = Yer_istasyonu_obj
        
        super().__init__(master,**kwargs)
        self.rowconfigure(0,weight=1)
        self.columnconfigure(0,weight=1)
        self.columnconfigure(1,weight=1)

    #? LAYER-2
        self.left_main_frame = customtkinter.CTkTabview(self,corner_radius=5,border_width=1)
        self.left_main_frame.add("CONTROL")
        self.right_main_frame=customtkinter.CTkTabview(self,corner_radius=5,border_width=1)
        self.right_main_frame.add("VIDEO-FEED")

        self.left_main_frame.grid(row=0,column=0,padx=10,pady=10,sticky="nsew")
        self.right_main_frame.grid(row=0,column=1,padx=10,pady=10,sticky="nsew")

    #? LAYER-3
        self.Confirmation_button=customtkinter.CTkButton(master=self.left_main_frame.tab("CONTROL"),text="Onay VER/AL",command=Yer_istasyonu_obj.yki_onay_ver)
        self.Confirmation_button.grid(row=0,column=0,padx=10,pady=10,sticky="nwe")





#?  LAYER-1
class COMPANION_FRAMES(customtkinter.CTkFrame):
    def __init__(self, master,**kwargs):
        super().__init__(master,**kwargs)

        self.rowconfigure(0,weight=1)

        #? LAYER-2
        self.tabview = customtkinter.CTkTabview(self,corner_radius=5,border_width=1)
        self.tabview.grid(row=0,rowspan=2,column=0, padx=(5, 5), pady=(5, 5), sticky="nsew")
        self.tabview.add("LIST")
        self.tabview.add("DATA")
        self.tabview.add("MONITOR")
        # self.tabview.tab("TAB-1").grid_columnconfigure(0, weight=1)  # configure grid of individual tabs
        # self.tabview.tab("TAB-2").grid_columnconfigure(0, weight=1)
        #? LAYER-3
        # self.optionmenu_1 = customtkinter.CTkOptionMenu(self.tabview.tab("TAB-1"), dynamic_resizing=False,
        #                                                 values=["Value 1", "Value 2", "Value Long Long Long"])
        # self.optionmenu_1.grid(row=0, column=0, padx=20, pady=(20, 10))

        # self.optionmenu_1 = customtkinter.CTkOptionMenu(self.tabview.tab("TAB-2"), dynamic_resizing=False,
        #                                                 values=["Value 1", "Value 2", "Value Long Long Long"])
        # self.optionmenu_1.grid(row=0, column=0, padx=20, pady=(20, 10))

        # self.optionmenu_1 = customtkinter.CTkOptionMenu(self.tabview.tab("TAB-3"), dynamic_resizing=False,
        #                                                 values=["Value 1", "Value 2", "Value Long Long Long"])
        # self.optionmenu_1.grid(row=0, column=0, padx=20, pady=(20, 10))

#?  LAYER-1
class MENU_FRAME(customtkinter.CTkFrame):
    def __init__(self, master,**kwargs):
        super().__init__(master,**kwargs)

        #? LAYER-2
        button = customtkinter.CTkButton(self,text="A",width=50,height=50,corner_radius=150)
        button.grid(row=0,column=0,padx=5, pady=20,sticky="n")
        button = customtkinter.CTkButton(self,text="B",width=50,height=50)
        button.grid(row=1,column=0,padx=5, pady=20)
        button = customtkinter.CTkButton(self,text="C",width=50,height=50)
        button.grid(row=2,column=0,padx=5, pady=20)
        button = customtkinter.CTkButton(self,text="D",width=50,height=50)
        button.grid(row=3,column=0,padx=5, pady=20,sticky="s")

#?  LAYER-1
class TERMINAL_FRAME(customtkinter.CTkFrame):
    def __init__(self, master,**kwargs):
        super().__init__(master,**kwargs)

        self.columnconfigure(0,weight=1)
        self.rowconfigure(0,weight=1)
        # text_frame = customtkinter.CTkFrame(self)
        # text_frame.grid(row=0,column=0,padx=10,pady=(10,10),sticky="nsew")

        self.tabview = customtkinter.CTkTabview(self,corner_radius=5,border_width=1)
        self.tabview.grid(row=0,column=0, padx=5, pady=0, sticky="nsew")
        self.tabview.add("TERMINAL")

#? MAIN-LAYER
class App(customtkinter.CTk):
    def __init__(self,Yer_istasyonu_obj=None):
        super().__init__()
        self.Yer_istasyonu_obj = Yer_istasyonu_obj

        self.title("ALGAN - GROUND CONTROL STATION")
        self.geometry("1920x1080")
        #self.wm_attributes("-fullscreen",True)

        self.rowconfigure(0,weight=3)
        self.rowconfigure(1,weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=4)
        self.grid_columnconfigure(2, weight=0)

        self.menu_frame = MENU_FRAME(master=self,width=150,corner_radius=0)
        self.main_frame = MAIN_GUI_FRAME(master=self,Yer_istasyonu_obj=Yer_istasyonu_obj)
        self.terminal_frame = TERMINAL_FRAME(master=self)
        self.companion_frame = COMPANION_FRAMES(master=self,width=500)

        self.menu_frame.grid(row=0,column=0,rowspan=2,pady=(0,20),sticky="nsw")
        self.main_frame.grid(row=0,column=1, padx=20, pady=20,sticky="nswe")
        self.terminal_frame.grid(row=1,column=1, padx=20, pady=20,sticky="nswe")
        self.companion_frame.grid(row=0,column=2,rowspan=2,padx=20,pady=20,sticky="nswe")
    
    def server_stat_check(self):
        #cp.fatal("UI-SERVERCHECK")
        self.after(2000, self.server_stat_check)

    def run(self):# Run the GUI event
        try:
            self.after(5000, self.server_stat_check)
            self.mainloop()
        except KeyboardInterrupt:
            print("KEYBOARD INTERRUPT\nKEYBOARD INTERRUPT\nKEYBOARD INTERRUPT\nKEYBOARD INTERRUPT\nKEYBOARD INTERRUPT\n")

#? Eski arayüz
class main_gui:
    def __init__(self,Yer_istasyonu_obj,server_manager) -> None:
        #GUI INIT
        self.root = tk.Tk()
        self.root.title("Ground Control Station")
        lock_img = tk.PhotoImage(file=os.getcwd()+'\\Savasan-iha\\Mustafa Berkay\\Resources\\lock.png')
        unlock_img = tk.PhotoImage(file=os.getcwd()+'\\Savasan-iha\\Mustafa Berkay\\Resources\\unlock.png')
        self.lock_img = lock_img.subsample(6, 6)
        self.unlock_img = unlock_img.subsample(6, 6)
        
        self.indicator_anasunucu = tk.Label(self.root, text="AnaSunucu", width=20, height=2, bg='red', font=('Helvetica', 12))
        self.indicator_yonelim = tk.Label(self.root, text="Yonelim", width=20, height=2, bg='red', font=('Helvetica', 12))
        self.indicator_mod = tk.Label(self.root, text="Mod", width=20, height=2, bg='red', font=('Helvetica', 12))
        self.indicator_kamikaze = tk.Label(self.root, text="Kamikaze", width=20, height=2, bg='red', font=('Helvetica', 12))
        self.indicator_UI_telem = tk.Label(self.root, text="UI_Telem", width=20, height=2, bg='red', font=('Helvetica', 12))
        self.indicator_YKI_ONAY = tk.Label(self.root, text="YKI_Onay", width=20, height=2, bg='red', font=('Helvetica', 12))
        self.indicator1_MAV_PROXY = tk.Label(self.root, text="MavProxy", width=20, height=2, bg='red', font=('Helvetica', 12))
        self.send_button = tk.Button(self.root, text="ONAY VER/REDDET", image = self.lock_img, command=Yer_istasyonu_obj.yki_onay_ver, font=('Helvetica', 14))
        self.exit_button = tk.Button(self.root, text="EXIT YKI", command=self.close_all, font=('Helvetica', 14))
        self.exit_button.pack(pady=20)
        self.indicator_anasunucu.pack(pady=10)
        self.indicator_yonelim.pack(pady=10)
        self.indicator_mod.pack(pady=10)
        self.indicator_kamikaze.pack(pady=10)
        self.indicator_UI_telem.pack(pady=10)
        self.indicator_YKI_ONAY.pack(pady=10)
        self.indicator1_MAV_PROXY.pack(pady=10)
        self.send_button.pack(pady=20)
        
        self.Yer_istasyonu_obj = server_manager
        self.Yer_istasyonu_obj = Yer_istasyonu_obj

    def server_status_check(self):
        if self.Yer_istasyonu_obj.Yki_onayi_verildi:
            self.send_button.config(image=self.unlock_img)
        else:
            self.send_button.config(image=self.lock_img)

        if self.Yer_istasyonu_obj.ana_sunucu_status:
            self.indicator_anasunucu.config(bg='green')
        else:
            self.indicator_anasunucu.config(bg='red')
        
        if self.Yer_istasyonu_obj.Yönelim_sunucusu:
            self.indicator_yonelim.config(bg='green')
        else:
            self.indicator_yonelim.config(bg='red')

        if self.Yer_istasyonu_obj.kamikaze_sunucusu:
            self.indicator_mod.config(bg='green')
        else:
            self.indicator_mod.config(bg='red')

        if self.Yer_istasyonu_obj.kamikaze_sunucusu:
            self.indicator_kamikaze.config(bg='green')
        else:
            self.indicator_kamikaze.config(bg='red')

        if self.Yer_istasyonu_obj.UI_telem_sunucusu:
            self.indicator_UI_telem.config(bg='green')
        else:
            self.indicator_UI_telem.config(bg='red')

        if self.Yer_istasyonu_obj.YKI_ONAY_sunucusu:
            self.indicator_YKI_ONAY.config(bg='green')
        else:
            self.indicator_YKI_ONAY.config(bg='red')

        if self.Yer_istasyonu_obj.MAV_PROXY_sunucusu:
            self.indicator1_MAV_PROXY.config(bg='green')
        else:
            self.indicator1_MAV_PROXY.config(bg='red')
        
        # Schedule the next update
        self.root.after(1000, self.server_status_check)

    def close_all(self):
        print("GUI: ('close_all') CALLED")
        yer_istasyonu_obj.trigger_event(event_number=10,message="stop_capture")
        time.sleep(3)
        yer_istasyonu_obj.SHUTDOWN_KEY = "ALGAN"
        self.root.destroy()

    def run(self):# Run the GUI event
        try:
            self.root.after(500, self.server_status_check)
            self.root.mainloop()
        except KeyboardInterrupt:
            print("KEYBOARD INTERRUPT\nKEYBOARD INTERRUPT\nKEYBOARD INTERRUPT\nKEYBOARD INTERRUPT\nKEYBOARD INTERRUPT\n")

if __name__ == "__main__":
    app = App()
    app.mainloop()
