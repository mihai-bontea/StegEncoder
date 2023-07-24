import tkinter.messagebox
import customtkinter
import pyperclip

from tkinter import filedialog
from functools import partial
from Controller import Controller

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

class GraphicalUserInterface(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.controller = Controller()

        self.configure_window()
        self.create_sidebar()

        self.create_tabview()
        self.set_encoding_tab()
        self.set_decoding_tab()
        self.set_default_values()
    
    def configure_window(self):
        self.title("StegEncoder")
        self.geometry(f"{900}x{580}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)
        self.grid_columnconfigure(3, weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

    def create_tabview(self):
        self.tabview = customtkinter.CTkTabview(self, width=250)
        self.tabview.grid(row=0, column=1, rowspan=3, padx=(0, 0), pady=(10, 0), sticky="nsew")
        self.tabview.add("Encode")
        self.tabview.add("Decode")
        self.tabview.tab("Encode").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Decode").grid_columnconfigure(0, weight=1)

    def create_sidebar(self):
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame,
                                                 text="StegEncoder\n📸📼🎬", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))
    
    def set_encoding_tab(self):
        self.encoding_lsb_option_menu = customtkinter.CTkOptionMenu(self.tabview.tab("Encode"),
                                                        values=["1", "2", "3", "4", "5", "6", "7", "8"])
        self.encoding_lsb_option_menu.grid(row=0, column=0, padx=(0, 250), pady=(10, 10))

        self.checkbox = customtkinter.CTkCheckBox(self.tabview.tab("Encode"), text="Use Encryption")
        self.checkbox.grid(row = 0, column = 0, padx=(250, 0), pady=(10, 10))

        self.encoding_file_selection_button = customtkinter.CTkButton(self.tabview.tab("Encode"), text="Select a file",
                                                                      command=self.encoding_upload_action)
        self.encoding_file_selection_button.grid(row=1, column=0, padx=(0, 250), pady=(10, 10))

        self.encoding_textbox = customtkinter.CTkTextbox(self.tabview.tab("Encode"), width=10)
        self.encoding_textbox.grid(row=2, column=0, padx=(150, 150), pady=(50, 50), sticky="nsew")

        self.encode_button = customtkinter.CTkButton(self.tabview.tab("Encode"), text="Encode",
                                                             command=partial(self.attempt_encode, self.encoding_textbox))
        self.encode_button.grid(row=1, column=0, padx=(250, 0), pady=(10, 10))

        self.copy_button = customtkinter.CTkButton(self.tabview.tab("Encode"), text="Copy key",
                                                   command=self.copy_to_clipboard_action)
        self.copy_button.grid(row=3, column=0, padx=(0, 0), pady=(10, 10))

        self.encode_result = customtkinter.CTkLabel(
            self.tabview.tab("Encode"), text="", font=customtkinter.CTkFont(size=12))

    def set_decoding_tab(self):
        self.decoding_lsb_option_menu = customtkinter.CTkOptionMenu(self.tabview.tab("Decode"),
                                                        values=["1", "2", "3", "4", "5", "6", "7", "8"])
        self.decoding_lsb_option_menu.grid(row=0, column=0, padx=(0, 250), pady=(10, 10))

        self.decoding_file_selection_button = customtkinter.CTkButton(self.tabview.tab("Decode"), text="Select a file",
                                                                      command=self.decoding_upload_action)
        self.decoding_file_selection_button.grid(row=1, column=0, padx=(0, 250), pady=(10, 10))

        self.decode_button = customtkinter.CTkButton(self.tabview.tab("Decode"), text="Decode",
                                                             command=self.attempt_decode)
        self.decode_button.grid(row=2, column=0, padx=(0, 250), pady=(10, 10))

        self.mask_label = customtkinter.CTkLabel(self.tabview.tab("Decode"), text="🔑 Encryption key:", anchor="w")
        self.mask_label.grid(row=0, column=0, padx=(250, 0), pady=(10, 0))

        self.mask_frame = customtkinter.CTkFrame(self.tabview.tab("Decode"), width=140, height=30)
        self.mask_frame.grid(row=1, column=0, padx=(250, 0), pady=(10, 10))
        self.decoding_mask = tkinter.StringVar()
        self.mask_entry = customtkinter.CTkEntry(self.mask_frame, textvariable=self.decoding_mask)
        self.mask_entry.grid(row=1, column=0, padx=(0, 0), pady=(0,0), sticky="we")

        self.decode_result = customtkinter.CTkLabel(
            self.tabview.tab("Decode"), text="", font=customtkinter.CTkFont(size=12))        
        self.decode_secret_message = customtkinter.CTkTextbox(self.tabview.tab("Decode"), width=10)

    def set_default_values(self):
        self.appearance_mode_optionemenu.set("Dark")
        self.scaling_optionemenu.set("100%")
        self.encoding_lsb_option_menu.set("LSBs used")
        self.decoding_lsb_option_menu.set("LSBs used")
        self.encode_button.configure(state="disabled")
        self.copy_button.configure(state="disabled")
        self.decode_button.configure(state="disabled")
        self.encoding_textbox.insert("0.0", "Write the secret message here...")

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def encoding_upload_action(self,event=None):
        self.encoding_filename = filedialog.askopenfilename()
        self.encode_button.configure(state="normal")
        self.copy_button.configure(state="disabled")
    
    def decoding_upload_action(self):
        self.decoding_filename = filedialog.askopenfilename()
        self.decode_button.configure(state="normal")
    
    def select_output_path(self, extension):
        return filedialog.asksaveasfilename(defaultextension=extension) 
    
    def copy_to_clipboard_action(self):
        pyperclip.copy(str(self.mask))

    def get_nr_LSBs_used(self, option_menu):
        try:
            nr_lsb_used = int(option_menu.get())
        except:
            return 1
        else:
            return nr_lsb_used

    def attempt_encode(self, input_textbox):
        secret_message = input_textbox.get(1.0, "end-1c")
        nr_lsb_used = self.get_nr_LSBs_used(self.encoding_lsb_option_menu)
        use_encryption = self.checkbox.get()
        self.mask, exception = \
            self.controller.handle_encode(self.encoding_filename, secret_message, nr_lsb_used, use_encryption, self.select_output_path)

        if exception is None:
            self.encode_result.configure(text="Encoding process done successfully.")
            if self.mask is not None:
                self.copy_button.configure(state="normal")

        else:
            self.encode_result.configure(text=str(exception))
            print(str(exception))
        
        self.encode_result.grid(row=4, column=0, padx=(0, 0), pady=(10, 10))
    
    def attempt_decode(self):
        nr_lsb_used = self.get_nr_LSBs_used(self.decoding_lsb_option_menu)
        decoding_mask = bytes.fromhex(self.decoding_mask.get())
        secret_message, exception = self.controller.handle_decode(self.decoding_filename, nr_lsb_used, decoding_mask)

        if exception is None:
            self.decode_result.configure(text="Decoding process done successfully.")
            self.decode_secret_message.insert("0.0", str(secret_message)[2:-1])
            self.decode_secret_message.grid(row=4, column=0, padx=(150, 150), pady=(50, 50), sticky="nsew")
        else:
            self.decode_result.configure(text=str(exception))

        self.decode_result.grid(row=3, column=0, padx=(0, 0), pady=(10, 10))


if __name__ == "__main__":
    gui = GraphicalUserInterface()
    gui.mainloop()