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

from apps.data_cube_manager import models
from apps.dc_algorithm import forms


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
    tool_inputs = None
    task_model_name = None
    tool_satellites = None

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

    def _get_task_model_name(self):
        """Get the task_model_name property

        The task model name must be usable for querying for a model with apps.get_model.
        Meant to implement a general NotImplementedError for required properties

        Raises:
            NotImplementedError in the case of task_model_name not being defined

        Returns:
            The value of task_model_name.

        """
        if self.task_model_name is None:
            raise NotImplementedError(
                "You must specify a task_model_name in classes that inherit"
                "ToolClass. See the ToolClass and dc_algorithm.models docstring"
                "for more details."
            )
        return self.task_model_name

    def _get_tool_model(self, model):
        """Get a model from the subclassing tool

        Used to get a model from the specific tool - e.g. if tool
        'custom_mosaic_tool' subclasses this, you can get
        custom_mosaic_tool.Query by calling self._get_tool_model('query')

        Returns:
            Model class requested by 'model'
        """

        return apps.get_model('.'.join([self._get_tool_name(), model]))


class DataCubeVisualization(ToolClass, View):
    """Visualize ingested and indexed Data Cube regions using leaflet"""

    tool_name = self._get_tool_name()

    def get(self, request):
        """Main end point for viewing datasets and their extents on a leaflet map"""
        context = {'form': forms.VisualizationForm(),
                   'tool_name': self.tool_name,
                   }
        context['dataset_types'] = models.DatasetType.objects.using('agdc').filter(
            definition__has_keys=['measurements'])
        context['tool_inputs'] = self.tool_inputs
        return render(request, 'trial.html', context)


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