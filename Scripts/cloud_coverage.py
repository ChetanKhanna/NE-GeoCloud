import sys
from utils.data_cube_utilities.dc_mosaic import create_mosaic, ls7_unpack_qa, ls8_unpack_qa, ls5_unpack_qa
import numpy as np
from utils.data_cube_utilities.dc_mosaic import create_median_mosaic, ls7_unpack_qa, ls8_unpack_qa, ls5_unpack_qa
import utils.data_cube_utilities.data_access_api as dc_api  
import datacube  
from utils.data_cube_utilities.dc_utilities import write_png_from_xr
from utils.data_cube_utilities.dc_display_map import display_map
import datetime


start_time = datetime.datetime.now()

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

dc = datacube.Datacube(app = '3B_urban', config = '/home/localuser/.datacube.conf')  


# <br>
# 
# > **Loading a Dataset**  
# > Requires latitude-longitude bounds of an area, a time-range, list of desired measurements, platform and product names.

# In[8]:


dc.list_products()


# In[9]:


api = dc_api.DataAccessApi(config = '/home/localuser/.datacube.conf')

platform = sys.argv[6]
product = sys.argv[5]

if product == 'ls8_ingested':
    desired_bands = ['red','green','nir','swir2', 'quality']
else:
    desired_bands = ['red','green','nir','swir2', 'pixel_qa']  # needed by ndvi, ndwi, ndbi and cloud masking

desired_bands = desired_bands + ['blue'] # blue is needed for a true color visualization purposes

landsat_dataset = dc.load(product = sys.argv[5], platform = sys.argv[6],	lat = (sys.argv[1], sys.argv[2]),	lon = (sys.argv[3], sys.argv[4]),	time = (sys.argv[7], sys.argv[8]),	measurements = desired_bands)

if product == 'ls8_ingested':
    landsat_mosaic =landsat_dataset
else:
    landsat_mosaic = median_mosaic(landsat_dataset)
# print(landsat_mosaic)

# <br>  
# > **Saving your data**  
# > A .tiff or png is a great way to represent true color mosaics. The image below is a saved .png representation of of a landsat mosaic.  

# In[12]:


write_png_from_xr('static/assets/results/cloud_free/cloud_free.png', landsat_mosaic, ["red", "green", "blue"], scale = [(0,2000),(0,2000),(0,2000)])
