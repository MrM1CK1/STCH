##comparison of Selected Thermal CHaracteristics using remote sensing techniques. Bachelor Thesis##


import os
from pprint import pprint
import earthpy.spatial as es
import geopandas as gpd
import numpy as np
import pandas as pa
import tifffile as tf
from fiona.crs import from_epsg
from rasterio.mask import mask
from scipy import ndimage
from shapely.geometry import box

import calc_STCH


SCRIPT_DIR = os.path.dirname((os.path.abspath(__file__)))   #Directory of the script
IN_FOLDER = (os.path.join(SCRIPT_DIR, r'input'))            #Input folder in the same directory
OUT_FOLDER = (os.path.join(SCRIPT_DIR, r'output'))          #Output folder in the same directory
CLIPPED = (os.path.join(SCRIPT_DIR, r'output'))             #Clipped folder in the output folder

SQUARE = box(17.0846,49.5122,18.5743,49.9015) #Coordinates of the area of interest
EPSG_CODE = 32633       #EPSG code of the area of interest
L8_dict = {}
L9_dict = {}
L8_metadata = {}
landsate_date = []


landsat_tif = calc_STCH.find_path(IN_FOLDER, ".TIF")   ###L1 i L2

RadiShortIn = pa.read_csv((os.path.join(SCRIPT_DIR, 'Rsin.csv')), delimiter =';') #RadiationShort.csv

#Finding the Landsat images (Landsat Level 1)
for landsat_path in landsat_tif:
    
    landsat_name = os.path.basename(landsat_path) 
    if 'L1' in landsat_name:
        date = landsat_name.split('_')[3] #20220627
        if date not in landsate_date:
            landsate_date.append(date)

        if date in L8_dict:
            L8_dict[date].append(landsat_path)
        else:
            L8_dict[date] = [landsat_path]      

#Joining the Rsin values with the Landsat images
for date in landsate_date:

    Rsin_value = RadiShortIn.loc[RadiShortIn['date'] == int(date), 'value']

    if Rsin_value.empty:
        Rsin_value = RadiShortIn["value"].mean()
    else:
        Rsin_value = Rsin_value.to_numpy()[0]

        
for landsat_path in landsat_tif:
    if 'B1.TIF' in landsat_path:
        txt_path = landsat_path.replace('B1.TIF', 'MTL.txt')
        
        metadata_file = open(txt_path, 'r')
        for line in metadata_file:
            if '=' in line:
                key, value = line.strip().split(' = ')
                L8_metadata[key] = value                                 
        metadata_file.close()
        break
    
# Clipping the images
list_of_paths_clipped = []
for landsat_path in landsat_tif:
    image_name = os.path.basename(landsat_path).replace('.TIF', '')   
    if 'B' in image_name.split('_')[-1]: ## vyfiltruje pouze pásma s DATY (Bx)
        out_path = os.path.join(CLIPPED, image_name + '_Clipped.TIF') 
        calc_STCH.Raster_clip(landsat_path, out_path, SQUARE)
        list_of_paths_clipped.append(out_path) 


