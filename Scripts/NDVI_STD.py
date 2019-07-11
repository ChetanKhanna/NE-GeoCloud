
# coding: utf-8

# # NDVI STD <a id="top"></a>
# 
# Deviations from an established average z-score   
# 
# <hr>  
#   
# # Notebook Summary
# 
# * A baseline for each month is determined by measuring NDVI over a set time
# * The data cube is used to visualize at NDVI anomalies over time.
# * Anomalous times are further explored and visualization solutions are proposed.
# 
# <hr>  
# 
# # Algorithmic process  
# 
# * [Import dependencies and connect to the data cube](#import)
# * [Choose platform and product](#plat_prod)
# * [Get the maximum extents of the data cube](#extents)
# * [Define extents you require that fall within the maximum extents](#define_extents) (selecting too much can make the acquisition process slow)
# * [Retrieve the data from the data cube](#retrieve_data)
# * [Obtain the clean mask and use it to filter out clouds and scan lines](#clean_mask)
# * [Calculate NDVI and make a dataframe](#calculate)
# * [Make a dataframe from the xarray](#pandas)
# * [Make a visualization function to view ndvi and z-scores over the region](#visualization_function)
# * [Calculate the baseline average NDVI for each month](#calculate_baseline)
# * [Use a boxplot to view the baseline distributions quickly](#boxplot_analysis)
# * [Use a violin plot to examine kernel densities in more detail](#violinplot_analysis)
# * [Create a pixel plot of the months by time to view z-scores](#pixelplot_analysis)
# * [Further examine the region of a time identified in the pixel plot](#heatmap_analysis)
# 
# <hr>  
# 
# # How It Works
# 
# To detect changes in plant life, we use a measure called NDVI. 
# * <font color=green>NDVI</font> is the ratio of the difference between amount of near infrared light <font color=red>(NIR)</font> and red light <font color=red>(RED)</font> divided by their sum.
# <br>
# 
# $$ NDVI =  \frac{(NIR - RED)}{(NIR + RED)}$$  
# 
# <br>
# <div class="alert-info">
# The idea is to observe how much red light is being absorbed versus reflected. Photosynthetic plants absorb most of the visible spectrum's wavelengths when they are healthy.  When they aren't healthy, more of that light will get reflected.  This makes the difference between <font color=red>NIR</font> and <font color=red>RED</font> much smaller which will lower the <font color=green>NDVI</font>.  The resulting values from doing this over several pixels can be used to create visualizations for the changes in the amount of photosynthetic vegetation in large areas.
# </div>

# <hr>  
# 
# ## <a id="import">Import Dependencies and Connect to the Data Cube</a>  [&#9652;](#top)

# In[1]:

from IPython import get_ipython
import numpy
import datacube
dc = datacube.Datacube(app = 'my_app', config = '/home/localuser/.datacube.conf')

import utils.data_cube_utilities.data_access_api as dc_api  
api = dc_api.DataAccessApi(config = '/home/localuser/.datacube.conf')


# <hr>  
# 
# ## <a id="plat_prod">Select the Product and Platform</a>  [&#9652;](#top)

# In[2]:


# Change the data platform and data cube here

platform = "LANDSAT_7"
# platform = "LANDSAT_8"

# product = "ls7_ledaps_ghana"
product = "ls7_ledaps_general"
# product = "ls7_ledaps_senegal"
# product = "ls7_ledaps_sierra_leone"
# product = "ls7_ledaps_tanzania"
# product = "ls7_ledaps_vietnam"

# Get Extents
extents = api.get_full_dataset_extent(platform = platform, product = product)
print("extents")
print(extents)

# <hr>  
# 
# ## <a id="extents">Determine the Extents of the Data</a>  [&#9652;](#top)

# In[3]:


latitude_extents = (min(extents['latitude'].values),max(extents['latitude'].values))
longitude_extents = (min(extents['longitude'].values),max(extents['longitude'].values))
time_extents = (min(extents['time'].values),max(extents['time'].values))
print(time_extents)


# <hr>  
# 
# ## <a id="define_extents">Define the Region to Be Examined</a>  [&#9652;](#top)

