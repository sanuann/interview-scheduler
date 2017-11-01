# *****************************************************************************
# scheduler/admin.py
# *****************************************************************************

from django.contrib import admin

from . import models


# *****************************************************************************
# InterviewAdmin
# *****************************************************************************

@admin.register(models.Interview)
class InterviewAdmin(admin.ModelAdmin):

    """
    """

    pass


# *****************************************************************************
# InterviewCalendarAdmin
# *****************************************************************************

@admin.register(models.InterviewCalendar)
class InterviewCalendarAdmin(admin.ModelAdmin):

    """
    """

    inlines = (
        type(str('InterviewSlotInlineAdmin'), (admin.TabularInline, object), {
            'extra': 0,
            'fields': (
                'start_time',
                'end_time',
                'monday',
                'tuesday',
                'wednesday',
                'thursday',
                'friday',
                'saturday',
                'sunday',
                'max_spots',
            ),
            'model': models.InterviewSlot,
        }),
        type(str('ConflictInlineAdmin'), (admin.TabularInline, object), {
            'extra': 0,
            'fields': (
                'start_time',
                'end_time',
            ),
            'model': models.InterviewConflict,
        }),
    )
