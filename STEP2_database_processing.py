import pandas as pd


# Leer csv
animal_features = pd.read_csv("animal_features.csv")



#1. Transformar todos los "YES" a "True":
animal_features = animal_features.replace("YES", True)



#2. Fusionar atributos que pertenecen a la misma categoria y que estan desplegados en mas de una columna

#Como se repite muchas veces el mismo proceso, lo transformo en función:
def group_categories(animal_features, columnas_a_unir, nombre_nueva_columna):
    
    columna_regiones_acumuladas = []

    #recorremos cada entrada (cad fila y cada indice de esta)
    for indice, fila in animal_features.iterrows():
        regiones = []

        #Recorrer columna de regiones y añadir regiones donde hay True
        for columna in columnas_a_unir:
            if fila[columna] == True:
                regiones.append(columna)

        # Añadir a la columna_regiones_acumuladas los resultados de la fila [lista de regiones]
        # en caso que no este vacia, sino pongo un None
        if regiones != []:
            columna_regiones_acumuladas.append(regiones)
        else:
            columna_regiones_acumuladas.append(None)

    #Creo columna categorica bibliographic"_regions y la lleno con los resultados
    animal_features[nombre_nueva_columna] = columna_regiones_acumuladas

    #Elimino las columnas redundantes
    animal_features = animal_features.drop(columns=columnas_a_unir)

    return animal_features


#2.1. Biogeographic Regions

columnas_regiones = [
    "nearctic",
    "palearctic",
    "oriental",
    "ethiopian",
    "neotropical",
    "australian",
    "antarctica",
    "oceanic_islands",
    "arctic_ocean",
    "indian_ocean",
    "atlantic_ocean",
    "pacific_ocean",
    "mediterranean_sea"
]


#Llamamos la función para agrupar las columnas "columnas_regiones" en una columna categorica "biogeographic_regions"
animal_features = group_categories(
    animal_features,
    columnas_regiones,
    "biogeographic_regions"
)


#2.2. Habitat Regions (mismo proceso)
columnas_habitat = [
    "temperate",
    "tropical",
    "polar",
    "terrestrial",
    "saltwater_or_marine",
    "freshwater"
]

animal_features = group_categories(
    animal_features,
    columnas_habitat,
    "habitat_regions"
)


#2.3. Terrestrial Biomes (mismo proceso)
columnas_terrestrial_biomes = [
    "tundra",
    "taiga",
    "desert_or_dune",
    "savanna_or_grassland",
    "chaparral",
    "forest",
    "rainforest",
    "scrub_forest",
    "mountains",
    "icecap"
]

animal_features = group_categories(
    animal_features,
    columnas_terrestrial_biomes,
    "terrestrial_biomes"
)


#2.4. Aquatic Biomes (mismo proceso)
columnas_aquatic_biomes = [
    "pelagic",
    "benthic",
    "reef",
    "oceanic_vent",
    "lakes_and_ponds",
    "rivers_and_streams",
    "temporary_pools",
    "coastal",
    "abyssal",
    "brackish_water"
]

animal_features = group_categories(
    animal_features,
    columnas_aquatic_biomes,
    "aquatic_biomes"
)

#2.5 Wetlands
columnas_wetlands = [
    "marsh",
    "swamp",
    "bog"
]

animal_features = group_categories(
    animal_features, 
    columnas_wetlands, 
    "wetlands"
)

# 2.6. Behaviour
# No tiene sentido agrupar todo con todo 
# Lo agrupo por subgrupos que me parecen coherentes:

# Activity Periods
columnas_activity_periods = [
    "diurnal", 
    "nocturnal", 
    "crepuscular"
]

animal_features = group_categories(
    animal_features, 
    columnas_activity_periods, 
    "activity_periods"
)


# Movement Types
columnas_movement_types = [
    "flies", 
    "glides", 
    "saltatorial",
    "natatorial", 
    "scansorial", 
    "cursorial"
]

