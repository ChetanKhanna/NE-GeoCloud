#!/usr/bin/env python
# coding: utf-8

# In[1]:



# # NDVI  
# <br>  
#   
# > **NDVI(Normalized Difference Vegetation Index**  
# > A derived index that correlates well with the existance of vegetation.  
# 
# <br>
# 
# $$ NDVI =  \frac{(NIR - RED)}{(NIR + RED)}$$  
# 
# <br>

# In[2]:


def NDVI(dataset):
    return (dataset.nir - dataset.red)/(dataset.nir + dataset.red)


# <br>
# # NDWI  
#   
# <br>
# > ** NDWI Normalized Difference Water Index **  
# > A derived index that correlates well with the existance of water.  
# <br>
# 
# $$ NDWI =  \frac{GREEN - NIR}{GREEN + NIR}$$  
#   
# <br>

# In[3]:


def NDWI(dataset):
    return (dataset.green - dataset.nir)/(dataset.green + dataset.nir)


# <br>  
# 
# # NDBI  
# <br>  
# > ** NDWI Normalized Difference Build-Up Index **  
# > A derived index that correlates well with the existance of urbanization.  
# <br>
# 
# $$ NDBI =  \frac{(SWIR - NIR)}{(SWIR + NIR)}$$  
#  
# <br>  

# In[4]:


def NDBI(dataset):
        return (dataset.swir2 - dataset.nir)/(dataset.swir2 + dataset.nir)


# <br>
# # MOSAIC  
#   
# <br>  
# >** Recent-Pixel-First Mosaic **   
# >A cloud free representation of satellite imagery. Works by masking out clouds from imagery, and using the most recent cloud-free pixels in an image.  
# 
# ![](diagrams/urbanization/flat_mosaic.png)
#   
# <br>  

# In[5]:


from utils.data_cube_utilities.dc_mosaic import create_mosaic, ls7_unpack_qa, ls8_unpack_qa, ls5_unpack_qa
import numpy as np

def mosaic(dataset):
    # The mask here is based on pixel_qa. It comes bundled in with most Landsat Products.
    if sys.argv[6]=='LANDSAT_7':
    # The mask here is based on pixel_qa. It comes bundled in with most Landsat Products.
        clear_xarray  = ls7_unpack_qa(dataset.pixel_qa, "clear")  # Boolean Xarray indicating landcover
        water_xarray  = ls7_unpack_qa(dataset.pixel_qa, "water")  # Boolean Xarray indicating watercover
    elif sys.argv[6]=='LANDSAT_8':
        clear_xarray  = ls8_unpack_qa(dataset.pixel_qa, "clear")  # Boolean Xarray indicating landcover
        water_xarray  = ls8_unpack_qa(dataset.pixel_qa, "water")  # Boolean Xarray indicating watercover
    elif sys.argv[6]=='LANDSAT_5':
        clear_xarray  = ls5_unpack_qa(dataset.pixel_qa, "clear")  # Boolean Xarray indicating landcover
        water_xarray  = ls5_unpack_qa(dataset.pixel_qa, "water")  # Boolean Xarray indicating watercover

    
    cloud_free_boolean_mask = np.logical_or(clear_xarray, water_xarray)
    
    return create_mosaic(dataset, clean_mask = cloud_free_boolean_mask)


# <br>
#   
# > **Median Mosaic**  
# >  A cloud free representation fo satellite imagery. Works by masking out clouds from imagery, and using the median valued cloud-free pixels in the time series  
#   
# <br>
# 
# 
# ![](diagrams/urbanization/median_comp.png)  
#   
# <br>

# In[6]:


from utils.data_cube_utilities.dc_mosaic import create_median_mosaic, ls7_unpack_qa, ls8_unpack_qa, ls5_unpack_qa

def median_mosaic(dataset):
    if sys.argv[6]=='LANDSAT_7':
    # The mask here is based on pixel_qa. It comes bundled in with most Landsat Products.
        clear_xarray  = ls7_unpack_qa(dataset.pixel_qa, "clear")  # Boolean Xarray indicating landcover
        water_xarray  = ls7_unpack_qa(dataset.pixel_qa, "water")  # Boolean Xarray indicating watercover
    elif sys.argv[6]=='LANDSAT_8':    
        clear_xarray  = ls8_unpack_qa(dataset.pixel_qa, "clear")  # Boolean Xarray indicating landcover
        water_xarray  = ls8_unpack_qa(dataset.pixel_qa, "water")  # Boolean Xarray indicating watercover
    elif sys.argv[6]=='LANDSAT_5':
        clear_xarray  = ls5_unpack_qa(dataset.pixel_qa, "clear")  # Boolean Xarray indicating landcover
        water_xarray  = ls5_unpack_qa(dataset.pixel_qa, "water")  # Boolean Xarray indicating watercover

    cloud_free_boolean_mask = np.logical_or(clear_xarray, water_xarray)
    
    return create_median_mosaic(dataset, clean_mask = cloud_free_boolean_mask)


