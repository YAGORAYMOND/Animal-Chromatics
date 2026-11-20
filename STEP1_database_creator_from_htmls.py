
"""
README

Welcome.

This script takes a folder path containing htmls as input 
Thers htmls are the result from a table query from 
https://animaldiversity.ummz.umich.edu/quaardvark/search/
and creates a csv table and places al the animal images in
a new folder named "animal_photos".

The aim is to overcome the fact that the original website allows to download
tables but no images. So instead of downloading follow these steps:

STEPS:
- 1. Create the animal query including the "Live Animal" (photo of the animal) column
- 2. Rigth button on the resulting table > save as > "animal_query.html"
- 3. This downloads an html and a folder with this same name
- 4. Place this folder and html in the same location with this script and execute the script.
- 5. Check that "animal_features.csv" and "animal_photos" folder is created in this same folder where the script is located.

El archivo python se ha de colocar al mismo nivel que la carpeta conteniendo los htmls.
"""

from bs4 import BeautifulSoup
import os
import shutil
import pandas as pd


#The file is locates
carpeta_htmls = "query_animaldiversity"

#Diccionari compost de diccionaris (anomenats registe), q cadascun es una entrada, i transformem al final en CSV
registres = []


#Recorro toda la carpeta para sacar los nombres de los htmls:
htmls = []
for nombre in os.listdir(carpeta_htmls):
    if nombre.endswith(".html"):
        htmls.append(nombre)

