##calculations comparing Selected Thermal CHaracteristics using remote sensing techniques. Bachelor Thesis##
 

import os
import earthpy as et
import earthpy.spatial as es
import geopandas as gpd
import numpy as np
import tifffile as tf
import rasterio
import json
import matplotlib.pyplot as plt
import sys
from osgeo import gdal, osr
from numpy import log
from rasterio.mask import mask
import fiona


print('Import done.')

def find_path(input_folder, file_name):
    path_list_folder = []
    for root, dics, files in os.walk(input_folder, topdown=False):
        for name in files:
            if name.endswith(file_name) :
                path_list_folder.append(os.path.join(root, name))
    return path_list_folder

#https://gist.github.com/mhweber/1af47ef361c3b20184455060945ac61b
def Raster_clip(inras, outras, SQUARE):
    src  = rasterio.open(inras)
    # Create a square GeoDataFrame from the square
    df = gpd.GeoDataFrame({'geometry': [SQUARE]}, crs="EPSG:4326")
    df = df.to_crs(src.crs)
    def getFeatures(gdf):
        """Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
        return [json.loads(gdf.to_json())['features'][0]['geometry']]
    coords = getFeatures(df)
    clipped_array, clipped_transform = mask(dataset=src, shapes=coords, crop=True)
    out_meta = src.meta.copy()
    out_meta.update({"driver": "GTiff",
                    "height": clipped_array.shape[1],
                    "width": clipped_array.shape[2],
                    "transform": clipped_transform,}
                    )
    
    with rasterio.open(outras, "w", **out_meta) as dest:
        dest.write(clipped_array)

    return clipped_array    


#https://gist.github.com/jkatagi/a1207eee32463efd06fb57676dcf86c8
def GeoRef(input_array, src_dataset_path, output_path):
        cols = input_array.shape[1]
        rows = input_array.shape[0]
        
        dataset = gdal.Open(src_dataset_path, gdal.GA_ReadOnly)
        originX, pixelWidth, b, originY, d, pixelHeight = dataset.GetGeoTransform() 
        driver = gdal.GetDriverByName('GTiff')
        band_num = 1
        GDT_dtype = gdal.GDT_Float32
        outRaster = driver.Create(output_path, cols, rows, band_num, GDT_dtype)
        outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
        outband = outRaster.GetRasterBand(band_num)
        outband.WriteArray(input_array)
        prj=dataset.GetProjection()
        outRasterSRS = osr.SpatialReference(wkt=prj)
        outRaster.SetProjection(outRasterSRS.ExportToWkt())
        
        return True

#Top of Atmosphere Reflectance
def TOA_Reflectance(band, ADD, MULT, out_folder, name = "_TOA_Ref"):   
    
    band_p= tf.imread(band)
    
    result_toa = MULT * band_p + ADD
    result_toa_path = os.path.join(out_folder, name + ".TIF")
    
    GeoRef(result_toa, band, result_toa_path)
    
    return result_toa_path


#Albedo Liang's method
def Albedo_liang(toa_band_2, toa_band_4, toa_band_5, toa_band_6, toa_band_7, out_folder, name = 'albedo'):
    B2_T = np.array(tf.imread(toa_band_2))
    B4_T = np.array(tf.imread(toa_band_4))
    B5_T = np.array(tf.imread(toa_band_5))
    B6_T = np.array(tf.imread(toa_band_6))
    B7_T = np.array(tf.imread(toa_band_7))
    
    result_albedo = ((0.356 * B2_T) + (0.130 * B4_T) + (0.373 * B5_T) + (0.085 * B6_T) + (0.072 * B7_T))-0.0018/1.016
    result_albedo_path = os.path.join(out_folder, name + ".TIF")
    
    GeoRef(result_albedo, toa_band_5, result_albedo_path)
    
    return result_albedo_path


#Albedo Tasumi's method
def Albedo_Tasumi(toa_band_2, toa_band_4, toa_band_5, toa_band_7, out_folder, name = 'albedo_tasumi'):
    B2_T = np.array(tf.imread(toa_band_2))
    B4_T = np.array(tf.imread(toa_band_4))
    B5_T = np.array(tf.imread(toa_band_5))
    B7_T = np.array(tf.imread(toa_band_7))

    albedo_tasumi = ((0.149 * B2_T) + (0.311 * B4_T) + (0.103 * B5_T)  + (0.036 * B7_T))-0.0018/0.599
    albedo_tasumi_path = os.path.join(out_folder, name + ".TIF")
    GeoRef(albedo_tasumi, toa_band_7, albedo_tasumi_path)

    return albedo_tasumi_path
 

#Top of Atmosphere Radiance
#TIRS = Thermal Infrared Sensor
#ADD = Additive rescaling factor
#MULT = Multiplicative rescaling factor
def TOA_Radiance(TIRS, ADD, MULT, out_folder, name = "TOA_Radiance"):   
        
    thermal= tf.imread(TIRS)
    
    cal_radiance = (MULT  * thermal) + ADD
    res_cal_radiance = os.path.join(out_folder, name + ".TIF")
    
    GeoRef(cal_radiance, TIRS, res_cal_radiance)
    
    return res_cal_radiance


#Normalized Difference Vegetation Index
#NIR = Near Infrared Band
#RED = Red Band
def NDVI(red, nir, out_folder, name = "_NDVI"):

    red_band = tf.imread(red)
    nir_band = tf.imread(nir)
    r = np.array(red_band).astype(rasterio.float32)#Convert to float32 to avoid overflows
    n = np.array(nir_band).astype(rasterio.float32)#Convert to float32 to avoid overflows
    
    overflows = np.seterr(divide='ignore', invalid='ignore') # Ignore the divided by zero or Nan appears

    ndvi = (n - r) / (n + r) # The NDVI formula
    ndvi_TIF = os.path.join(out_folder, name + ".TIF")

    GeoRef(ndvi, red, ndvi_TIF)

    return ndvi_TIF


#Vegetation Cover
#VC = 0.5 * NDVI + 0.5
#NDVI = Normalized Difference Vegetation Index		
def VC(ndvi, out_folder, name = "VC"):
    ndvi_arr = np.array(tf.imread(ndvi))
    calc_VC= 0.5 * ndvi_arr + 0.5
  
    result_VC = os.path.join(out_folder, name +".TIF")

    GeoRef(calc_VC, ndvi, result_VC)

    return result_VC


#Brightness Temperature
#Add = Radiance Add Band
#Mult = Radiance Multi Band
#b10_l1 = Band 10
def Brightness_Temperature(Add, Mult, b10_l1, out_folder, name = "BriTemp"):
    K1 = 774.8853
    K2 = 1321.0789
    Add = np.array(Add)
    Mult = np.array(Mult).astype(rasterio.float32)
    b10 = tf.imread(b10_l1)

    calc_BT = (K2 / np.log((K1 / (Mult * b10 + Add)) + 1)) - 273.15
    
    result_BT = os.path.join(out_folder, name + ".TIF")
    
    GeoRef(calc_BT, b10_l1, result_BT)
    
    return result_BT


#Land Surface Emissivity
#B10 = Brightness Temperature
#VC = Vegetation Cover
#NDVI = Normalized Difference Vegetation Index
#https://www.sciencedirect.com/science/article/pii/S0034425704000574
def LSE(b4, ndvi, VegC, out_folder, name = "LSE"):
    #b4_arr = np.array(tf.imread(b4))
    #ndvi_arr = np.array(tf.imread(ndvi))
    VegC_arr = np.array(tf.imread(VegC))
    
    calc_LSE = (0.004 * VegC_arr) + 0.986

    result_LSE = os.path.join(out_folder, name + ".TIF")
    
    GeoRef(calc_LSE, b4, result_LSE)
    
    return result_LSE


#Land Surface Temperature
#Emiss = Emissivity
#BrighT = Brightness Temperature
#B10 = Band 10
def LST(Emiss,BrighT,B10_l1, out_folder, name = "LST"):
    Emiss_arr = np.array(tf.imread(Emiss))
    BrighT_arr = np.array(tf.imread(BrighT))
    B10_arr = np.array(tf.imread(B10_l1))
    
    calc_LST = (BrighT_arr / (1 + ((0.00115 * B10_arr) / 1.4388) * log(Emiss_arr)))
    
    result_LST = os.path.join(out_folder, name + ".TIF")
    
    GeoRef(calc_LST, B10_l1, result_LST)
    
    return result_LST


#Net Radiation
#LSE = Land Surface Emissivity
#LST = Land Surface Temperature
#Albedo = Albedo
#Rsin = Solar Radiation
def Rn(LSE,LST,Albedo,Rsin, out_folder, name = "Rn"):
    LSE_arr = np.array(tf.imread(LSE))
    LST_arr = np.array(tf.imread(LST))
    Albedo_arr = np.array(tf.imread(Albedo))
    Rsin_arr = np.array(Rsin)

    #Constants
    stefan_boltzmann_constant = 5.67e-8 # W/m^2/K^4
    Emisivity_constant = 0.78

    Rlout = LSE_arr * 5.6703 * 10.0 ** (-8.0) * LST_arr ** 4
    Rlin = Emisivity_constant * 5.6703 * 10.0 ** (-8.0) * LST_arr ** 4
    Rsout =  Albedo_arr * Rsin

    calc_Rn = Rsin_arr - Rsout + Rlout - Rlin
    
    result_Rn = os.path.join(out_folder, name + ".TIF")
    
    GeoRef(calc_Rn, LSE, result_Rn)
    
    return result_Rn


#Ground Heat Flux
#Rn = Net Radiation
#VegC = Vegetation Cover
#https://www.mdpi.com/2072-4292/14/21/5629
#𝐺0=𝑅𝑛⋅[Γ𝑐+(1−𝑓𝑐)⋅(Γ𝑠−Γ𝑐)]
def GHFlux_1(Rn, VegC, out_folder, name = "GHE"):
    Rn_arr = np.array(tf.imread(Rn))
    VegC_arr = np.array(tf.imread(VegC))
    
    calc_GHE = Rn_arr * (0.05 + (1 - VegC_arr) * (0.315-0.05))
    
    result_GHE = os.path.join(out_folder, name + ".TIF")
    
    GeoRef(calc_GHE, Rn, result_GHE)
    
    return result_GHE


def GHFlux_2(albedo, lst,ndvi, totalRadiation, out_folder, name = "GHE"):
    albedo_arr = np.array(tf.imread(albedo))
    lst_arr = np.array(tf.imread(lst))
    totalRadiation_arr = np.array(tf.imread(totalRadiation))
    ndvi_arr = np.array(tf.imread(ndvi))

  # Calculate G
    calc_GHE = (lst_arr/albedo_arr) * ((0.0038*albedo_arr)+(0.0074*(albedo_arr**2))) * (1-(0.98*ndvi_arr**4))
    
    result_GHE = os.path.join(out_folder, name + ".TIF")
    
    GeoRef(calc_GHE, lst, result_GHE)
    
    return result_GHE



def Gr(RN,out_folder, name = "G"):
    RN_arr = np.array(tf.imread(RN))
    
    calc_G = 0.1 * RN_arr
    
    result_G = os.path.join(out_folder, name + ".TIF")
    
    GeoRef(calc_G, RN, result_G)
    
    return result_G