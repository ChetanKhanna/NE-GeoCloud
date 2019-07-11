import gdal
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt

img_ds = gdal.Open("/home/localuser/Downloads/S2B_MSIL1C_20190117T043119_N0207_R133_T46RCP_20190117T072349.SAFE/Geo/sentinel_stack_geo_subset.img")
band2= img_ds.GetRasterBand(1).ReadAsArray()
band3 = img_ds.GetRasterBand(2).ReadAsArray()
band4= img_ds.GetRasterBand(3).ReadAsArray()
band8 = img_ds.GetRasterBand(4).ReadAsArray()
x=img_ds.RasterXSize
y=img_ds.RasterYSize
gt=img_ds.GetGeoTransform()
minx=gt[0]
maxy=gt[3]
x_res=gt[1]
y_res=gt[5]
ans=np.stack((band2,band3,band4,band8),0)

latitude= float(input("Enter the Latitude: "))
longitude=float(input("Enter the Longitude: "))
horizontal=longitude-minx;
vertical=maxy-latitude;
horizontal/=x_res
vertical/=y_res
horizontal=int(horizontal)
vertical=int(vertical*-1)
roi = np.insert(ans[:, vertical, horizontal], 0, 1, axis=0)

latitude2= float(input("Enter the Latitude: "))
longitude2=float(input("Enter the Longitude: "))
horizontal2=longitude2-minx;
vertical2=maxy-latitude2;
horizontal2/=x_res
vertical2/=y_res
horizontal2=int(horizontal2)
vertical2=int(vertical2*-1)
roi2 = np.insert(ans[:, vertical2, horizontal2], 0, 2, axis=0)

latitude3= float(input("Enter the Latitude: "))
longitude3=float(input("Enter the Longitude: "))
horizontal3=longitude3-minx;
vertical3=maxy-latitude3;
horizontal3/=x_res
vertical3/=y_res
horizontal3=int(horizontal3)
vertical3=int(vertical3*-1)
roi3 = np.insert(ans[:, vertical3, horizontal3], 0, 3, axis=0)

latitude4= float(input("Enter the Latitude: "))
longitude4=float(input("Enter the Longitude: "))
horizontal4=longitude4-minx;
vertical4=maxy-latitude4;
horizontal4/=x_res
vertical4/=y_res
horizontal4=int(horizontal4)
vertical4=int(vertical4*-1)
roi4 = np.insert(ans[:, vertical4, horizontal4], 0, 4, axis=0)

new=np.stack((roi,roi2,roi3,roi4),0)
X=new[0:4,1:5]
y=[1,2,3,4]

rf = RandomForestClassifier(n_estimators=500, oob_score=True)
rf = rf.fit(X, y)

new_shape = (ans.shape[1] * ans.shape[2], ans.shape[0])
img_as_array = ans[:4, :,].reshape(new_shape)
class_prediction = rf.predict(img_as_array)
class_prediction = class_prediction.reshape(ans[0, :, :].shape)

def color_stretch(image, index, minmax=(0, 10000)):
    colors = image[:, :, index].astype(np.float64)
    max_val = minmax[1]
    min_val = minmax[0]
    colors[colors[:, :, :] > max_val] = max_val
    colors[colors[:, :, :] < min_val] = min_val
    for b in range(colors.shape[2]):
    	colors[:, :, b] = colors[:, :, b] * 1 / (max_val - min_val)
	return colors
    
img543 = color_stretch(ans, [4, 3, 2], (0, 8000))
n = class_prediction.max()

# Next setup a colormap for our map
colors = dict((
    (2, (0, 150, 0, 255)),  # Forest
    (1, (0, 0, 255, 255)),  # Water
    (3, (0, 255, 0, 255)),  # Herbaceous
    (4, (160, 82, 45, 255))  # Barren
))

for k in colors:
    v = colors[k]
    _v = [_v / 255.0 for _v in v]
    colors[k] = _v
    
index_colors = [colors[key] if key in colors else 
                (255, 255, 255, 0) for key in range(1, n + 1)]
cmap = plt.matplotlib.colors.ListedColormap(index_colors, 'Classification', n)

plt.subplot(121)
plt.imshow(img543)
plt.title('Landsat Image')
print(class_prediction.shape)
plt.subplot(122)
plt.imshow(class_prediction, cmap=cmap, interpolation='none')
plt.title('Classified Image')
plt.show()

finalcoordinates=[minx, maxy, minx+(gt[1]*x_res), maxy+(gt[5]*y_res)]