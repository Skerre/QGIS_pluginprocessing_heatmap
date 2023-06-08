""" QGIS TESTING"""

import requests
from zipfile import ZipFile
import glob
from qgis.core import *
import os
import sys
import json
import pandas as pd
import csv
# set up system paths
qspath = r'C:\Users\martin\PycharmProjects\HeatMapMaker\QGIS script/qgis_sys_paths.csv'
# provide the path where you saved this file.
paths = pd.read_csv(qspath).paths.tolist()
sys.path += paths
# set up environment variables
qepath = r'C:\Users\martin\PycharmProjects\HeatMapMaker\QGIS script/qgis_env.json'
js = json.loads(open(qepath, 'r').read())
for k, v in js.items():
    os.environ[k] = v
# In special cases, we might also need to map the PROJ_LIB to handle the projections
# for mac OS
# .environ['PROJ_LIB'] = '/Applications/Qgis.app/Contents/Resources/proj'

# qgis library imports
import PyQt5.QtCore
import qgis.PyQt.QtCore
from qgis.core import (QgsApplication,
                       QgsProcessingFeedback,
                       QgsProcessingRegistry)
from qgis.analysis import QgsNativeAlgorithms

feedback = QgsProcessingFeedback()
# initializing processing module
QgsApplication.setPrefixPath(js['HOME'], True)
qgs = QgsApplication([], False)
qgs.initQgis() # use qgs.exitQgis() to exit the processing module at the end of the script.
# initialize processing algorithms
# Pycharm gives an error but it works...
from processing.core.Processing import Processing
Processing.initialize()
import processing
QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())

def download():

    value_to_check = input("Enter a value to check: ")
    # Call the function to check if the value exists in the CSV file
    print(check_value_in_csv(value_to_check))


    inputcountry = input("Country: ")

    if not os.path.isdir(f'{inputcountry}'):
        print("Folder does not exist: Downloading files")
        baseurl = 'https://biogeo.ucdavis.edu/data/diva/adm/'
        url = baseurl + inputcountry + "_adm.zip"
        r = requests.get(url, allow_redirects=True)
        with open('{}.zip'.format(inputcountry), 'wb') as file:
            file.write(r.content)
        file.close()
        os.mkdir(inputcountry)
        with ZipFile('{}.zip'.format(inputcountry), 'r') as zObject:
            zObject.extractall('{}'.format(inputcountry))
            zObject.close()
        os.remove("{}.zip".format(inputcountry))
    admin_bounds = map(os.path.basename, glob.glob('{}/*[2|0].*'.format(inputcountry), recursive=True))
    admin_bounds = list(admin_bounds)
    return admin_bounds, inputcountry


def process(data, ctr):
    print("Entering Processing")
    filtered_list = [item for item in data if item.endswith('2.shp') or item.endswith('0.shp')]
    print(filtered_list)
    layer = QgsVectorLayer("{}".format(ctr), filtered_list[0], "ogr")
    print(layer.isValid())
    a = processing.run("qgis:randompointsinsidepolygons", {'INPUT': layer,
                    'STRATEGY': 0, 'VALUE': 100,
                    'MIN_DISTANCE': None, 'OUTPUT': 'TEMPORARY_OUTPUT'})
    processing.run("qgis:heatmapkerneldensityestimation", {'INPUT': a, 'RADIUS': 0.5, 'RADIUS_FIELD': '', 'PIXEL_SIZE': 0.005, 'WEIGHT_FIELD': '',
                    'KERNEL': 0, 'DECAY': 0, 'OUTPUT_VALUE': 0, 'OUTPUT': 'TEMPORARY_OUTPUT'})

    # processing.run("gdal:cliprasterbymasklayer", {
    #     'INPUT': 'C:/Users/martin/Documents/QGIS_temp/processing_yRndbJ/50c7494b1a7a456c8a388683633495bb/OUTPUT.tif',
    #     'MASK': 'C:/Users/martin/PycharmProjects/HeatMapMaker/ZMB/ZMB_adm0.shp', 'SOURCE_CRS': None, 'TARGET_CRS': None,
    #     'TARGET_EXTENT': None, 'NODATA': -1, 'ALPHA_BAND': False, 'CROP_TO_CUTLINE': True, 'KEEP_RESOLUTION': False,
    #     'SET_RESOLUTION': False, 'X_RESOLUTION': None, 'Y_RESOLUTION': None, 'MULTITHREADING': False, 'OPTIONS': '',
    #     'DATA_TYPE': 0, 'EXTRA': '', 'OUTPUT': 'TEMPORARY_OUTPUT'})

    print("End of processing")

def cleanworkspace():
    pass

def check_value_in_csv(value):
    with open('countries.csv', 'r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            # Check if the value exists in the first column
            if row[0] == value:
                return row[1]
            # Check if the value exists in the second column
            if row[1] == value:
                return row[0]
    return False

# Get user input

def main():
    admlist, ctr = download()
    process(admlist, ctr)
    # cleanworkspace()

if __name__ == "__main__":
    main()