# <br>  
# 
# # Loading Data

# > **Data cube object**  
# > A datacube object is your interface with data stored on your data cube system.  
# <br>  

# In[7]:


import datacube  
dc = datacube.Datacube(app = '3B_urban', config = '/home/localuser/.datacube.conf')  


# <br>
# 
# > **Loading a Dataset**  
# > Requires latitude-longitude bounds of an area, a time-range, list of desired measurements, platform and product names.

# In[8]:


dc.list_products()


# In[9]:


import utils.data_cube_utilities.data_access_api as dc_api  
api = dc_api.DataAccessApi(config = '/home/localuser/.datacube.conf')

platform = 'LANDSAT_7'
product = 'ls7_ledaps_general'


desired_bands = ['red','green','nir','swir2', 'pixel_qa']  # needed by ndvi, ndwi, ndbi and cloud masking
desired_bands = desired_bands + ['blue'] # blue is needed for a true color visualization purposes

landsat_dataset = dc.load(product = sys.argv[5],	platform = sys.argv[6],	lat = (sys.argv[1], sys.argv[2]),	lon = (sys.argv[3], sys.argv[4]),	time = (sys.argv[7], sys.argv[8]),	measurements = desired_bands)
print(landsat_dataset)


# <br>  
# 
# # Displaying Data  
# <br>  
# 
# >**A cloud free composite**  
# Clouds get in the way of understanding the area. Cloud free composites draw from a history of acquisitions to generate a cloud free representation of your area  
# 
# <br>  

# In[11]:


landsat_mosaic = median_mosaic(landsat_dataset)
print(landsat_mosaic)


# <br>  
# > **Saving your data**  
# > A .tiff or png is a great way to represent true color mosaics. The image below is a saved .png representation of of a landsat mosaic.  

# In[12]:


from utils.data_cube_utilities.dc_utilities import write_png_from_xr
write_png_from_xr('diagrams/urbanization/cloud_free_mosaic.png', landsat_mosaic, ["red", "green", "blue"], scale = [(0,2000),(0,2000),(0,2000)])


# <br>  
# 
# ![](diagrams/urbanization/cloud_free_mosaic.png)  
#   
# <br>  

# <br>
# # Urbanization Analysis  
# <br>  
# 
# > **NDWI, NDVI, NDBI**  
# You will very rarely have urban classification and water classifications apply to the same pixel. For urban analysis, it may make sense to compute not just urban classes, but classes that are unlikely to co-occur with urbanization. 
#   
# <br>

# In[13]:


ndbi = NDBI(landsat_mosaic)  # Urbanization
ndvi = NDVI(landsat_mosaic)  # Dense Vegetation
ndwi = NDWI(landsat_mosaic)  # High Concentrations of Water


# <br>
# <br>
# >**Plot Values**  
# > xarray data-arrays have built in plotting functions you can use to validate trends or differences in your data.  
# <br>
#   

# In[14]:


(ndvi).plot(cmap = "Greens")


# In[15]:


(ndwi).plot(cmap = "Blues")


# In[16]:


(ndbi + 0.2).plot(cmap = "Reds")


# > **Convert To a Dataset**  
# It's good practice to accurately name your datasets and data-arrays. If you'd like to merge data-arrays into a larger datasets, you should convert data-arrays to datasets

# In[17]:


ds_ndvi = ndvi.to_dataset(name = "NDVI")
ds_ndwi = ndwi.to_dataset(name=  "NDWI")
ds_ndbi = ndbi.to_dataset(name = "NDBI")


# <br>
# > **Merge into one large Dataset **  
# > If your data-arrays share the same set of coordinates, or if you feel that you'll be using these values together in the future,  you should consider merging them into a dataset

# In[18]:


urbanization_dataset = ds_ndvi.merge(ds_ndwi).merge(ds_ndbi)


# <br>  
# >** Checking your Merge **  
# >The string readout of your new dataset should give you a good idea about how the `.merge` went.  
# <br>

# In[19]:


print(urbanization_dataset)


# <br>  
# <br>  
# 
# >**Building a False Color Composite**  
# > If you have three lowly correlated measurements, place each measurement on its own Red, Green, Blue channel and visualize it. 

# In[20]:


write_png_from_xr('diagrams/urbanization/false_color.png', urbanization_dataset, ["NDBI", "NDVI", "NDWI"], scale = [(-1,1),(0,1),(0,1)])


# ![](diagrams/urbanization/false_color.png)

# <br>
# >**Analyze The False Color Image**  
# 
# > Values that adhere strongly to individual classes adhere to their own color channel. In this example, NDVI adheres to green, NDWI adheres to blue, and NDBI seems to adhere to red  

# <br>  
# <br>  
# > **Validate urbanization using other imagery**  
# > Double check results using high-resolution imagery.  Compare to the false color mosaic
# <br>

# In[21]:


from utils.data_cube_utilities.dc_display_map import display_map
display_map(latitude = lat ,longitude = lon)  


# In[ ]:





# In[ ]:




