# *****************************************************************************
# scheduler/serializers.py
# *****************************************************************************

from datetime import datetime, timedelta

import rest_framework.serializers as serializers
from django.utils.dateparse import parse_date
from django.shortcuts import get_object_or_404

from scheduler.helpers.InterviewScheduleHandler import InterviewScheduleHandler
from . import models
from .enums import Weekday


# *****************************************************************************
# InterviewSlotSerializer
# *****************************************************************************

class InterviewSlotSerializer(serializers.ModelSerializer):

    """
    serializes an available interview slot

    """

    end_time = serializers.DateTimeField(read_only=True)
    start_time = serializers.DateTimeField(read_only=True)
    slot_id = serializers.IntegerField(read_only=True, source='id')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['end_time'] = serializers.SerializerMethodField()
        self.fields['start_time'] = serializers.SerializerMethodField()

    def _get_datetime(self, time, local_tz):
        dt = datetime.combine(self.context.get('date'), time)
        return local_tz.localize(dt).isoformat()

    def get_end_time(self, obj):

        """
        convert end time to a timezone aware datetime

        """

        return self._get_datetime(obj.end_time, obj.local_tz)

    def get_start_time(self, obj):

        """
        convert start time to a timezone aware datetime

        """

        return self._get_datetime(obj.start_time, obj.local_tz)

    class Meta:
        model = models.InterviewSlot
        fields = (
            'calendar',
            'end_time',
            'max_spots',
            'slot_id',
            'start_time',
        )


# *****************************************************************************
# InterviewCalendarSerializer
# *****************************************************************************

class InterviewCalendarSerializer(serializers.ModelSerializer):

    """
    serializes an interview calendar with available time slots

    """

    slots = serializers.SerializerMethodField()

    def _get_slots_for_date(self, calendar, date):

        """
        return available slots for particular date

        """

        filter_kwargs = {
            Weekday(date.weekday()).name: True,
        }

        slots = calendar.slots.filter(**filter_kwargs)
        slots = [slot for slot in slots if slot.is_available(date)]

        serializer = InterviewSlotSerializer(
            slots,
            context={'date': date},
            many=True,
        )

        return serializer.data

    def get_slots(self, obj):

        """
        generate set of available interview times for date range

        """

        start_date = self.context.get('start_date')
        end_date = self.context.get('end_date')

        if not start_date or not end_date:
            return []

        start = parse_date(start_date)
        end = parse_date(end_date)

        available_slots = []
        while start <= end:
            available_slots.extend(self._get_slots_for_date(obj, start))
            start = start + timedelta(days=1)

        return available_slots

    class Meta:
        model = models.InterviewCalendar
        fields = (
            'id',
            'description',
            'slots',
            'timezone',
        )


# *****************************************************************************
# InterviewSerializer
# *****************************************************************************

class InterviewSerializer(serializers.ModelSerializer):

    """
    serializer to create and serialize an application's Interviews

    """

    slot_id = serializers.IntegerField(write_only=True)

    def create(self, validated_data):

        """
        add Location and InterviewCalendar to serializer data

        """
        slot_id = validated_data.pop('slot_id')
        slot = get_object_or_404(models.InterviewSlot, pk=slot_id)
        # check that interview time is still available
        handler = InterviewScheduleHandler(validated_data.get('start_time'), slot)

        if not handler.is_available():
            raise serializers.ValidationError(
                'Interview time is no longer available',
            )

        #if not slot.is_available(validated_data.get('start_time')):
        #    raise serializers.ValidationError(
        #        'Interview time is no longer available',
        #    )

        validated_data['calendar'] = slot.calendar

        return models.Interview.objects.create(**validated_data)

    class Meta():
        model = models.Interview
        fields = (
            'id',
            'calendar',
            'canceled',
            'canceled_at',
            'created',
            'end_time',
            'slot_id',
            'start_time',
        )
