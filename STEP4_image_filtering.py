# Este script esta pensado para ser ejecutado varias veces combinado con el proceso de 
# filtrado manual.
# 
# La primera vez que se ejecuta crea las carpetas "verif_pending" y "verif_accepted" y
# hubica en "verif_pending" todas las imagenes candidatas a ser seleccionadas. Estas se 
# escogen con los siguientes criterios:
#  - Que no existan ya imagenes del mismo animal en "verif_accepted"
#  - Que tengan un mínimo de 1000 px (no ser excesivamente pequeñas) tras eliminar el fondo (alpha > 0)
#  - Propone imagenes del mimso animal en orden de image index 1 -> 2 -> 3 etc.
#
# El script esta pensado para ejecutarse una 1a vez y hacer la tarea de abrir "verif_pending"
# eliminar todas las imagenes que no son correctas (criterio visual, e.g. mala segmentación)
# y luego volver a ejecutar este script una 2a vez.
#
# La 2a vez (y posteriores veces) que el script se ejecuta, este mueve todas las imágenes que
# no se han eliminado de "verif_pending" hacia "verif_accepted".
# Adicionalmente, el script analiza que animales aún no aparecen en "verif_accepted" (sea por ejemplo
# porque su imagen se ha eliminado en la selección y no trnsferido a "verif accepted") y para estos
# casos, propone nuevas imagenes de estos animales y los pone en "verif_pending" para una 2a ronda
# de evaluación.
#
# El usuario deberia repetir este proceso de evaluación y ejecución del script hasta que ve que 
# no aparecen nuevas imágenes en el directorio "verif_pending"
#
# Adicionalmente este script crea un diccionario que se registra como csv con el record de 
# el estado de cada imagen. El archivo csv se llama: "registro_eliminadas_manualmente.csv" e incluye 
#   - Key : nombre de la imagen
#   - value: estado, puede ser "propuesta", "descartada", "no_propuesta", "aceptada"
#
# Adicionalemnte este script genera una nueva columna al dataset principal "animal_features_wt_colors.csv"
# llamada "Seleccionados" que contiene valores True / False para cada entrada indicando si estos
# se ubican en la carpeta "verif_accepted" (y por lo tanto estan seleccionados para el dataset final).

import os
import shutil
import pandas as pd
import numpy as np
from PIL import Image

# 1.CARGAR ARCHIVOS: 

#cargo la lista de todas las entradas
animal_features = pd.read_csv("animal_features_wt_colors.csv")

#si no existe creamos la carpeta "verif_accepted"
os.makedirs("verif_accepted", exist_ok=True)

#abrimos el "registro_eliminados_manualmente" si existe y sino lo creamos como lista vacia
if os.path.exists("registro_eliminadas_manualmente.csv"):
    registro_df = pd.read_csv("registro_eliminadas_manualmente.csv")
    #Transformamos de pandas df a lista:
    registro = dict(zip(registro_df["image"], registro_df["estado"]))
else:
    registro = {}

# creo verif_pending si no existe ya
os.makedirs("verif_pending", exist_ok=True)



# 2.DETECTAR FOTOS ELIMINADAS DE "verif_accepted" DESDE LA ÚLTIMA EJECUCIÓN (y actualizar en lista):

#recorro la lista
for image, estado in registro.items():
    #Si la imagen consta como "propuesta" (deberia estar en la lista)
    if estado == "propuesta":
        #calculo el path de la imagen en verif pending
        image_path = os.path.join("verif_pending", image)

        # si la imagen esta en verif_pending y no se ha eliminado tras la revisión
        # (asumiendo que entre 2 ejecuciones de este script tiene que haber una revisión de imagenes)
        # significa que se puede mover hacia "verif_accepted":
        if os.path.exists(image_path):
            destino = os.path.join("verif_accepted", image)
            shutil.move(image_path, destino)
            #y la registramos como "aceptada"
            registro[image] = "aceptada"
            print("imagen aceptada:", image)

        # si ya no esta significa que la hemos eliminada, la marcamos en la lista como descartada: 
        else:
            registro[image] = "descartada"
            print("imagen descartada:", image)


# 3. INCORPORAMOS EN LA LISTA "registro" TODAS LAS IAMGENES DE "verif" QUE NO ESTEN AÚN
# Esto es basicamente para inicializar la lista a la primera ejecución, en las posteriores si no se modifica verif no efectua cambios...

# Recorro todas las imagenes de la carpeta verif:
for image in os.listdir("verif"):
    #si la imagen no esta en el registro la añado como "no_propuesta"
    if image not in registro:
        registro[image] = "no_propuesta"


# 4. PROPONER UNA IMAGEN "propuesta" POR ANIMAL

