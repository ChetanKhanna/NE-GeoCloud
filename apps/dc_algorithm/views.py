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

from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.apps import apps
import json
from django.template.loader import render_to_string
from apps.data_cube_manager import models
from apps.dc_algorithm import forms

from .models import Area, Application, ApplicationGroup

class Parameter:
    name = None
    variable = None
    min = 0
    max = 80
    help = None

class ToolClass:
    """Base class for all Tool related classes

    Contains common functions for tool related views, e.g. getting tool names etc.
    Attributes defined here will be required for all inheriting classes and will raise
    NotImplementedErrors for required fields.

    Attributes:
        tool_name: label for the tool that the class is used in.
            e.g. custom_mosaic_tool, water_detection, etc.

    """

    tool_name = None
    tool_id = None
    tool_inputs = 0
    task_model_name = None
    tool_satellites = None
    tool_parameters = 0

    def _get_tool_name(self):
        """Get the tool_name property

        Meant to implement a general NotImplementedError for required properties

        Raises:
            NotImplementedError in the case of tool_name not being defined

        Returns:
            The value of tool_name.

        """
        # if self.tool_name is None:
        #     raise NotImplementedError(
        #         "You must specify a tool_name in classes that inherit ToolClass. See the ToolClass docstring for more details."
        #     )
        return self.tool_name


class DataCubeVisualization(ToolClass, View):
    """Visualize ingested and indexed Data Cube regions using leaflet"""

    def get(self, request):
        """Main end point for viewing datasets and their extents on a leaflet map"""
        tool_name = self._get_tool_name()
        form = []
        for i in range(self.tool_inputs):
            form.append(forms.VisualizationForm(i, satellites=self.tool_satellites))

        context = {'form': form,
                    'tool_name': self.tool_name,
                    'tool_id': self.tool_id,
                }
        return render(request, 'dc_algorithm/visualization.html', context)


class GetIngestedAreas(View):
    """Get a dict containing details on the ingested areas, grouped by Platform"""

    def get(self, request):
        """Call a synchronous task to produce a dict containing ingestion details

        Work performed in a synchrounous task so the execution is done on a worker rather than on
        the webserver. Gets a dict like:
            {Landsat_5: [{}, {}, {}],
            Landsat_7: [{}, {}, {}]}
        """

        platforms = models.IngestionDetails.objects.filter(
            global_dataset=False).order_by().values_list('platform').distinct()

        ingested_area_details = {
            platform[0]: [
                ingestion_detail_listing.get_serialized_response()
                for ingestion_detail_listing in models.IngestionDetails.objects.filter(
                    global_dataset=False, platform=platform[0])
            ]
            for platform in platforms
        }

        return JsonResponse(ingested_area_details)


def post(self, request):

    if request.method == 'POST':
        if 'lat_min' in request.POST:
            print(request.POST)
            params = request.POST['postdata']
            ingestion_data = params['ingestion_data']
            # cmd = 'python apps/cloud_coverage/cloud_coverage.py' + coords_arr[0] + coords_arr[1] + coords_arr[2] + coords_arr[5] ingestion_data
            # p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            return render(request, 'dc_algorithm/output.html', params)
    else:
        return HttpResponseBadRequest('Only POST requests are allowed')
    