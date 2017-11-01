# *****************************************************************************
# scheduler/models.py
# *****************************************************************************

from datetime import date, datetime, timedelta

import pytz
import calendar
# import datetime

from django.db import models
from django.utils import timezone
from django.utils.html import mark_safe


# *****************************************************************************
# Interview
# *****************************************************************************

class Interview(models.Model):
    """
    represents a scheduled candidate interview

    """

    calendar = models.ForeignKey(
        'scheduler.InterviewCalendar',
        blank=True,
        null=True,
        related_name='interviews',
    )
    created = models.DateTimeField(auto_now_add=True)

    canceled = models.BooleanField(default=False)
    canceled_at = models.DateTimeField(blank=True, null=True)

    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)

    def cancel_previous(self):
        """
        cancel any previously scheduled interviews

        """

        previous_interviews = self.application.interviews.exclude(
            pk=self.pk,
        ).filter(canceled=False)

        previous_interviews.update(canceled=True, canceled_at=timezone.now())

    def __str__(self):
        return 'Interview at {}'.format(self.start_time)


# *****************************************************************************
# InterviewCalendar
# *****************************************************************************

class InterviewCalendar(models.Model):
    """
    represents an availability calendar for interview scheduling

    """

    description = models.CharField(max_length=512, blank=True, null=True)
    timezone = models.CharField(
        choices=[(zone, zone) for zone in pytz.common_timezones],
        max_length=32,
    )

    min_hours_notice = models.PositiveIntegerField()
    max_hours_out = models.PositiveIntegerField()

    def __str__(self):
        return '{}'.format(self.description)


# *****************************************************************************
# InterviewConflict
# *****************************************************************************

class InterviewConflict(models.Model):
    """
    represents a block of time in which interviews cannot be scheduled

    """

    calendar = models.ForeignKey(
        'scheduler.InterviewCalendar',
        related_name='conflicts',
    )
    end_time = models.DateTimeField()
    start_time = models.DateTimeField()


# *****************************************************************************
# InterviewSlot
# *****************************************************************************

class InterviewSlot(models.Model):
    """
    represents a block of available weekday time for an interview

    """

    calendar = models.ForeignKey(
        'scheduler.InterviewCalendar',
        related_name='slots',
    )
    end_time = models.TimeField()
    start_time = models.TimeField()

    monday = models.BooleanField(default=False, verbose_name='Mon')
    tuesday = models.BooleanField(default=False, verbose_name='Tue')
    wednesday = models.BooleanField(default=False, verbose_name='Wed')
    thursday = models.BooleanField(default=False, verbose_name='Thur')
    friday = models.BooleanField(default=False, verbose_name='Fri')
    saturday = models.BooleanField(default=False, verbose_name='Sat')
    sunday = models.BooleanField(default=False, verbose_name='Sun')

    max_spots = models.PositiveIntegerField(default=1)


    @property
    def local_tz(self):

        """
        returns pytz timezone for slot

        """
        return pytz.timezone(self.calendar.timezone)


