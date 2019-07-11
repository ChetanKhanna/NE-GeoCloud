# Copyright 2016 United States Government as represented by the Administrator
# of the National Aeronautics and Space Administration. All Rights Reserved.
#
# Portion of this code is Copyright Geoscience Australia, Licensed under the
# Apache License, Version 2.0 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of the License
# at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# The CEOS 2 platform is licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from apps.dc_algorithm.views import DataCubeVisualization, GetIngestedAreas
from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
import json
import os
import subprocess
import multiprocessing
import gdal
import numpy as np
from PIL import Image
import base64
import gdal
import math
import time


class DataCubeVisualization(DataCubeVisualization):

    """
    Create a Visualizer which shows all ingested data
    """
    tool_name = 'Land Cover Classification'
    tool_id = 'fractional_cover'
    tool_inputs = 1
    tool_satellites = {'Sentinel', 'LANDSAT_8'}


class GetIngestedData(GetIngestedAreas):

    pass

def tiling(request, z, x, y):
    #data = np.zeros((h, w, 3), dtype=np.uint8)
    
  #   y=(2**int(z))-int(y)-1
  #   print(y)
  #   ullat,ullon= num2deg(int(x),y,int(z))
  #   brlat,brlon= num2deg(int(x)+1,(y+1),int(z))
  #   bbox = [ullat,ullon,brlat,brlon]
  #   print("bbox 1: {}".format(bbox))
    
  #   bbox = [int((gt[3]-ullat)/-gt[5]),-1*int((gt[0]-ullon)/gt[1]),int((gt[3]-brlat)/-gt[5]),-1*int((gt[0]-brlon)/gt[1])]
  # #  bbox = bbox.astype(int)
  #   print("bbox2: {}".format(bbox))
  #   #print("shape")
  #   print(new_arr.shape)
  #   if(bbox[0]>0 and bbox[1]>0 and bbox[2]>0 and bbox[3]>0):  
  #     img = Image.fromarray(new_arr[bbox[0]:bbox[2],bbox[1]:bbox[3]])
  #   # serialize to HTTP response
  #     response = HttpResponse(content_type="image/png")
  #     img.save(response, "PNG")

      response = HttpResponse(content_type="image/png")
      img = Image.open("/home/localuser/Datacube/NE-GeoCloud/static/assets/results/urbanization/false_color/" + z + "/" + x + "/" + y + ".png")
      img.save(response, "PNG")
      return response
        # return ("ok")

class OutputView(View):
    def post(self, request):

        if request.method == 'POST':
            lat_min = request.POST.get('lat_min')
            lat_max = request.POST.get('lat_max')
            long_min = request.POST.get('long_min')
            long_max = request.POST.get('long_max')
            product = request.POST.get('product')
            platform = request.POST.get('platform')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date') 
            print("LAND COVER")
            cmd = 'python /home/localuser/Datacube/NE-GeoCloud/Scripts/land_classification.py '
            cmd1 = 'rm -r /home/localuser/Datacube/NE-GeoCloud/static/assets/results/land_classification/out'
            cmd2 = 'gdal2tiles.py -z 3-14 /home/localuser/Datacube/NE-GeoCloud/static/assets/results/land_classification/out.png'
            cmds = [cmd,cmd1,cmd2]          
            time.sleep(10)                                                                                                                                                                                                                                        

            # p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)                                                                   
            # while p.poll() is None:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
            #     continue
            # out, err = p.communicate()
            # print(out + err)

            # p1 = subprocess.Popen(cmd1, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            # while p1.poll() is None:
            #     continue
            # print("2")
            
            # p2 = subprocess.Popen(cmd2, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=r'/home/localuser/Datacube/NE-GeoCloud/static/assets/results/urbanization')
            # while p2.poll() is None:
            #     continue
            # print(cmd2)
            # print(multiprocessing.cpu_count())
            # _ = input("wait")
            # context = {
            #             'lat_min': lat_min,
            #             'lat_max': lat_max,
            #             'long_min': long_min,
            #             'long_max': long_max,
            #             'product': product,
            #             'platform': platform,
            #             'start_date': start_date,
            #             'end_date': end_date,
            #             'out' : out,
            #             'err' : err
            # }
            # return render(request, 'cloud_coverage/output.html', context)


            image = "/static/assets/results/land_classification/out.png" 
            result = {"image" : image,
                        "lat_min" : lat_min,
                        "lat_max" : lat_max,
                        "long_min" : long_min,
                        "long_max" : long_max,
                        # "out" : out,
                        # "err" : err
                        }
            response = []
            response.append(result)
            
            # context = {
            #             'lat_min': lat_min,
            #             'lat_max': lat_max,
            #             'long_min': long_min,
            #             'long_max': long_max,
            #             'product': product,
            #             'platform': platform,
            #             'start_date': start_date,
            #             'end_date': end_date,
            #             'out' : out,
            #             'err' : err
            # }
            return HttpResponse(json.dumps(response))