# In[4]:


from utils.data_cube_utilities.dc_display_map import display_map

display_map(latitude_extents, longitude_extents)


# In[5]:


params = {'latitude': (0.55, 0.7),
 'longitude': (35.55, 35.7),
 'time': (numpy.datetime64('2005-01-01T00:00:00.000000'), numpy.datetime64('2010-12-01T00:00:00.000000'))}


# In[6]:


params = {'latitude': (0.55, 0.7),
 'longitude': (35.55, 35.7),
 'time': ( '2005-01-01', '2010-12-01')}


# In[7]:


params = {'latitude': (0.55, 0.6),
 'longitude': (35.55, 35.5),
 'time': ( '2005-01-01', '2010-12-01')}


# In[8]:


display_map(params["latitude"], params["longitude"])


# <hr>  
# 
# ## <a id="retrieve_data">Retrieve the Data From the Data Cube</a>  [&#9652;](#top)

# In[ ]:


dataset = dc.load(**params,
                  platform = platform,
                  product = product,
                  measurements = ['red', 'green', 'blue', 'swir1', 'swir2', 'nir', 'pixel_qa']) 
dataset


# <hr>  
# 
# ## <a id="clean_mask">Create and Use Clean Mask</a>  [&#9652;](#top)

# In[ ]:


exec(%matplotlib inline)
import matplotlib.pyplot as plt
import seaborn as sns
from utils.data_cube_utilities.dc_mosaic import ls7_unpack_qa

#Make a Clean Mask to remove clouds and scanlines
mask = ls7_unpack_qa(dataset.pixel_qa, "clear")

#Filter the scenes with that clean mask
dataset = dataset.where(mask)


# <hr>  
# 
# ## <a id="calculate">Calculate the NDVI</a>  [&#9652;](#top)

# In[ ]:


#Calculate NDVI
ndvi = (dataset.nir - dataset.red)/(dataset.nir + dataset.red)


# <hr>  
# 
# ## <a id="pandas">Convert the Xarray to a Dataframe</a>  [&#9652;](#top)

# In[ ]:


import pandas as pd

#Cast to pandas dataframe
df = ndvi.to_dataframe("NDVI")

#flatten the dimensions since it is a compound hierarchical dataframe
df = df.stack().reset_index()

#Drop the junk column that was generated for NDVI
df = df.drop(["level_3"], axis=1)

#Preview first 5 rows to make sure everything looks as it should
df.head()


# In[ ]:


#Rename the NDVI column to the appropriate name
df = df.rename(index=str, columns={0: "ndvi"})

#clamp NDVI between 0 and 1
df.ndvi = df.ndvi.clip_lower(0)

#Add columns for Month and Year for convenience
df["Month"] = df.time.dt.month
df["Year"] = df.time.dt.year

#Preview changes
df.head()


# <hr>  
# 
# ## <a id="visualization_function">Define a Function to Visualize Values Over the Region</a>  [&#9652;](#top)

# In[ ]:


from matplotlib.ticker import FuncFormatter


#Create a function for formatting our axes
def format_axis(axis, digits = None, suffix = ""):
    
    #Get Labels
    labels = axis.get_majorticklabels()
    
    #Exit if empty
    if len(labels) == 0: return
    
    #Create formatting function
    format_func = lambda x, pos: "{0}{1}".format(labels[pos]._text[:digits],suffix)
    
    #Use formatting function
    axis.set_major_formatter(FuncFormatter(format_func))
    

