""" QGIS TESTING"""

import requests
import sys
from zipfile import ZipFile
import os
import glob
from qgis.core import *
from qgis import processing

# sys.path.append("C:/Program Files/QGIS 3.30.0/apps/qgis/python/plugins")
# from plugins import processing

def download():
    inputcountry = input("Country: ")
    if not os.path.isdir(f'{inputcountry}'):
        print("Folder does not exist: Downloading files")
        baseurl = 'https://biogeo.ucdavis.edu/data/diva/adm/'
        url = baseurl + inputcountry + "_adm.zip"
        r = requests.get(url, allow_redirects=True)
        open('{}.zip'.format(inputcountry), 'wb').write(r.content)
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
    layer = QgsVectorLayer("/{}".format(ctr), filtered_list[0], "ogr")
    processing.run("qgis:randompointsinsidepolygons",
                           {'INPUT': layer,
                    'STRATEGY': 0, 'VALUE': 100,
                    'MIN_DISTANCE': None, 'OUTPUT': '/{}/randompoints_temp.shp'.format(ctr)})
    processing.run("qgis:heatmapkerneldensityestimation",
                           {'INPUT': layer, 'RADIUS': 0.5, 'RADIUS_FIELD': '', 'PIXEL_SIZE': 0.005, 'WEIGHT_FIELD': '',
                    'KERNEL': 0, 'DECAY': 0, 'OUTPUT_VALUE': 0, 'OUTPUT': 'TEMPORARY_OUTPUT'})
    print("End of processing")


def cleanworkspace():
    pass


def main():
    admlist, ctr = download()
    process(admlist, ctr)
    # cleanworkspace()


if __name__ == "__main__":
    main()
