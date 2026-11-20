# Animal-Chromatics
A data visualisation project exploring the colour palettes of animal species and their relationship with the characteristics documented in Animal Diversity Web (ADW)

## Dataset
The data was obtainde from Animal Diversity Web (https://animaldiversity.org/) including the characteristics considered relevant for this study toguether with images of the animals for the extraction of its characteristic color palettes.

## Data processing:

### STEP1: Extraction of animal characteristics from ADW HTML files
The script `STEP1_database_creator_from_htmls.py` takes the html file of the result a query from Quaardavark query tool (https://animaldiversity.ummz.umich.edu/quaardvark/) and extracts the table information toguether with the images. The output is a CSV “animal_features.csv”  and a folder “animal_photos” containing the images of the species.

### STEP2: Cleaning and restructuring of the dataset
The dataset resulting from step 1 contains 88 extracted columns with unfolded categories with values Yes or empy. In the scrpit `STEP2_database_processing.py`, these colums are colapsed into 32 colums with mainly categorical variables. Additionally a column with stablishing a score for  processing priority is calculated (in case processing priorisaiton is needed). The result is saved in anew CSV: “animal_features_filtered.csv”  

## STEP3: Background removal and extraction of colour palettes
This script `STEP3_image_processing.py` opens the images listed on “animal_features_filtered.csv” (column image_path contains its path) and applies the rembg algorithm (https://github.com/danielgatis/rembg) to remove the images background. The resulting images are stored in a folder named “animal_photos_no_bkg”.

Example of a background removal:
<img width="560" height="190" alt="image" src="https://github.com/user-attachments/assets/35c558bb-5de0-4c6a-9405-410fbde089b5" />

Subsequently, the images with removed background are processed with clustering algorithm (k-means, scikit learn) to quantize them into 5 bins. The centroids of the clusters define the 5 characteristic colors of the animal. The algorthm is used to predict and label the pixels in the image (closest centroid) and then the proportions are counted to calcualte the percentage of each color in the palette. This information is stored in the variables "color" and "color_percentages", two new columns added to the dataframe. The dataframe is exported as “animal_features_wt_colors.csv”. Additionally, a verification image composed of the image without background and its characteristic pallete is calculated and stored in the folder "Verif".

Example of a verification image (left: segmented animal, right: calculated pallete)
<img width="563" height="235" alt="image" src="https://github.com/user-attachments/assets/003c630d-33cb-4f8f-9583-55f8120ae80d" />

## STEP 4: Manual validation and filtering of the extracted palettes
While reviewing the verification images it became obvious that the results needed a visual validation. Therefore, the script `STEP4_image_filtering.py` was created to coordinate this process. When this script is first run, a folder called "verif_pending" is created with first images of each specie. You then need to manually inspect the images and delete from this folder the files that do not meet requirements (based on your human eye). Once all the images have been reviewed, execute the script again an the images will be transfered to "verif_accepted" folder. Additionally the "Verif_pending" folder will be filled again with more images of the same species as the rejected images, if any available. Repeat this process of verificaton and execution untill no more new images appear in "verif_pending". A csv called "registro_eliminadas_manualmente.csv" is created to track the process. Additionally, a new column is created in "animal_features_wt_colors.csv" named "seleccionados" with a True if the image has been selected and a False otherwhise.

Here you can find some examples of images whose palette is not passing the visual inspections. The main causes are:

A) Wrong segmentation:
<img width="460" height="194" alt="image" src="https://github.com/user-attachments/assets/ebeb75df-8f97-4972-8c35-6b41ae7302ad" />

B) Animal framed too small in the image:
<img width="460" height="194" alt="image" src="https://github.com/user-attachments/assets/1c085f55-9f73-44dd-8de4-82eb0691e81b" />

C) Original image in greyscale:
<img width="460" height="194" alt="image" src="https://github.com/user-attachments/assets/63b101d5-5057-4605-8a5b-6004399397e7" />

D) White balance missadjustment:
<img width="460" height="194" alt="image" src="https://github.com/user-attachments/assets/47f2767e-8cb6-48f4-81af-21f9ab1ad0fb" />


