import customtkinter
import tkinter
from tkintermapview import TkinterMapView
from PIL import Image, ImageTk
import PIL
import os

DARK_MODE = "dark"
customtkinter.set_appearance_mode(DARK_MODE)
customtkinter.set_default_color_theme("blue")

class App(customtkinter.CTk):

    APP_NAME = "Flight Tracker"
    WIDTH = 1240
    HEIGHT = 1080

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title(App.APP_NAME)
        self.geometry(str(App.WIDTH) + "x" + str(App.HEIGHT))
        self.minsize(App.WIDTH, App.HEIGHT)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind("<Command-q>", self.on_closing)
        self.bind("<Command-w>", self.on_closing)
        self.createcommand('tk::mac::Quit', self.on_closing)
        #self.wm_attributes('-fullscreen', True)

        # current_path = os.getcwd()+"\\Savasan-iha\\Mustafa Berkay\\Resources"
        # self.plane_image = ImageTk.PhotoImage(Image.open(os.path.join(current_path,"plane.png")).resize((40, 40)))
        # self.plane_circle_1_image = ImageTk.PhotoImage(Image.open(os.path.join(current_path,"plane_circle_1.png"))).resize((35, 35))
        # self.plane_circle_2_image = ImageTk.PhotoImage(Image.open(os.path.join(current_path,"plane_circle_2.png"))).resize((35, 35))

        current_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.plane_image = Image.open(os.path.join(current_path, "Resources", "plane.png")).resize((40, 40))
        self.plane_circle_1_image = ImageTk.PhotoImage(Image.open(os.path.join(current_path, "Resources", "plane_circle_1.png")).resize((35, 35)))
        self.plane_circle_2_image = ImageTk.PhotoImage(Image.open(os.path.join(current_path, "Resources", "plane_circle_2.png")).resize((35, 35)))

        self.marker_list = []
        
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_left = customtkinter.CTkFrame(master=self, width=150, corner_radius=0, fg_color=None)
        self.frame_left.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

        self.frame_mid = customtkinter.CTkFrame(master=self, corner_radius=0)
        self.frame_mid.grid(row=0, column=1, rowspan=1, pady=0, padx=0, sticky="nsew")

        self.frame_right = customtkinter.CTkFrame(master=self, width=150, corner_radius=0, fg_color=None)
        self.frame_right.grid(row=0, column=2, padx=0, pady=0, sticky="nsew")

        # ============ frame_left ============

        self.frame_left.grid_rowconfigure(8, weight=1)

        self.button_1 = customtkinter.CTkButton(master=self.frame_left,text="Set Marker",command=self.set_marker_event)
        self.button_1.grid(pady=(20, 0), padx=(20, 20), row=0, column=0)

        self.button_2 = customtkinter.CTkButton(master=self.frame_left,text="Clear Markers",command=self.clear_marker_event)
        self.button_2.grid(pady=(20, 0), padx=(20, 20), row=1, column=0)

        self.button_3 = customtkinter.CTkButton(master=self.frame_left,text="Empty Button")
        self.button_3.grid(pady=(20, 0), padx=(20, 20),row=2, column=0)

        self.button_4 = customtkinter.CTkButton(master=self.frame_left,text="Empty Button")
        self.button_4.grid(pady=(20, 0), padx=(20, 20),row=3, column=0)

        self.button_5 = customtkinter.CTkButton(master=self.frame_left,text="Empty Button")
        self.button_5.grid(pady=(20, 0), padx=(20, 20),row=4, column=0)

        self.button_6 = customtkinter.CTkButton(master=self.frame_left,text="Empty Button")
        self.button_6.grid(pady=(20, 0), padx=(20, 20),row=5, column=0)

        self.button_7 = customtkinter.CTkButton(master=self.frame_left,text="Empty Button")
        self.button_7.grid(pady=(20, 0), padx=(20, 20),row=6, column=0)

        self.button_8 = customtkinter.CTkButton(master=self.frame_left,text="Empty Button")
        self.button_8.grid(pady=(20, 0), padx=(20, 20),row=7, column=0)

        self.map_label = customtkinter.CTkLabel(self.frame_left, text="Tile Server:", anchor="w")
        self.map_label.grid(row=9, column=0, padx=(20, 20), pady=(20, 0))

        self.map_option_menu = customtkinter.CTkOptionMenu(self.frame_left, values=["OpenStreetMap", "Google normal", "Google satellite"],command=self.change_map)
        self.map_option_menu.grid(row=10, column=0, padx=(20, 20), pady=(10, 0))

        self.appearance_mode_label = customtkinter.CTkLabel(self.frame_left, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=11, column=0, padx=(20, 20), pady=(20, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.frame_left, values=["Dark","Light","System"],command=self.change_appearance_mode)
        self.appearance_mode_optionemenu.grid(row=12, column=0, padx=(20, 20), pady=(10, 20))

        # ============ frame_mid ============

        self.frame_mid.grid_rowconfigure(1, weight=1)
        self.frame_mid.grid_rowconfigure(0, weight=0)
        self.frame_mid.grid_columnconfigure(0, weight=1)
        self.frame_mid.grid_columnconfigure(1, weight=0)
        self.frame_mid.grid_columnconfigure(2, weight=1)

        database_path = "D:\\Visual Code File Workspace\\ALGAN\AlganYazilim\\Savasan-iha\\Mustafa Berkay\\Resources\\PoligonDenizli_tiles.db"
        script_directory = os.path.dirname(os.path.abspath(__file__))
        database_path = os.path.join(script_directory, "PoligonDenizli_tiles.db")

        self.map_widget = TkinterMapView(self.frame_mid, corner_radius=0,database_path=database_path)
        self.map_widget.grid(row=1, rowspan=1, column=0, columnspan=3, sticky="nswe", padx=(0, 0), pady=(0, 0))

        self.entry = customtkinter.CTkEntry(master=self.frame_mid,placeholder_text="type address")
        self.entry.grid(row=0, column=0, sticky="we", padx=(12, 0), pady=12)
        self.entry.bind("<Return>", self.search_event)

        self.button_5 = customtkinter.CTkButton(master=self.frame_mid,text="Search",width=90,command=self.search_event)
        self.button_5.grid(row=0, column=1, sticky="w", padx=(12, 0), pady=12)

        # ========== frame_right =============
        switch_1 = customtkinter.CTkSwitch(master=self.frame_right, text="Empty-Switch", onvalue="on", offvalue="off")
        switch_1.grid(pady=(20, 0), padx=(20, 20), row=0, column=0)

        switch_2 = customtkinter.CTkSwitch(master=self.frame_right, text="Empty-Switch", onvalue="on", offvalue="off")
        switch_2.grid(pady=(20, 0), padx=(20, 20), row=1, column=0)

        switch_3 = customtkinter.CTkSwitch(master=self.frame_right, text="Empty-Switch", onvalue="on", offvalue="off")
        switch_3.grid(pady=(20, 0), padx=(20, 20), row=2, column=0)

        switch_4 = customtkinter.CTkSwitch(master=self.frame_right, text="Empty-Switch", onvalue="on", offvalue="off")
        switch_4.grid(pady=(20, 0), padx=(20, 20), row=3, column=0)


        # Set default values
        #self.map_widget.set_address("Antalya")
        # self.map_option_menu.set("OpenStreetMap")
        # self.appearance_mode_optionemenu.set("Dark")

    def search_event(self, event=None):
        self.map_widget.set_address(self.entry.get())

    def set_marker_event(self):
        current_position = self.map_widget.get_position()
        self.marker_list.append(self.map_widget.set_marker(current_position[0], current_position[1]))

    def clear_marker_event(self):
        for marker in self.marker_list:
            marker.delete()

    def set_plane(self,lat,lon,rotation,plane_id="[id?]"):
        rotated_icon = ImageTk.PhotoImage(self.plane_image.rotate(360-rotation,PIL.Image.NEAREST,expand=1))
        return self.map_widget.set_marker(lat,lon,text=f'ID:{plane_id}',icon=rotated_icon)

    def delete_plane(self):
        pass

    def change_appearance_mode(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_map(self, new_map: str):
        if new_map == "OpenStreetMap":
            self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
        elif new_map == "Google normal":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=19)
        elif new_map == "Google satellite":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=19)

    def on_closing(self, event=0):
        self.destroy()

    def start(self):
        self.mainloop()

if __name__ == "__main__":
    app = App()
    app.start()