for date in landsate_date:
    for path in list_of_paths_clipped:
        if date in path:
            if 'SR_B1' in path:
                b1_l2 = path
                
            elif 'SR_B2' in path:
                b2_l2 = path
                reflectance_MULT_B2 = float((L8_metadata['REFLECTANCE_MULT_BAND_2']))
                reflectance_ADD_B2 = float((L8_metadata['REFLECTANCE_ADD_BAND_2']))
                
            elif 'SR_B3' in path:
                b3_l2 = path
                
            elif 'SR_B4' in path:
                b4_l2 = path
                reflectance_MULT_B4 = float((L8_metadata['REFLECTANCE_MULT_BAND_4']))
                reflectance_ADD_B4 = float((L8_metadata['REFLECTANCE_ADD_BAND_4']))
                
            elif 'SR_B5' in path:
                b5_l2 = path
                reflectance_MULT_B5 = float((L8_metadata['REFLECTANCE_MULT_BAND_5']))
                reflectance_ADD_B5 = float((L8_metadata['REFLECTANCE_ADD_BAND_5']))
                
            elif 'SR_B6' in path:
                b6_l2  = path
                reflectance_MULT_B6 = float((L8_metadata['REFLECTANCE_MULT_BAND_6']))
                reflectance_ADD_B6 = float((L8_metadata['REFLECTANCE_ADD_BAND_6']))
                
            elif 'SR_B7' in path:
                b7_l2  = path
                reflectance_MULT_B7 = float((L8_metadata['REFLECTANCE_MULT_BAND_7']))
                reflectance_ADD_B7 = float((L8_metadata['REFLECTANCE_ADD_BAND_7']))
                
            elif 'ST_B10' in path:
                b10_l2  = path
                radiance_MULT_B10 = float((L8_metadata['RADIANCE_MULT_BAND_10']))
                radiance_ADD_B10 = float((L8_metadata['RADIANCE_ADD_BAND_10']))

                K1_CONSTANT_BAND_10 = float((L8_metadata['K1_CONSTANT_BAND_10']))
                K2_CONSTANT_BAND_10 = float((L8_metadata['K2_CONSTANT_BAND_10']))
                
            elif 'L1TP' and 'B10' in path:
                b10_l1  = path
                radiance_MULT_B10_l1 = float((L8_metadata['RADIANCE_MULT_BAND_10']))
                radiance_ADD_B10_l1 = float((L8_metadata['RADIANCE_ADD_BAND_10']))
                K1_CONSTANT_BAND_10_L1 = float((L8_metadata['K1_CONSTANT_BAND_10']))
                K2_CONSTANT_BAND_10_L1 = float((L8_metadata['K2_CONSTANT_BAND_10']))
    
    ndvi_TIF = calc_STCH.NDVI(b4_l2, b5_l2, OUT_FOLDER, 'NDVI_' + date)   
    VegC = calc_STCH.VC(ndvi_TIF, OUT_FOLDER, 'VC_' + date)

    TOA_radiance_B10_L1 = calc_STCH.TOA_Radiance(b10_l1, radiance_ADD_B10_l1, radiance_MULT_B10_l1, OUT_FOLDER, 'TOA_Radiance_B10_' + date)
    BrighTemp = calc_STCH.Brightness_Temperature(radiance_ADD_B10_l1,radiance_MULT_B10_l1, b10_l1, OUT_FOLDER, 'BrightTemp_' + date)

    Emmisivity = calc_STCH.LSE(b4_l2, ndvi_TIF, VegC, OUT_FOLDER, 'Emiss_' + date)
    LSTemperature = calc_STCH.LST(Emmisivity, BrighTemp, b10_l1, OUT_FOLDER, 'LST_' + date)

    TOA_refle_b2 = calc_STCH.TOA_Reflectance(b2_l2, reflectance_ADD_B2, reflectance_MULT_B2, OUT_FOLDER, 'TOARef_b2_' + date)
    TOA_refle_b4 = calc_STCH.TOA_Reflectance(b4_l2, reflectance_ADD_B4, reflectance_MULT_B4, OUT_FOLDER, 'TOARef_b4_' + date)
    TOA_refle_b5 = calc_STCH.TOA_Reflectance(b5_l2, reflectance_ADD_B5, reflectance_MULT_B5, OUT_FOLDER, 'TOARef_b5_' + date)
    TOA_refle_b6 = calc_STCH.TOA_Reflectance(b6_l2, reflectance_ADD_B6, reflectance_MULT_B6, OUT_FOLDER, 'TOARef_b6_' + date)
    TOA_refle_b7 = calc_STCH.TOA_Reflectance(b7_l2, reflectance_ADD_B7, reflectance_MULT_B7, OUT_FOLDER, 'TOARef_b7_' + date)
    Albedo_liang = calc_STCH.Albedo_liang(TOA_refle_b2, TOA_refle_b4, TOA_refle_b5, TOA_refle_b6, TOA_refle_b7, OUT_FOLDER, 'Albedo_Liang_' + date)
    Albedo_Tasumi = calc_STCH.Albedo_Tasumi(TOA_refle_b2, TOA_refle_b4, TOA_refle_b5, TOA_refle_b7, OUT_FOLDER, 'Albedo_Tasumi_' + date)


    Rn = calc_STCH.Rn(Emmisivity, LSTemperature, Albedo_liang, Rsin_value, OUT_FOLDER, 'Rn_' + date)
    GroundHeatFlux = calc_STCH.GHFlux_1(Rn, VegC, OUT_FOLDER, 'GHF_SEBS_' + date)
    GroundHeatFlux_2 = calc_STCH.GHFlux_2(Albedo_liang,b10_l1,LSTemperature, ndvi_TIF,TOA_radiance_B10_L1, OUT_FOLDER, 'GHF_SEBAL_' + date)
    Gr = calc_STCH.Gr(Rn, OUT_FOLDER, 'GHF_Rn_' + date)

pprint('All done and in order')
