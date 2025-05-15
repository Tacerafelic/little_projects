import customtkinter as ctk
from tkinter import filedialog, Canvas
import tkinter as tk
from PIL import Image, ImageTk
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from CTkToolTip import *


METHODS_DICT = {
    "AREA": cv.INTER_AREA,
    "CUBIC": cv.INTER_CUBIC,
    "LINEAR": cv.INTER_LINEAR,
    "LANCZOS4": cv.INTER_LANCZOS4,
    "NEAREST": cv.INTER_NEAREST,
}


# Tooltip-Klasse
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tipwindow or not self.text:
            return
        x, y, _cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + cy + self.widget.winfo_rooty() + 25
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw,
            text=self.text,
            justify="left",
            background="#ffffe0",
            relief="solid",
            borderwidth=1,
            font=("Arial", 10),
        )
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None


class ImageApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode(
            "dark"
        )  # Währe schon nice wenn man wählen könnte zwischen light, dark und barbie mode
        ctk.set_default_color_theme("dark-blue")
        self.geometry("1200x800")
        self.title("TK 33 34 Bildbearbeitung")
        self.minsize(800, 500)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=2, uniform="a")
        self.columnconfigure(1, weight=3, uniform="a")

        self.init_parameters()

        self.image_import = ctk.CTkButton(
            self, text="Open Image", command=self.open_dialog
        )  # Anfangsbutton
        self.image_import.grid(column=0, columnspan=2, row=0)

        self.mainloop()

    def init_parameters(
        self,
    ):  # Bearbeitungsmethoden. Momentan nur effects also Interpolationsmethoden
        self.effect_vars = {
            "method": ctk.StringVar(value="AREA"),  # Default-Methode
            "scale": 1.0,
        }
        self.selection = None
        self.image = None

    def changeMode(self):
        val = (
            self.switch_mode.get()
        )  # wenn jemand unbedingt den light modus verwenden muss....
        if val:
            ctk.set_appearance_mode("light")
        else:
            ctk.set_appearance_mode("dark")

    def open_dialog(
        self,
    ):  # Logik hinter dem Anfangsbutton. öffnet einfach den explorer. selbsterklärend
        file = filedialog.askopenfilename()
        if file:
            self.load_image(file)

    def load_image(self, path):
        self.image = cv.imread(path)
        self.original = self.image.copy()
        self.image = cv.cvtColor(self.image, cv.COLOR_BGR2RGB)
        self.image_pil = Image.fromarray(self.image)
        self.image_tk = ImageTk.PhotoImage(self.image_pil)

        # Vorherige Canvas-Elemente entfernen
        if hasattr(self, "canvas_frame"):
            self.canvas_frame.destroy()
        if hasattr(self, "canvas_fin"):
            self.canvas_fin.destroy()

        # Canvas-Frame mit Scrollbars
        self.canvas_frame = ctk.CTkFrame(self)
        self.canvas_frame.grid(row=0, column=1, rowspan=2, sticky="nsew")

        self.scroll_canvas = Canvas(
            self.canvas_frame,
            width=800,
            height=600,
            bg="grey",
            bd=0,
            relief="ridge",
            highlightthickness=0,
            scrollregion=(0, 0, self.image.shape[1], self.image.shape[0]),
        )
        self.scroll_canvas.grid(row=0, column=0, sticky="nsew")

        # Scrollbars hinzufügen
        x_scroll = tk.Scrollbar(
            self.canvas_frame, orient="horizontal", command=self.scroll_canvas.xview
        )
        x_scroll.grid(row=1, column=0, sticky="ew")
        y_scroll = tk.Scrollbar(
            self.canvas_frame, orient="vertical", command=self.scroll_canvas.yview
        )
        y_scroll.grid(row=0, column=1, sticky="ns")

        self.scroll_canvas.configure(
            xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set
        )

        # Bild einfügen
        self.scroll_canvas.create_image(0, 0, anchor="nw", image=self.image_tk)

        # Interaktion aktivieren
        self.scroll_canvas.bind("<ButtonPress-1>", self.on_press)
        self.scroll_canvas.bind("<B1-Motion>", self.on_drag)
        self.scroll_canvas.bind("<ButtonRelease-1>", self.on_release)

        self.canvas = self.scroll_canvas  # Referenz für spätere Methoden

        ########################################################
        # Logik hinter dem Menü hier sind alle Buttons
        ########################################################

        self.menu = ctk.CTkTabview(self)
        self.menu.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.menu.add("Position")
        self.menu.add("Save")

        # self.switch_lan = ctk.CTkSwitc
        self.switch_mode = ctk.CTkSwitch(
            self.menu.tab("Position"),
            text="Light Mode",
            onvalue=1,
            offvalue=0,
            command=self.changeMode,
        )
        self.switch_mode.place(relx=0.1, rely=0.01, anchor="nw")

        self.clear_button = ctk.CTkButton(
            self.menu.tab("Position"),
            text="x",
            text_color="grey",
            command=self.clear_image,
            fg_color="transparent",
            hover_color="red",
            width=20,
            height=20,
        )
        self.clear_button.place(relx=0.99, rely=0.01, anchor="ne")

        self.clear_button_save = ctk.CTkButton(
            self.menu.tab("Save"),
            text="x",
            text_color="grey",
            command=self.clear_image,
            fg_color="transparent",
            hover_color="red",
            width=20,
            height=20,
        )
        self.clear_button_save.place(
            relx=0.99, rely=0.01, anchor="ne"
        )  # side="right", pady=20, padx=20, anchor="ne"

        ctk.CTkLabel(self.menu.tab("Position"), text="Scaling Method:").place(
            relx=0.1, rely=0.1
        )
        self.method_menu = ctk.CTkOptionMenu(
            self.menu.tab("Position"),
            variable=self.effect_vars["method"],
            values=list(METHODS_DICT.keys()),
        )
        self.method_menu.place(relx=0.4, rely=0.1)

        ctk.CTkLabel(self.menu.tab("Position"), text="Scale:").place(
            relx=0.1, rely=0.15
        )
        self.scale_entry = ctk.CTkEntry(self.menu.tab("Position"))
        self.scale_entry.place(relx=0.4, rely=0.15)
        self.scale_entry.insert(0, "1.0")

        self.label_doc = ctk.CTkLabel(
            self.menu.tab("Position"),
            wraplength=200,
            text="Bevor Sie eine Methode anwenden können, müssen Sie einen Bereich im Bild auswählen. Klicken Sie dafür einfach ins Bild und ziehen Sie einen Bereich.",
            pady=10,
        )

        self.label_doc.place(relx=0.3, rely=0.5)

        self.apply_button = ctk.CTkButton(
            self.menu.tab("Position"), text="Apply", command=self.apply_resize
        )
        self.apply_button.place(relx=0.17, rely=0.3)

        self.compare_button = ctk.CTkButton(
            self.menu.tab("Position"),
            text="Compare ALL Methods",
            command=self.compare_methods,
        )
        self.compare_button.place(relx=0.53, rely=0.3)

        # self.sup_button = ctk.CTkButton(self.menu.tab('Save'), text="", command=self.suprise)
        # self.sup_button.pack()  # wenn keine weiteren buttons/ anderes zeugs padx = 10, pady = 250

        self.save_button = ctk.CTkButton(
            self.menu.tab("Save"), text="Save ALL", command=self.save_image
        )
        self.save_button.place(relx=0.35, rely=0.1)

        self.tooltip_1 = CTkToolTip(
            self.save_button,
            delay=0.3,
            message="Speichert alles, was aktuell angezeigt wird inklusive Achsen und Beschriftungen.",
        )

        self.save_methods_button = ctk.CTkButton(
            self.menu.tab("Save"),
            text="Save Method",
            command=self.save_selected_subplot,
        )
        self.save_methods_button.place(relx=0.5, rely=0.2)

        self.subplot_choice = ctk.IntVar(value=1)  # Standard: 1. Subplot

        # Switch-Button hinzufügen
        self.switch_button = ctk.CTkSwitch(
            self.menu.tab("Save"),
            text="Original/Method",
            variable=self.subplot_choice,
            onvalue=2,
            offvalue=1,
        )
        self.switch_button.place(relx=0.13, rely=0.2)

        self.tooltip_2 = CTkToolTip(
            self.save_methods_button,
            delay=0.3,
            message="Speichert nur das reine Bild der Grafik ohne weitere Anzeigeelemente. \n Nur mit zwei Graphen auswählbar",
        )

        # self.label_doc_save = ctk.CTkLabel(
        #     self.menu.tab('Save'),
        #     wraplength=200,
        #     text="Die Speichermethoden unterscheiden sich!!! Bei Save können Sie die Grafik (also mit den Achsen usw.) speichern. Die zweite Speicherfunktion ermöglicht das Speichern der Vergrößerungen an sich. Achtung: Diese Option ist nur bei zwei Grafiken mögliche.",
        #     pady=10,
        # )

        # self.label_doc_save.place(relx = 0.3, rely = 0.5)

    ######################################
    # neues Fenster für .... i dont know. just in case (143) i guess ?
    def suprise(self):
        extra_window = ctk.CTkToplevel()
        extra_window.geometry("300x400")

    def clear_image(
        self,
    ):  # Logik hinter clear button. falls das falsche Bild ausgewählt wurde, oder wenn man ein weiteres bearbeiten möchte.
        if self.canvas:
            self.canvas.destroy()
            self.menu.destroy()
            self.canvas_fin.destroy()
        self.image = None

    def on_press(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.canvas.delete("selection")
        self.selection = [x, y, x, y]

    def on_drag(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.selection[2] = x
        self.selection[3] = y

    def on_release(self, event):
        x1, y1, x2, y2 = self.selection
        x1, x2 = sorted([x1, x2])
        y1, y2 = sorted([y1, y2])
        self.selection = [x1, y1, x2, y2]
        self.canvas.create_rectangle(
            x1, y1, x2, y2, outline="red", width=5, tags="selection"
        )

    def apply_resize(
        self,
    ):  # Hier werden die Interpoliermethoden bzw. eine davon angewendet
        if not self.selection or self.image is None:
            return

        x1, y1, x2, y2 = self.selection
        cropped = self.original[y1:y2, x1:x2]
        cropped_color = cv.cvtColor(cropped, cv.COLOR_BGR2RGB)

        scale = float(self.scale_entry.get())
        width, height = cropped_color.shape[1], cropped_color.shape[0]
        new_width, new_height = int(width * scale), int(height * scale)

        method_name = self.effect_vars["method"].get()
        method = METHODS_DICT[method_name]

        resized = cv.resize(
            cropped_color, (new_width, new_height), interpolation=method
        )
        # resized_color = cv.cvtColor(resized, cv.COLOR_BGR2RGB)
        self.canvas_fin.delete("all")

        self.fig_1, axes = plt.subplots(1, 2, figsize=(10, 5))
        axes[0].imshow(cropped_color)
        axes[0].set_title(f"Original ({width}x{height})")
        axes[1].imshow(resized)
        axes[1].set_title(f"{method_name} ({new_width}x{new_height})")
        # plt.show()
        canvas_1 = FigureCanvasTkAgg(self.fig_1, master=self.canvas_fin)
        canvas_1.draw()
        widget = canvas_1.get_tk_widget()
        widget.pack()

        self.method_fig, self.method_axes = plt.subplots(1, 2, figsize=(10, 5))

        # Links: Originalbild
        self.method_axes[0].imshow(cropped_color)
        self.method_axes[0].set_title("Original")
        self.method_axes[0].axis("off")

        # Rechts: Transformiertes Bild
        self.method_axes[1].imshow(resized)
        self.method_axes[1].set_title(method_name)
        self.method_axes[1].axis("off")

        self.method_fig.canvas.draw()

        if hasattr(self, "canvas_fin_image"):
            self.canvas_fin_image.get_tk_widget().destroy()
        self.canvas_fin_image = canvas_1

    def compare_methods(
        self,
    ):  # sollte sich Studi entscheiden alle gleichzeitig sehen zu wollen, dann geht das hier. Basically der gleiche code wie oben, nur das hier WIRKLICH  alles dargestellt wird
        if not self.selection or self.image is None:
            return

        x1, y1, x2, y2 = self.selection
        cropped = self.original[y1:y2, x1:x2]
        cropped_color = cv.cvtColor(cropped, cv.COLOR_BGR2RGB)

        scale = float(self.scale_entry.get())
        width, height = cropped_color.shape[1], cropped_color.shape[0]
        new_width, new_height = int(width * scale), int(height * scale)

        methods = list(METHODS_DICT.values())
        titles = list(METHODS_DICT.keys())

        self.canvas_fin.delete("all")

        self.fig_1, axes = plt.subplots(2, 3, figsize=(15, 10))
        axes[0, 0].imshow(cropped_color)
        axes[0, 0].set_title(f"Original ({width}x{height})")

        for i, method in enumerate(methods):
            resized = cv.resize(cropped, (new_width, new_height), interpolation=method)
            resized_color = cv.cvtColor(resized, cv.COLOR_BGR2RGB)
            ax = axes[(i + 1) // 3, (i + 1) % 3]
            ax.imshow(resized_color)
            ax.set_title(f"{titles[i]} ({new_width}x{new_height})")
        # plt.show()
        canvas_1 = FigureCanvasTkAgg(self.fig_1, master=self.canvas_fin)
        canvas_1.draw()
        widget = canvas_1.get_tk_widget()
        widget.pack()

        # Falls du das vorherige FigureCanvasTkAgg-Objekt speichern willst, um Speicherlecks zu vermeiden:
        if hasattr(self, "canvas_fin_image"):
            self.canvas_fin_image.get_tk_widget().destroy()
        self.canvas_fin_image = canvas_1

    def save_image(self):

        if not hasattr(self, "fig_1"):
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("PDF files", "*.pdf"),
            ],
        )

        if not file_path:
            return

        # Canvas als Bild speichern
        self.fig_1.savefig(file_path, dpi=300, bbox_inches="tight")
        print(f"Image saved as {file_path}")

    def save_selected_subplot(self):
        if not hasattr(self, "method_fig") or self.method_fig is None:
            print("Keine Methode-Subplots zum Speichern gefunden.")
            return

        # Datei-Speicher-Dialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("PDF files", "*.pdf"),
            ],
            title="Speichern als",
        )

        if not file_path:
            return

        selected_subplot_index = (
            self.subplot_choice.get() - 1
        )  # Index anpassen (0-basiert)

        # Alle Subplots abrufen
        axes = self.method_fig.axes

        if len(axes) <= selected_subplot_index:
            print("Nicht genug Subplots vorhanden.")
            return

        selected_ax = axes[selected_subplot_index]  # Gewählten Subplot abrufen

        # Neue leere Figure ohne Achsen
        new_fig, new_ax = plt.subplots(figsize=selected_ax.figure.get_size_inches())

        # Bild aus Subplot holen und übertragen
        image = selected_ax.get_images()[0]
        new_ax.imshow(
            image.get_array(),
            cmap=image.get_cmap(),
            vmin=image.get_clim()[0],
            vmax=image.get_clim()[1],
        )
        new_ax.axis("off")

        # Speichern
        new_fig.savefig(file_path, bbox_inches="tight", pad_inches=0, dpi=300)
        plt.close(new_fig)

        print(f"Subplot {selected_subplot_index + 1} gespeichert als {file_path}")


if __name__ == "__main__":  # öffnet ImageApp
    ImageApp()