animal_features = group_categories(
    animal_features, 
    columnas_movement_types, 
    "movement_types"
)


# Living Habits
columnas_living_habits = [
    "arboreal", 
    "terricolous", 
    "fossorial", 
    "troglophilic"
]

animal_features = group_categories(
    animal_features, 
    columnas_living_habits, 
    "living_habits"
)


# Seasonal Movements
columnas_seasonal_movements = [
    "nomadic", 
    "migratory", 
    "sedentary"
]

animal_features = group_categories(
    animal_features, 
    columnas_seasonal_movements, 
    "seasonal_movements"
)


# Dormancy
columnas_dormancy = [
    "hibernation", 
    "aestivation", 
    "daily_torpor"
]

animal_features = group_categories(
    animal_features, 
    columnas_dormancy, 
    "dormancy"
)


# Social Behaviors
columnas_social_behaviors = [
    "solitary", 
    "territorial", 
    "social",
    "colonial", 
    "dominance_hierarchies"
]

animal_features = group_categories(
    animal_features, 
    columnas_social_behaviors, 
    "social_behaviors"
)



# 2.7. Primary Diet
columnas_primary_diet = [
    "carnivore",
    "herbivore",
    "omnivore",
    "planktivore",
    "mycophage",
    "detritivore",
    "coprophage"
]

animal_features = group_categories(
    animal_features, 
    columnas_primary_diet, 
    "primary_diet"
)



# 3. Imspectionando Dtype veo que "mass_average_g" y "elevation_average_m" aparecen como object cuando son numericas.

animal_features.info()

# Las inspecciono y tras ver que no se tiene que sacar unidad ni modificar de ninguna manera, simplemente estan almacenadas
# en este formato las transformo a numerico:
animal_features["mass_average_g"] = pd.to_numeric(animal_features["mass_average_g"])
animal_features["elevation_average_m"] = pd.to_numeric(animal_features["elevation_average_m"])

#Reviso que todo este modificado, ya aparecen como float64, esta correcto.
animal_features.info()


# 4. Creo una columna de familia menos especifica agrupando la categoria "class": 

# Inspeccionar clases disponibles a rutear en el diccionario:
# print(sorted(animal_features["class"].dropna().unique()))

# Diccionario mapeo de grupo especifico a grupo general (clases del reino animal)
grupos_animales = {
    "Mammalia": "mammals",
    "Aves": "birds",
    "Reptilia": "reptiles",
    "Amphibia": "amphibians",
    "Actinopterygii": "fish",
    "Chondrichthyes": "fish",
    "Cephalaspidomorphi": "fish",
    "Sarcopterygii": "fish",
    "Insecta": "insects",
    "Craniata": "other_vertebrates"
}

#Creo la nueva columna grupos (general)
columna_grupos = []

for clase in animal_features["class"]:
    if pd.isna(clase) or clase in ["Not Assigned", "Not assigned"]:
        grupo = "unknown"
    elif clase in grupos_animales:
        grupo = grupos_animales[clase]
    else:
        grupo = "other_invertebrates"

    columna_grupos.append(grupo)

animal_features["animal_group"] = columna_grupos




# 5. Creo la columna de processing priority para decidir en que orden voy a procesar imagenes y saviendo que no tendre tiempo para
# procesar 17.800 imagenes en este proyecto.
# Tengo 3 consignas de orden:
# - Considerar una imagen de cada animal (procesar una imagen de cada animal image_number == 1 antes de empezar con la segunda etc.)
# - Ir analizando fotos alternadamente de diferente "class" == diferentes especies. Para no tener solo aves por ejemplo.
# - Crear un "documentation_score" para priorizar especies con mayor grado de documentación en el dataset (que luego sirvan para filtrar y ver diferencias visuales)


