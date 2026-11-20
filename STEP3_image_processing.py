# Este script toma como input el csv creado "animal_features_filtered.csv" por STEP2_database_processing.py
# Y va procesando animal por animal siguiendo la lista de prioridades de la columna: "processing_priority"
# Esta pensado para que se ejecute en varios dias y no se repita el trabajo. 
# De forma que modificamos la tabla indicandosalta el procesamiento si la tabla indicando que imagenes se han procesado ya y estas se saltan si ya estan procesadas.

# Antes de ejecutar este script instala rembg
# pip install "rembg[gpu]"



#Imports:
import pandas as pd
import os
from PIL import Image #per guardar imatges uso pillow
from rembg import remove, new_session #funció de eliminar background q farem servir de rembg
import numpy as np
from sklearn.utils import shuffle
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt 



# Leer csv "animal_features_wt_colors" si ya existe y si no crearlo basandolo en animal_features_filtered
if not os.path.exists("animal_features_wt_colors.csv"):
    #si no existe cargo animal_features_filtered.csv como base
    animal_features_wt_colors = pd.read_csv("animal_features_filtered.csv")
    #y le añado una columna donde almacenaré las extracciones de colores caracterísicos
    animal_features_wt_colors["color"] = None
    animal_features_wt_colors["color_percentages"] = None
else:
    #si ya existe, simplemente la cargo
    animal_features_wt_colors = pd.read_csv("animal_features_wt_colors.csv")



# Viendo que la función rembg era muy lenta y despues de leer la documentación (https://github.com/danielgatis/rembg) veo que lo optimo es crear una sesión
# y reutilitzarla. Leer sección: "Batch processing with session reuse (recommended for performance)"
# Cargo el modelo U2Net una sola vez y reutilizo la sesión para todas las imágenes:
session = new_session("u2net")

#Función de quitar fondo de las fotos:
def remove_bkg(input_image_path, output_folder):
    
    """
    Dado el path a una imagen de una animal ("input_image_path" en formato .jpg) esta función le quita el fondo
    y guarda el resultado en la carpeta elegida "output_folder" con el mismo nombre de entrada y el apendice "_no_bkg"
    en formato .png (ya que lo requiere para la transparencia de la zona de fondo eliminada).
    La función devueñve el output path de la imagen creada "output_path"
    Esta función utiliza el rembg algorythm (https://github.com/danielgatis/rembg).

    """
    image_name = os.path.splitext(os.path.basename(input_image_path))[0] #extraure nom del doc sense extensió per afegir la ext "".png"
    output_path = os.path.join(output_folder, image_name + "_no_bkg.png") #IMPORTANT: output ha de ser PNG ja que rembg retorna png (amb transparencia)

    #si la imagen ya esta creada no repetimos el proceso
    if os.path.exists(output_path):
        return output_path

    #carreguem la imatge
    image = Image.open(input_image_path)

    #li treiem el fons amb rembg
    imatge_sense_fons = remove(image, session=session) #especificamos la sesión creada antes de llamar la función para aumentar eficiencia del proceso 

    #tanquem la imatge
    image.close()

    #si no existeix el output path que li donem el crea
    if not os.path.exists(output_path):
       #Create the new dir, 
        os.makedirs(output_folder, exist_ok=True) #exist_ok=True, pq no doni error si la carpeta ja existeix (Reexecute), salta el pas si ja existeix i prou. No elimina la existent. 

    #guarden la imatge sense fons al output path
    imatge_sense_fons.save(output_path)

    #print for cmd
    print(f"Image {image_name}_no_bkg.png created" )

    return output_path