#Create a function for examining the z-score and NDVI of the region graphically
def examine(month = list(df["time"].dt.month.unique()), year = list(df["time"].dt.year.unique()), value_name = "z_score"):
    
    #This allows the user to pass single floats as values as well
    if type(month) is not list: month = [month]
    if type(year) is not list: year = [year]
          
    #pivoting the table to the appropriate layout
    piv = pd.pivot_table(df[df["time"].dt.year.isin(year) & df["time"].dt.month.isin(month)],
                         values=value_name,index=["latitude"], columns=["longitude"])
   
    #Sizing
    plt.rcParams["figure.figsize"] = [11,11]
    
    #Plot pivot table as heatmap using seaborn
    val_range = (-1.96,1.96) if value_name is "z_score" else (df[value_name].unique().min(),df[value_name].unique().max())
    ax = sns.heatmap(piv, square=False, cmap="RdYlGn",vmin=val_range[0],vmax=val_range[1], center=0)

    #Formatting        
    format_axis(ax.yaxis, 6)
    format_axis(ax.xaxis, 7) 
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=90 )
    plt.gca().invert_yaxis()


# Lets examine the average <font color=green>NDVI</font> across all months and years to get a look at the region

# In[ ]:


#It defaults to binning the entire range of months and years so we can just leave those parameters out
examine(value_name="ndvi")


# This gives us an idea of the healthier areas of the region before we start looking at specific months and years.
# <hr>

# ## <a id="calculate_baseline">View the Baseline Averages Binned by Month</a>   [&#9652;](#top)

# In[ ]:


#Make labels for convenience
labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

#Initialize an empty pandas Series
df["z_score"] = pd.Series()

#declare list for population
binned_data = list()

#Calculate monthly binned z-scores from the composited monthly NDVI mean and store them
for i in range(12):
    
    #grab z_score and NDVI for the appropriate month
    temp  = df[["z_score", "ndvi"]][df["Month"] == i+1]
    
    #populate z_score
    df.loc[df["Month"] == i+1,"z_score"] = (temp["ndvi"] - temp["ndvi"].mean())/temp["ndvi"].std(ddof=0)
    
    #print the month next to its mean NDVI and standard deviation
    binned_data.append((labels[i], temp["ndvi"].mean(), temp["ndvi"].std()))

#Create dataframe for binned values
binned_data = pd.DataFrame.from_records(binned_data, columns=["Month","Mean", "Std_Dev"])
    
#print description for clarification
print("Monthly Average NDVI over Baseline Period")

#display binned data
binned_data


# ## <a id="boxplot_analysis">Visualize the Baseline Distributions Binned by Month</a>  [&#9652;](#top)

# In[ ]:


#Set figure size to a larger size
plt.rcParams["figure.figsize"] = [16,9]

#Create the boxplot
df.boxplot(by="Month",column="ndvi")

#Create the mean line
plt.plot(binned_data.index+1, binned_data.Mean, 'r-')

#Create the one standard deviation away lines
plt.plot(binned_data.index+1, binned_data.Mean-binned_data.Std_Dev, 'b--')
plt.plot(binned_data.index+1, binned_data.Mean+binned_data.Std_Dev, 'b--')

#Create the two standard deviations away lines
plt.plot(binned_data.index+1, binned_data.Mean-(2*binned_data.Std_Dev), 'g-.', alpha=.3)
plt.plot(binned_data.index+1, binned_data.Mean+(2*binned_data.Std_Dev), 'g-.', alpha=.3)


# The plot above shows the distributions for each individual month over the baseline period.
# <br>
# - The <b><font color=red>red</font></b> line is the mean line which connects the <b><em>mean values</em></b> for each month.  
#     <br>
# - The dotted <b><font color=blue>blue</font></b> lines are exactly <b><em>one standard deviation away</em></b> from the mean and show where the NDVI values fall within 68% of the time, according to the Empirical Rule.  
#     <br>
# - The <b><font color=green>green</font></b> dotted lines are <b><em>two standard deviations away</em></b> from the mean and show where an estimated 95% of the NDVI values are contained for that month.
# <br>
# 
# <div class="alert-info"><font color=black> <em><b>NOTE: </b>You will notice a seasonal trend in the plot above.  If we had averaged the NDVI without binning, this trend data would be lost and we would end up comparing specific months to the average derived from all the months combined, instead of individually.</em></font>
# </div>
# <hr>

# ## <a id="violinplot_analysis">Visualize the Baseline Kernel Distributions Binned by Month</a>   [&#9652;](#top)
# This style of plot has the advantage of allowing us to visualize kernel distributions but comes at a higher computational cost

