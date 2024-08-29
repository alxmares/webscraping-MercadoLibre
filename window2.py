import customtkinter as ctk
from bs4 import BeautifulSoup
import requests
import os
import pathlib
import pandas as pd
from tkinter import filedialog, messagebox

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Web Scraping App")
        self.geometry("800x700")

        # Configuración de la grilla para que las columnas y filas se expandan correctamente
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(3, weight=2)

        # Variables
        self.titulo_var = ctk.StringVar()
        self.url = ctk.StringVar()
        self.nombre = ctk.StringVar()
        self.photos = []

        # Elementos de la interfaz
        self.create_widgets()
    
    def create_widgets(self):
        # Etiquetas y entradas
        ctk.CTkLabel(self, text='URL:', font=("Arial", 14)).grid(row=0, column=0, padx=20, pady=10, sticky="w")
        ctk.CTkEntry(self, textvariable=self.url, font=("Arial", 14)).grid(row=0, column=1, padx=20, pady=10, sticky="ew")

        ctk.CTkLabel(self, text='Nombre:', font=("Arial", 14)).grid(row=1, column=0, padx=20, pady=10, sticky="w")
        ctk.CTkEntry(self, textvariable=self.nombre, font=("Arial", 14)).grid(row=1, column=1, padx=20, pady=10, sticky="ew")

        # Botón para obtener datos
        ctk.CTkButton(self, text='Aceptar', command=self.datos, font=("Arial", 14)).grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="ew")

        # Frame para resultados
        self.frame = ctk.CTkFrame(self)
        self.frame.grid(row=3, column=0, columnspan=2, padx=20, pady=20, sticky="nsew")

    def conectar(self, u: str):
        r = requests.get(u)
        while r.status_code != 200:
            print("No hay conexión")
            r = requests.get(u)
        soup = BeautifulSoup(r.content, 'html.parser')
        return soup.body

    def datos(self):
        body = self.conectar(self.url.get())
        
        # Encuentro el título y lo convierto a texto, permitiendo editarlo
        titulo_auto = body.find('h1', attrs={"class": "ui-pdp-title"}).text.strip()
        self.titulo_var.set(titulo_auto)
        
        precios = body.findAll('span', class_='andes-money-amount ui-pdp-price__part andes-money-amount--cents-superscript andes-money-amount--compact')
        precio = precios[0].find('span', class_="andes-money-amount__fraction").text.strip()

        marca = None
        while not marca:
            try:
                marca = body.find('span', class_="andes-table__column--value").text.strip()
            except:
                body = self.conectar(self.url.get())

        # Buscar imágenes en las etiquetas <figure> con la clase específica
        imgs = body.find_all("figure", class_='ui-pdp-gallery__figure')

        self.photos = []  # Reinicia la lista de URLs de imágenes

        for img in imgs:
            img_tag = img.find('img', class_="ui-pdp-image ui-pdp-gallery__figure__image")
            if not img_tag:
                img_tag = img.find('img', class_="ui-pdp-image ui-pdp-gallery__figure__image lazy-loadable")

            if img_tag and 'data-zoom' in img_tag.attrs:
                x = img_tag['data-zoom']
                self.photos.append(x)
            else:
                print("No se encontró la imagen en formato JPG.")

        self.mostrar_valores(titulo_auto, precio, marca, self.photos)

    def mostrar_valores(self, t, p, b, im):
        for widget in self.frame.winfo_children():
            widget.destroy()
        
        ctk.CTkLabel(self.frame, text=f"Título: {t}", font=("Arial", 14)).grid(row=0, column=0, padx=20, pady=10, sticky="nsew")
        ctk.CTkLabel(self.frame, text=f"Precio: {p}", font=("Arial", 14)).grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        ctk.CTkLabel(self.frame, text=f"Marca: {b}", font=("Arial", 14)).grid(row=2, column=0, padx=20, pady=10, sticky="nsew")

        for i, x in enumerate(im):
            if x != "":
                ctk.CTkLabel(self.frame, text=x, font=("Arial", 12)).grid(row=3 + i, column=0, padx=5, pady=5, sticky="w")
                ctk.CTkButton(self.frame, text='Copiar', command=lambda i=i: self.copiar(i)).grid(row=3 + i, column=1, padx=5, pady=5)
                ctk.CTkButton(self.frame, text='Agregar', command=lambda i=i: self.agregar(i)).grid(row=3 + i, column=2, padx=5, pady=5)
        
        # Botón para guardar en CSV o Excel
        ctk.CTkButton(self.frame, text='Guardar en CSV/Excel', command=self.export_data, font=("Arial", 14)).grid(row=3 + len(im), column=0, padx=20, pady=10, sticky="ew")

        # Botón para guardar imágenes
        ctk.CTkButton(self.frame, text='Guardar Imágenes', command=self.guardar_imagenes, font=("Arial", 14)).grid(row=4 + len(im), column=0, padx=20, pady=10, sticky="ew")

        # Botón para volver a buscar artículos
        ctk.CTkButton(self.frame, text='Volver a Buscar', command=self.reset_busqueda, font=("Arial", 14)).grid(row=5 + len(im), column=0, padx=20, pady=10, sticky="ew")

        # Actualizar tamaño de ventana según contenido
        self.update_idletasks()
        current_width = self.winfo_width()
        current_height = self.winfo_height()
        new_height = min(max(self.winfo_height(), 1200), 1200)  # Ajusta la altura dentro del rango permitido
        print(self.winfo_width(), self.winfo_width())
        print(current_height, new_height)
        #self.geometry(f"{current_width}x{new_height}")


    def copiar(self, i):
        self.clipboard_clear()
        self.clipboard_append(self.photos[i])

    def agregar(self, i):
        self.clipboard_append(", " + self.photos[i])

    def guardar_imagenes(self):
        directory = filedialog.askdirectory(title="Seleccionar Directorio")
        if directory:
            for i, url in enumerate(self.photos):
                if url:
                    try:
                        suffix = pathlib.Path(url).suffix
                        image_name = f"image_{i+1}{suffix}"
                        image_path = os.path.join(directory, image_name)

                        image_source = requests.get(url)
                        with open(image_path, 'wb') as file:
                            file.write(image_source.content)
                        print(f"Imagen guardada en: {image_path}")
                    except Exception as e:
                        print(f"Error al guardar la imagen {url}: {e}")
        else:
            print("Directorio no seleccionado.")

    def export_data(self):
        # Crear DataFrame con URLs de imágenes en una sola columna
        data = pd.DataFrame({
            'Título': [self.titulo_var.get()],
            'Precio': [self.url.get()],
            'Marca': [self.nombre.get()],
            'Imágenes': [', '.join(self.photos)]
        })
        file_type = filedialog.asksaveasfilename(defaultextension='.csv',
                                                 filetypes=[('CSV files', '*.csv'), ('Excel files', '*.xlsx')],
                                                 title="Guardar archivo")
        if file_type:
            try:
                if file_type.endswith('.csv'):
                    if os.path.exists(file_type):
                        data.to_csv(file_type, mode='a', header=False, index=False)
                    else:
                        data.to_csv(file_type, index=False)
                else:
                    if os.path.exists(file_type):
                        with pd.ExcelWriter(file_type, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
                            data.to_excel(writer, index=False, header=False, startrow=writer.sheets['Sheet1'].max_row)
                    else:
                        data.to_excel(file_type, index=False)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo: {e}")
        else:
            print("Archivo no seleccionado.")

    def reset_busqueda(self):
        self.url.set("")
        self.nombre.set("")
        self.titulo_var.set("")
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.create_widgets()

if __name__ == "__main__":
    app = App()
    app.mainloop()
