import sys
import datacube
dc = datacube.Datacube(app = 'my_app', config = '/home/localuser/.datacube.conf')

list_of_products = dc.list_products()
netCDF_products = list_of_products[list_of_products['format'] == 'NetCDF']
print(netCDF_products)


import utils.data_cube_utilities.data_access_api as dc_api  
api = dc_api.DataAccessApi(config = '/home/localuser/.datacube.conf')

platform = "LANDSAT_7"

# product = "ls7_ledaps_colombia"  
# product = "ls7_ledaps_vietnam"
product = "ls7_ledaps_general"  

# Get product extents
prod_extents = api.get_query_metadata(platform=platform, product=product, measurements=[])

latitude_extents = prod_extents['lat_extents']
print("Lat bounds:", latitude_extents)
longitude_extents = prod_extents['lon_extents']
print("Lon bounds:", longitude_extents)
time_extents = list(map(lambda time: time.strftime('%Y-%m-%d'), prod_extents['time_extents']))
print("Time bounds:", time_extents)

latitude_extents = (8, 9)
print(latitude_extents)

from utils.data_cube_utilities.dc_time import _n64_to_datetime
longitude_extents = (-3, -2)#list(map(lambda time: _n64_to_datetime(time), prod_extents['lon_extents']))
                             #.strftime('%Y-%m-%d'), prod_extents['lon_extents']))
print(longitude_extents)

from utils.data_cube_utilities.dc_time import _n64_to_datetime
longitude_extents = (-3, -2)#list(map(lambda time: _n64_to_datetime(time), prod_extents['lon_extents']))
                             #.strftime('%Y-%m-%d'), prod_extents['lon_extents']))
print(longitude_extents)

## The code below renders a map that can be used to orient yourself with the region.
from utils.data_cube_utilities.dc_display_map import display_map
display_map(latitude = latitude_extents, longitude = longitude_extents)

landsat_dataset = dc.load(latitude = (sys.argv[1], sys.argv[2]),
                          longitude = (sys.argv[3], sys.argv[4]),
                          platform = sys.argv[6],
                          time = (sys.argv[7], sys.argv[8]),
                          product = sys.argv[5],
                          measurements = ['red', 'green', 'blue', 'nir', 'swir1', 'swir2', 'pixel_qa']) 
print(landsat_dataset)

