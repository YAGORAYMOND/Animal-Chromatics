# Animal-Chromatics
A data visualisation project exploring the colour palettes of animal species and their relationship with the characteristics documented in Animal Diversity Web (ADW)

## Dataset
The data was obtainde from Animal Diversity Web including the characteristics considered relevant for this study toguether with images of the animals for the extraction of its characteristic color palettes.

## Data processing:

### STEP1: Extraction of animal characteristics from ADW HTML files
The script `STEP1_database_creator_from_htmls.py` takes the html file of the result a query from Quaardavark query tool (https://animaldiversity.ummz.umich.edu/quaardvark/) and extracts the table information toguether with the images. The output is a CSV “animal_features.csv”  and a folder “animal_photos” containing the images of the species.

### STEP2: Cleaning and restructuring of the dataset