# In[ ]:


sns.violinplot(x=df.Month, y="ndvi", data=df)


# <hr>  
# 
# ## <a id="pixelplot_analysis">Plot Z-Scores by Month and Year</a>  [&#9652;](#top)
# ### Pixel Plot Visualization

# In[ ]:


#Create heatmap layout from dataframe
img = pd.pivot_table(df, values="z_score",index=["Month"], columns=["Year"], fill_value=None)

#pass the layout to seaborn heatmap
ax = sns.heatmap(img, cmap="RdYlGn", annot=True, fmt="f", center = 0)

#set the title for Aesthetics
ax.set_title('Z-Score\n Regional Selection Averages by Month and Year')
ax.fill= None


# Each block in the visualization above is representative of the deviation from the average for the region selected in a specific month and year.  The omitted blocks are times when there was no satellite imagery available.  Their values must either be inferred, ignored, or interpolated.
# 
# You may notice long vertical strips of red.  These are strong indications of drought since they deviate from the baseline consistently over a long period of time. 

# <hr>  
# 
# ## <a id="heatmap_analysis">Further Examine Times Of Interest</a>  [&#9652;](#top)
# ### Use the function we created to examine times of interest

# In[ ]:


#Lets look at that drought in 2009 during the months of Aug-Oct

#This will generate a composite of the z-scores for the months and years selected
examine(month = [8], year = 2009, value_name="z_score")


# Note:
# This graphical representation of the region shows the amount of deviation from the mean for each pixel that was binned by month

# ### Grid Layout of Selected Times

# In[ ]:


import numpy as np
import matplotlib as mpl
import time

#Restrict input to a maximum of about 12 grids (months*year) for memory
def grid_examine(month = None, year = None, value_name = "z_score"):
    
    #default to all months then cast to list, if not already
    if month is None: month = list(df["Month"].unique())
    elif type(month) is int: month = [month]

    #default to all years then cast to list, if not already
    if year is None: year = list(df["Year"].unique())
    elif type(year) is int: year = [year]

    #get data within the bounds specified
    data = df[np.logical_and(df["Month"].isin(month) , df["Year"].isin(year))]
    
    #Set the val_range to be used as the vertical limit (vmin and vmax)
    val_range = (-1.96,1.96) if value_name is "z_score" else (df[value_name].unique().min(),df[value_name].unique().max())
    
    #create colorbar to export and use on grid
    Z = [[val_range[0],0],[0,val_range[1]]]
    CS3 = plt.contourf(Z, 200, cmap="RdYlGn")
    plt.clf()    
    
    
    #Define facet function to use for each tile in grid
    def heatmap_facet(*args, **kwargs):
        data = kwargs.pop('data')
        img = pd.pivot_table(data, values=value_name,index=["latitude"], columns=["longitude"], fill_value=None)
                
        ax = sns.heatmap(img, cmap="RdYlGn",vmin=val_range[0],vmax=val_range[1],
                         center = 0, square=True, cbar=False, mask = img.isnull())

        plt.setp(ax.xaxis.get_majorticklabels(), rotation=90 )
        plt.gca().invert_yaxis()
    
    
    #Create grid using the face function above
    with sns.plotting_context(font_scale=5.5):
        g = sns.FacetGrid(data, col="Year", row="Month", size=5,sharey=True, sharex=True) 
        mega_g = g.map_dataframe(heatmap_facet, "longitude", "latitude")      
        g.set_titles(col_template="Yr= {col_name}", fontweight='bold', fontsize=18)                         
       
        #Truncate axis tick labels using the format_axis function defined in block 13
        for ax in g.axes:
            format_axis(ax[0]._axes.yaxis, 6)
            format_axis(ax[0]._axes.xaxis, 7)
                
        #create a colorbox and apply the exported colorbar
        cbar_ax = g.fig.add_axes([1.015,0.09, 0.015, 0.90])
        cbar = plt.colorbar(cax=cbar_ax, mappable=CS3)


# In[ ]:


grid_examine(month=[8,9,10], year=[2008,2009,2010])