# 5.1. Documentation Score:
# Lo calculo como porcentaje de columnas de la entrada que estan llenas, cuanto mas llenas, mejor documentado.
# * Cuento las agrupaciones como una sola columna (ya que si pertenece a un grupo u otro igual nos cuenta como documentado en ese aspecto).
# * Excluyo las siguientes columnas que no tiene sentido contar.
columnas_excluded = [
    "species",
    "class",
    "family",
    "order",
    "image_path",
    "image_number"
]

#creo dataset para calculos donde saco las columas exluidas
columnas_score = animal_features.columns.drop(columnas_excluded)

#calculo del total de columnas consideradas
total_columnas = len(columnas_score)

#calculo suma de atributos notna()
sum_notna = animal_features[columnas_score].notna().sum(axis=1)

#calculo la columna de documentation_score como la el tanto por uno de columnas no vacias (notna())
animal_features["documentation_score"] = sum_notna / total_columnas

animal_features.info()
print(animal_features.head())


# 5.2. Crear una iteracion con niveles para calcular el processing priority.
# Para cada número de imagen (primero todas las 1, después las 2, etc.):
# - Ordenar los animales de cada grupo taxonómico por documentation_score descendente.
# - Seleccionar uno de cada grupo por turnos hasta agotarlos.
# Asignar a ese orden un processing_priority entero, consecutivo y único desde 1.


# Excluir los grupos residuales no identificados (suelen pertenecer a estas categorias los animales con muy pocos datos, poco utiles)
grupos_a_excluir = [
    "other_invertebrates",
    "other_vertebrates",
    "unknown"
]

# Guardo los indices en el orden de procesamiento
indices_ordenados = []

#El for de fuera es el de image_number para que sea el nivel mas alto de altenranza
for im_num in range(1, animal_features["image_number"].max() + 1):

    # Seleccionar las fotos con este número de imagen
    fotos = animal_features[animal_features["image_number"] == im_num]

    # Crear una lista por "animal_group", ordenada por score
    listas_por_clase = []

    for clase in sorted(fotos["animal_group"].fillna("unknown").unique()):

        #saltamos los elementos de clases a excluir de la iteración
        if clase in ["other_invertebrates", "other_vertebrates", "unknown"]:
            continue

        grupo = fotos[fotos["animal_group"].fillna("unknown") == clase]

        grupo = grupo.sort_values(
            by=["documentation_score", "species", "image_path"],
            ascending=[False, True, True]
            )

        #lista de indices de todos los elementos ordenados por score
        listas_por_clase.append(grupo.index.tolist())

    # Seleccionar una foto de cada clase por turno
    while any(listas_por_clase): # mientras tenga elementos alguna de las listas de animales separados por clase ("listas_por_clase")
        for lista in listas_por_clase: #recorro la lista para cada grupo
            if lista != []: # y si no esta vacia
                indice = lista.pop(0) #le saco y elimino el primer indice
                indices_ordenados.append(indice) #y lo añado al orden defnitivo de procesamiento (Que tiene en cuenta los grupos)

# Añadir las filas que todavía no tienen posición
for indice in animal_features.index:
    if indice not in indices_ordenados:
        indices_ordenados.append(indice)

# Ordenar las filas y asignar una prioridad única a cada fotografía
animal_features = animal_features.loc[indices_ordenados].copy()

#creo la nueva columna 
animal_features["processing_priority"] = range(1, len(animal_features) + 1)




# Seleccionar una foto de cada grupo por turno
while any(listas_por_clase):  # Mientras al menos una de las listas tenga elementos
    for lista in listas_por_clase:  # Recorrer la lista de cada grupo
        if lista != []:  # Si esta lista no está vacía
            indice = lista.pop(0)  # Extraer y eliminar su primer índice
            indices_ordenados.append(indice)  # Añadirlo al orden final de procesamiento




# 5. Guardar la tabla reultado:
animal_features.to_csv("animal_features_filtered.csv", index=False, encoding="utf-8-sig")