#Recorro la lista de htmls y proceso su contenido
for nombre_html in htmls:

    #Creo el path a partir del nombre de la carpeta y del html
    path_html = os.path.join(carpeta_htmls, nombre_html)

    #PARA CADA path_html, lo recorro y lo añado a la tabla.
    #obtenir html
    with open(path_html, "r", encoding="utf-8") as fitxer:
        html = fitxer.read()

    #li passo a beautifulsoup pq busqui la taula
    soup = BeautifulSoup(html, "html.parser")

    taula = soup.find("table", class_="tablesorter")

    #Creo una lista "cabeceras" con todos los headers de la tabla leyendo las etiquetas de cabecera del HTML ("th")
    cabeceras = []

    for cabecera in taula.find("thead").find_all("th"):
        cabeceras.append(cabecera.get_text(" ", strip=True))

    #restauro la taula
    cos_taula = taula.find("tbody")
    files = cos_taula.find_all("tr")

    print("Nombre de files:", len(files))

    #Creem el directori on guardar les imatges dels animals ("animal_photos"):
    os.makedirs("animal_photos", exist_ok=True) #exist_ok evita error si ja existeix i sobreescriu



    for fila in files:
        celles = fila.find_all("td")
        #averiguamos nombre especie para usar en nombre de las imagenes:
        especie = celles[0].get_text(strip=True)

        imatges = fila.find_all("img", class_="resource-frame")

        

        #Per cada imatge enregistro el fitxer amb el nom de l'animal a la carpeta "animal_photos"
        for numero, imatge in enumerate(imatges, start=1): #si n'hi ha ms d'un afegeixo un sequencial
            #Busca las imágenes dentro de la carpeta que contiene los htmls
            origen = os.path.join(carpeta_htmls, imatge["src"])

            nom_especie = especie.replace(" ", "_")
            extensio = os.path.splitext(origen)[1]
            nom_fitxer = f"{nom_especie}_{numero}{extensio}"

            desti = os.path.join("animal_photos", nom_fitxer)

            shutil.copy2(origen, desti)

            # Extraemos todos los atributos que nos interesan del html
            # y añadirlos a un diccionario 
            # que representa una fila/entrada final del csv

            registro = {
                "species": celles[cabeceras.index("Species")].get_text(strip=True),
                "class": celles[cabeceras.index("Class")].get_text(strip=True),
                "family": celles[cabeceras.index("Family")].get_text(strip=True),
                "order": celles[cabeceras.index("Order")].get_text(strip=True),

                "nearctic": celles[cabeceras.index("Nearctic :: Native")].get_text(strip=True),
                "palearctic": celles[cabeceras.index("Palearctic :: Native")].get_text(strip=True),
                "oriental": celles[cabeceras.index("Oriental :: Native")].get_text(strip=True),
                "ethiopian": celles[cabeceras.index("Ethiopian :: Native")].get_text(strip=True),
                "neotropical": celles[cabeceras.index("Neotropical :: Native")].get_text(strip=True),
                "australian": celles[cabeceras.index("Australian :: Native")].get_text(strip=True),
                "antarctica": celles[cabeceras.index("Antarctica :: Native")].get_text(strip=True),
                "oceanic_islands": celles[cabeceras.index("Oceanic Islands :: Native")].get_text(strip=True),
                "arctic_ocean": celles[cabeceras.index("Arctic Ocean :: Native")].get_text(strip=True),
                "indian_ocean": celles[cabeceras.index("Indian Ocean :: Native")].get_text(strip=True),
                "atlantic_ocean": celles[cabeceras.index("Atlantic Ocean :: Native")].get_text(strip=True),
                "pacific_ocean": celles[cabeceras.index("Pacific Ocean :: Native")].get_text(strip=True),
                "mediterranean_sea": celles[cabeceras.index("Mediterranean Sea :: Native")].get_text(strip=True),

                "temperate": celles[cabeceras.index("Temperate")].get_text(strip=True),
                "tropical": celles[cabeceras.index("Tropical")].get_text(strip=True),
                "polar": celles[cabeceras.index("Polar")].get_text(strip=True),
                "terrestrial": celles[cabeceras.index("Terrestrial")].get_text(strip=True),
                "saltwater_or_marine": celles[cabeceras.index("Saltwater or marine")].get_text(strip=True),
                "freshwater": celles[cabeceras.index("Freshwater")].get_text(strip=True),

                "tundra": celles[cabeceras.index("Tundra")].get_text(strip=True),
                "taiga": celles[cabeceras.index("Taiga")].get_text(strip=True),
                "desert_or_dune": celles[cabeceras.index("Desert or dune")].get_text(strip=True),
                "savanna_or_grassland": celles[cabeceras.index("Savanna or grassland")].get_text(strip=True),
                "chaparral": celles[cabeceras.index("Chaparral")].get_text(strip=True),
                "forest": celles[cabeceras.index("Forest")].get_text(strip=True),
                "rainforest": celles[cabeceras.index("Rainforest")].get_text(strip=True),
                "scrub_forest": celles[cabeceras.index("Scrub forest")].get_text(strip=True),
                "mountains": celles[cabeceras.index("Mountains")].get_text(strip=True),
                "icecap": celles[cabeceras.index("Icecap")].get_text(strip=True),

                "pelagic": celles[cabeceras.index("Pelagic")].get_text(strip=True),
                "benthic": celles[cabeceras.index("Benthic")].get_text(strip=True),
                "reef": celles[cabeceras.index("Reef")].get_text(strip=True),
                "oceanic_vent": celles[cabeceras.index("Oceanic vent")].get_text(strip=True),
                "lakes_and_ponds": celles[cabeceras.index("Lakes and Ponds")].get_text(strip=True),
                "rivers_and_streams": celles[cabeceras.index("Rivers and Streams")].get_text(strip=True),
                "temporary_pools": celles[cabeceras.index("Temporary Pools")].get_text(strip=True),
                "coastal": celles[cabeceras.index("Coastal")].get_text(strip=True),
                "abyssal": celles[cabeceras.index("Abyssal")].get_text(strip=True),
                "brackish_water": celles[cabeceras.index("Brackish Water")].get_text(strip=True),

                "marsh": celles[cabeceras.index("Marsh")].get_text(strip=True),
                "swamp": celles[cabeceras.index("Swamp")].get_text(strip=True),
                "bog": celles[cabeceras.index("Bog")].get_text(strip=True),

                "sexes_colored_or_patterned_differently": celles[cabeceras.index("Sexes colored or patterned differently")].get_text(strip=True),
                "polymorphic": celles[cabeceras.index("Polymorphic")].get_text(strip=True),
                "poisonous": celles[cabeceras.index("Poisonous")].get_text(strip=True),
                "venomous": celles[cabeceras.index("Venomous")].get_text(strip=True),

                "arboreal": celles[cabeceras.index("arboreal")].get_text(strip=True),
                "scansorial": celles[cabeceras.index("scansorial")].get_text(strip=True),
                "cursorial": celles[cabeceras.index("cursorial")].get_text(strip=True),
                "terricolous": celles[cabeceras.index("terricolous")].get_text(strip=True),
                "fossorial": celles[cabeceras.index("fossorial")].get_text(strip=True),
                "troglophilic": celles[cabeceras.index("troglophilic")].get_text(strip=True),
                "flies": celles[cabeceras.index("flies")].get_text(strip=True),
                "glides": celles[cabeceras.index("glides")].get_text(strip=True),
                "saltatorial": celles[cabeceras.index("saltatorial")].get_text(strip=True),
                "natatorial": celles[cabeceras.index("natatorial")].get_text(strip=True),
                "diurnal": celles[cabeceras.index("diurnal")].get_text(strip=True),
                "nocturnal": celles[cabeceras.index("nocturnal")].get_text(strip=True),
                "crepuscular": celles[cabeceras.index("crepuscular")].get_text(strip=True),
                "parasite": celles[cabeceras.index("parasite")].get_text(strip=True),
                "sessile": celles[cabeceras.index("sessile")].get_text(strip=True),
                "motile": celles[cabeceras.index("motile")].get_text(strip=True),
                "nomadic": celles[cabeceras.index("nomadic")].get_text(strip=True),
                "migratory": celles[cabeceras.index("migratory")].get_text(strip=True),
                "sedentary": celles[cabeceras.index("sedentary")].get_text(strip=True),
                "hibernation": celles[cabeceras.index("hibernation")].get_text(strip=True),
                "aestivation": celles[cabeceras.index("aestivation")].get_text(strip=True),
                "daily_torpor": celles[cabeceras.index("daily torpor")].get_text(strip=True),
                "solitary": celles[cabeceras.index("solitary")].get_text(strip=True),
                "territorial": celles[cabeceras.index("territorial")].get_text(strip=True),
                "social": celles[cabeceras.index("social")].get_text(strip=True),
                "colonial": celles[cabeceras.index("colonial")].get_text(strip=True),
                "dominance_hierarchies": celles[cabeceras.index("dominance hierarchies")].get_text(strip=True),

                "carnivore": celles[cabeceras.index("Carnivore")].get_text(strip=True),
                "herbivore": celles[cabeceras.index("Herbivore")].get_text(strip=True),
                "omnivore": celles[cabeceras.index("Omnivore")].get_text(strip=True),
                "planktivore": celles[cabeceras.index("Planktivore")].get_text(strip=True),
                "mycophage": celles[cabeceras.index("Mycophage")].get_text(strip=True),
                "detritivore": celles[cabeceras.index("Detritivore")].get_text(strip=True),
                "coprophage": celles[cabeceras.index("Coprophage")].get_text(strip=True),

                "mass_average_g": celles[cabeceras.index("Mass - average - g")].get_text(strip=True),
                "elevation_average_m": celles[cabeceras.index("Elevation - average - m")].get_text(strip=True),
                "length_average_mm": celles[cabeceras.index("Length - average - mm")].get_text(strip=True),
                "depth_average_m": celles[cabeceras.index("Depth - average - m")].get_text(strip=True),

                "image_path": desti,
                "image_number": numero
            }


            registres.append(registro)

            print(especie)
            print(desti)

#Crear CSV a partir de la llista de llistes: registres
df = pd.DataFrame(registres)
#veure el q has creat
print(df.head())
#enregistrar el csv amb el nom "animal_features.csv"
df.to_csv("animal_features.csv", index=False, encoding="utf-8-sig")