def color_quantization_calculator(input_image_path, n_colors=5, verif=False):
    """
    Dado un path de imagen en formato png (output de la función remove_bkg()), 
    esta función aplica sobre ella un algoritmo kmeans para encontrar los el numero n_colors de clusters 
    así como su tamaño relativo que seria el porcentaje de apariencia.

    Args:
        input_image_path (str):     path de la imagen .png a procesar.

        n_colors:   define el numero de colores/clusters a los que queremos reducir la imágen. 
                    Para un mejemplo detallado del funcinoamiento ver el ejemplo en la documentación de
                    sklearn donde reducen de 96615 colores a 64. (https://scikit-learn.org/1.5/auto_examples/cluster/plot_color_quantization.html)
                    En esta función por defecto reduciremos a 5 clusters.

        verif:  Por defecto desactivado (False). Si se pone en True guarda una imagen en el directorio verif creado en el lugar de ejecución de la función
            con un plot de la imagen input y la salida de colores. Sirve para verificar el correcto funcionamiento como el nombre indica.

    Returns:

        colors: np array cpn n_colors (5) filas y tres columnas, una paa cada color R, G, B, con valores entre 0 y 1.

        percentages: np array conteniendo porcentajes de peso de cada una de las n clases/clusters predichas en la imagen (mismo orden)

    """
    #load the photo
    image_original = Image.open(input_image_path)

    # Convert to floats instead of the default 8 bits integer coding. Dividing by
    # 255 is important so that plt.imshow works well on float data (need to
    # be in the range [0-1])
    image = np.array(image_original, dtype=np.float64) / 255

    #cerrar imagen
    image_original.close()

    # Load Image and transform to a 2D numpy array (matrix with each pixel in a row and columns of 0=R, 1=G, 2=B, 3=A)
    # OBS: differs from the original example in the sense that is not an RGB image
    # The png image is in 4 channels (RGBA): red, green blue, alpha (transparència).
    # Therefore we check d==4 anf not d==3
    w, h, d = original_shape = tuple(image.shape)
    assert d == 4
    image_array = np.reshape(image, (w * h, d)) 

    # Extract lines to transform RGBA array to RGB array (as in the example)
    image_array = image_array[image_array[:, 3] > 0 ] #exclude/eliminate all the transparent pixels (alpha=0)
    alpha = image_array[:, 3] #para usar luego en los weights en los counts
    image_array = image_array[:, :3] #delete the column from the np array that contains the info from transparency (4th column of the np array)


    # Fit the KMeans model with the np_array, we sample 1000 px of the array, to reduce processing time.
    print("Fitting model on a small sub-sample of the data")
    # Antes tenia n_samples=1000 pero me ha dado errores en imagenes donde el animal es pequeño (una vez recortado de la imagen ocupa una zona pequeña) y no se llega a los 1000 pixeles 
    # por eso modifico para que no de error permitiendo que sea 1000 o en su defecto numero de px del array ya sin px transparente (len(image_array) despues de quitar px con alpha=0).
    n_samples = min(1000, len(image_array))
    print(input_image_path, "píxeles tras el filtro:", len(image_array), "n_samples:", n_samples) #CHECK
    image_array_sample = shuffle(image_array, random_state=0, n_samples=n_samples)
    kmeans = KMeans(n_clusters=n_colors, random_state=0).fit(image_array_sample)

    # Get labels for all points
    print("Predicting color indices on the full image (k-means)")
    labels = kmeans.predict(image_array)

    # In kmeans.cluster_centers_ all the labels of the cluster for each pixel are stored
    # we calculate the percentages that this represent for each cluster with respect to the total.
    # Añado lo de clip para forzar rango porque me sale un out of range por 9.359e-06(seria 0...)
    colors = np.clip(kmeans.cluster_centers_, 0.0, 1.0)
    # He identificado visualmente un exceso de pixels de color negro en las representaciones.
    # Atribuyo esto a pixels con un alpha muy cercano a 0 (muy transparentes) que aparecen como grises dada su transparencia
    # pero si no tienes en cuenta la opacidad sesgan mucho el resultado.
    # Como solución he considerado ponderar el conteo usando la opacidad (valor alfa del pixel) como peso, asi pesaran mas los pixeles
    # mas opacos de misma forma que ocurre en la percepcion del ojo. 
    # Añado a bincount: wights=alpha.
    counts = np.bincount(labels, weights = alpha,  minlength=n_colors)
    percentages = (counts/counts.sum())*100

        
    #Verification
    if verif:
        
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.subplots.html
        #Crear figura:
        f, (ax1, ax2) = plt.subplots(1, 2, figsize=(10,4))

        #Left: precessed image
        ax1.imshow(image)
        ax1.axis("off")

        #Right: cluster colors
        order = np.argsort(percentages)[::-1]
        i=0

        for index in order:
            percentage = percentages[index]
            color = colors[index]
            ax2.barh(0, percentage, left=i, color=color)
            i += percentage
        ax2.set_xlim(0, 100)
        ax2.set_xlabel("Percentages of appearenc of each color, arranged from bigger to lower (%)")
        ax2.set_yticks([]) #remove y ticks, no need

        plt.tight_layout()

        #Guardar figura:
        # compruevo si existe el directorio ya y si no existe lo creo
        os.makedirs("verif", exist_ok=True)
        # creo el path para guardar la img de verificación
        image_name = os.path.splitext(os.path.basename(input_image_path))[0]
        path_verif = os.path.join("verif", image_name + "_verif.png")
        plt.savefig(path_verif)
        plt.close(f)

    return colors, percentages



# Recorro el csv y voy ejecutando las funciones para cada entrada
# siguiendo el orden establecido en la columna "processing_priority".
# Pongo checks para no duplicar trabajo.

# En caso que no lo este ya, ordenamos el dataset por orden de prioridad de procesamiento
animal_features_wt_colors = animal_features_wt_colors.sort_values("processing_priority", ascending=True)

# Recorremos todas las entradas del dataset
for index, entrada in animal_features_wt_colors.iterrows():
    #en caso de que la entrada no este ya procesada
    if pd.isna(entrada["color"]) or pd.isna(entrada["color_percentages"]):
        # aplicamos la función para eliminar background y la guardamos en el fichero "animal_photos_no_bkg"
        # la aplico con try porque sino con un error de apertura se rompe la ejecución y no lo quiero así
        try:
            img_no_bkg_path = remove_bkg(entrada["image_path"], "animal_photos_no_bkg")
        except Exception as error:
            print(f"Error: {error} en {entrada["image_path"]}")
            continue

        # guardamos tambien su return en una variable que es el path de la imagen sin background
        # se la pasamos a la función color_quantization_calculator()
        # esta nos calcula los clores y porcentajes de estos y los retorna:
        colors, percentages = color_quantization_calculator(img_no_bkg_path, n_colors=5, verif=True)

        # Guardamos el resultado de los colores y porcentajes en las respectivas columnas
        # Transformamos los np array a lista y esta en str antes de almacenarlos en el dataframe (para que se almacenen en 1 posicion del csv, sino da problemas....)
        animal_features_wt_colors.loc[index, "color"] = str(colors.tolist())
        animal_features_wt_colors.loc[index, "color_percentages"] = str(percentages.tolist())

        #Guardar/actualizar los avances en el CSV a cada iteración por si se interrumpe no perder el trabajo
        animal_features_wt_colors.to_csv("animal_features_wt_colors.csv", index=False) #guardar sin indice como una columna en el csv