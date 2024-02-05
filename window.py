from bs4 import BeautifulSoup
import requests
import os
import pathlib
from tkinter import *
from tkinter import messagebox 

photos = ['']*15

window = Tk()
window.title('Web scrapping')
window.geometry('')


def conectar(u:str):
    r = requests.get(u)   #Añado la URL al request
    while r.status_code != 200:
        print("No hay conexión")
    soup = BeautifulSoup(r.content, 'html.parser')  # Se obtiene todo el html, es decir, la informaicón del "Inspeccionar elemento"
    body = soup.body
    return body

def copiar(i):
    window.clipboard_clear()
    window.clipboard_append(photos[i])
def agregar(i):
    window.clipboard_append(", " + photos[i])
    
def save_image(folder: str, name:str, url:str):
    image_source = requests.get(url)
    
    suffix = pathlib.Path(url).suffix

    if suffix not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
        output = name + '.png'
    else:
        output = name + suffix
    
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    with open(f'{folder}{output}', 'wb') as file:
        file.write(image_source.content)
        #print(f'Succesfully downloaded: {output}') 
    
def datos():
    body = conectar(url.get())
    titulo = body.find('h1', attrs={"class":"ui-pdp-title"}).text #Encuentro el título y lo convierto a texto
    precios = body.findAll('span', class_='andes-money-amount ui-pdp-price__part andes-money-amount--cents-superscript andes-money-amount--compact')
    precio = precios[0].find('span', class_="andes-money-amount__fraction").text

    while True:
        try:
            marca = body.find('span', class_="andes-table__column--value").text
            break
        except:
            body = conectar(url.get())
            
    # --- Imágenes ---
    imgs = body.find_all(["span"], class_='ui-pdp-gallery__wrapper')
    path = nombre.get().replace(" ", "_") + "/"
    output_name = nombre.get().replace(" ", "_")

    i=0
    for img in imgs:
        #print(f"Foto {i+1}: " )
        output_name = output_name + str(i)
        try:
            x = img.find('img', class_="ui-pdp-image ui-pdp-gallery__figure__image")['src']
            save_image(path, output_name, x)
            x = x.replace("jpg", "webp")
            photos[i] = x
        except:
            try: 
                x = img.find('img', class_="ui-pdp-image ui-pdp-gallery__figure__image lazy-loadable")['data-src']
                x = x.replace("jpg", "webp")
                save_image(path, output_name, x)
                photos[i] = x
            except:
                print("No hay foto")
        i +=1
    #print()
    mostrar_valores(titulo,precio,marca,photos)
    
def mostrar_valores(t,p,b,im):
    title = Label(window,text=t,font=(14))
    price = Label(window,text=p,font=(14))
    brand = Label(window,text=b,font=(14))
    
    title.grid(row=2,column=1,padx=5,pady=5)
    price.grid(row=3,column=1,padx=5,pady=5)
    brand.grid(row=4,column=1,padx=5,pady=5)
    
    b2 = []
    b3 = []
    i=0
    for x in im:
        if x != "":
            images=Label(window,text=x,font=(5))
            images.grid(row=5+i,column=1,padx=5,pady=5)
            b=Button(window,command=lambda i=i: copiar(i),text='Copiar',font=(14))
            b_1=Button(window,command=lambda i=i: agregar(i),text='Agregar',font=(14))
            
            b2.append(b)
            b3.append(b_1)
            
            b2[i].grid(row=5+i,column=2,sticky=S)
            b3[i].grid(row=5+i,column=3,sticky=S)
        i+=1
        
    
    
     
l1=Label(window,text='URL:', font=(14))
l2=Label(window,text='Nombre: ', font=(14))
l1.grid(row=0,column=0,padx=5,pady=25)
l2.grid(row=1,column=0,padx=5,pady=5)

url=StringVar()
nombre=StringVar()

t1=Entry(window,textvariable=url,font=(14))
t2=Entry(window,textvariable=nombre,font=(14))
t1.grid(row=0,column=1,sticky=W)
t2.grid(row=1,column=1, sticky=W)


    
b1=Button(window,command=datos,text='Aceptar',font=(14))
b1.grid(row=0,column=3,sticky=E)

l3=Label(window,text="Título: ",font=(14))
l4=Label(window,text="Precio: ",font=(14))
l5=Label(window,text="Marca: ",font=(14))
l6=Label(window,text="Imágenes: ",font=(14))

l3.grid(row=2,column=0,padx=5,pady=5)
l4.grid(row=3,column=0,padx=5,pady=5)
l5.grid(row=4,column=0,padx=5,pady=5)
l6.grid(row=5,column=0,padx=5,pady=5)

window.mainloop()