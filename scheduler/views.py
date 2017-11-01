# *****************************************************************************
# companies/views.py
# *****************************************************************************

from django.shortcuts import get_object_or_404

from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import (
    InterviewCalendar,
    Interview
)

from .serializers import (
    InterviewCalendarSerializer,
    InterviewSerializer
)

# *****************************************************************************
# InterviewCalendarViewSet
# *****************************************************************************

class InterviewCalendarViewSet(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):

    """
    a ViewSet to list and retrieve InterviewCalendars

    """

    serializer_class = InterviewCalendarSerializer
    queryset = InterviewCalendar.objects.all()

    def get_serializer_context(self):

        """
        adds start and end dates to generate available interview times

        """

        start_date = self.request.query_params.get('startDate', None)
        end_date = self.request.query_params.get('endDate', None)

        return {
            'start_date': start_date,
            'end_date': end_date,
        }

# *****************************************************************************
# InterviewViewSet
# *****************************************************************************

class InterviewViewSet(
        mixins.CreateModelMixin,
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):

    """
    a ViewSet to list Interviews for an 

    """

    serializer_class = InterviewSerializer
    queryset = Interview.objects.all()

    def perform_create(self, serializer):

        """
        add application to serializer for save

        """

        return serializer.save()