#Creo una lista para consulta con todos los animales que ya tienen propuesta 
# (es decir q tienen una imagen con su nombre en la lista de registro y aparecen como "porpuesta")
animales_aceptados_o_propuestos = []
#recorro la lista:
for image, estado in registro.items():
    if estado == "aceptada":
        #extraigo el nombre del animal (sin numero de imagen ni etiqueta _no_bkg_verif)
        animal_sin_etiqueta = image.replace("_no_bkg_verif.png", "") #quito etiqueta e.g.: Velella_velella_4
        animal_name = animal_sin_etiqueta.rsplit("_", 1)[0] #quito numero de imagen e.g.: Velella_velella

        #si en alnimal no esta en la lista ya (pq hayan varias fotos de el), lo añadimos
        if animal_name not in animales_aceptados_o_propuestos:
            animales_aceptados_o_propuestos.append(animal_name)


#Siguiente paso es recorrer las fotos en orden 1->2->3 (sort_values)
#por eso ordeno el dataframe basado en la columna "image_number"
fotos_ordenadas = animal_features.sort_values("image_number")

#Y recorro estas fotos y analizo para cada una su estado y si han de ser propuestas:
for index, entrada in fotos_ordenadas.iterrows():

    #para cada entrada calculo su nombre (_no_bkg_verif.png) para comparar con la lista
    nombre_base = os.path.basename(entrada["image_path"])
    nombre_base = nombre_base.replace(".jpg", "") #e.g.: Velella_velella_4
    image = nombre_base + "_no_bkg_verif.png" #e.g.: Velella_velella_4_no_bkg_verif.png
    animal_name = nombre_base.rsplit("_", 1)[0] #e.g.: Velella_velella

    #si el animl ya esta propuesto, no hay que tocar nada:
    if animal_name in animales_aceptados_o_propuestos:
        continue

    #Solo analizamos las imagenes que estan en el registo
    #y que aún no han sido propuestas
    if image not in registro:
        continue

    if registro[image] != "no_propuesta":
        continue

    #Dentro de las entradas "no_propuesta" si estas son pequeñas (<1000px) las descartamos
    #Lo miramos en las imagenes sin fondo.
    #Esto lo tendriamos que haber descartado en el paso 3 pero no lo hice y lleva tanto tiempo recalcular
    #que es mas facil filtrar ahora:
    path_no_bkg = os.path.join("animal_photos_no_bkg", nombre_base + "_no_bkg.png")
    imagen = Image.open(path_no_bkg)
    pixeles = np.array(imagen)
    imagen.close()
    numero_pixeles = (pixeles[:, :, 3] > 0).sum()

    if numero_pixeles < 1000:
        registro[image] = "descartada"
        continue

    #Para las entradas que lleguen a este punto:
    #  - Que no tienen animal aceptado
    #  - Que no han sido propuestos
    #  - Que tienen la resolucion minima
    # las proponemos como candidatas haciendo una copia de la imagen de la carpteta "verif" a "verif_pending"
    origen = os.path.join("verif", image)
    destino = os.path.join("verif_pending", image)
    shutil.copy2(origen, destino)
    # ademas actualizamos la lsita de registro de no_propuesta -> propuesta
    registro[image] = "propuesta"
    # y las añadimos a animales propuestas
    animales_aceptados_o_propuestos.append(animal_name)



# 5. ACTUALIZAR LOS CAMBIOS

#Actualizamos la columna "seleccionados" del dataset "animal_features" con los archivos aceptados peresntes en la carpteta "verif_accepted"

#Inicializamos con toda la columna de seleccionados en false
animal_features["seleccionados"] = False
# Creamos una lista con todo los paths de las imagenes aceptadas (puestas en "verif_accepted")
imagenes_aceptadas = set(os.listdir("verif_accepted"))
# Recorremos la lista annimal_features
for index, entrada in animal_features.iterrows():
    #extraemos el nombre base
    nombre_base = os.path.basename(entrada["image_path"]).replace(".jpg", "")
    #le añadimos el sufijo "_no_bkg_verif.png" para comparar con los elementos de la lista imagenes_aceptadas
    image = nombre_base + "_no_bkg_verif.png"
    # en caso de que este nombre se encuentre en la lista, cambiamos a true la columna "seleccionados" para ese index.
    if image in imagenes_aceptadas:
        animal_features.loc[index, "seleccionados"] = True
#Guardamos el daataset "danimal features" con los cambios a csv
animal_features.to_csv("animal_features_wt_colors.csv", index=False)

#Gurardamos la lista "registro" al "registro_eliminadas_manualmente.csv" para poder volverla a conlsultar
#en proximas ejecuciones de este script
registro_df = pd.DataFrame(registro.items(), columns=["image", "estado"])
registro_df.to_csv("registro_eliminadas_manualmente.csv", index=False)



