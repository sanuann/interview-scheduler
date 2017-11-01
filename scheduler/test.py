import pytz
from django.test import TestCase

from scheduler.models import InterviewSlot, InterviewCalendar, InterviewConflict, Interview
from .helpers.InterviewScheduleHandler import InterviewScheduleHandler
from datetime import datetime

class InterviewScheduleHandlerTestCase(TestCase):
    
    def setUp(self):
        interview_calendar_instance = InterviewCalendar.objects.create(description = "US NorthEast Zone",
                                                                       timezone = "US/Eastern", min_hours_notice = 5,
                                                                       max_hours_out = 72)
        slot_start_time = (datetime(year=2017, month=10, day=30, hour=14, minute=00)).time()
        slot_end_time = (datetime(year=2017, month=10, day=30, hour=16, minute=00)).time()

        interview_slot_instance = InterviewSlot.objects.create(calendar = interview_calendar_instance,
                                                               start_time = slot_start_time, end_time = slot_end_time,
                                                               monday = True, tuesday = True, wednesday = True,
                                                               thursday = False, friday = False, saturday = False,
                                                               sunday = False, max_spots = 15)
        tz = pytz.timezone(interview_calendar_instance.timezone)
        interview_datetime = datetime(year=2017, month=10, day=30, hour=14, minute=00)
        self.interview_datetime = tz.localize(interview_datetime)
        self.interview_slot = interview_slot_instance
        handler_instance = InterviewScheduleHandler(self.interview_datetime, self.interview_slot)
        self.handler = handler_instance
        self.interview_calendar = interview_calendar_instance

    
    def test_is_available_with_monday_slot(self):
        result = self.handler.is_available()
        self.assertTrue(result, 'slot available on monday? {}'.format(result))
    

    def test_is_available_with_no_monday_slot(self):
        self.interview_slot.monday = False
        result = self.handler.is_available()
        self.assertFalse(result, 'slot not available on monday? {}'.format(result))
     

    def test_check_day_is_valid(self):
        result = self.handler.is_available()
        self.assertTrue(result, 'Interview day is one of the weekday for which the given slot is valid? {}'.format(result))


    def test_is_available_start_time_of_slot_is_within_limit(self):
        result = self.handler.is_available()
        self.assertTrue(result, 'slot start time is within min hour notice limit? {}'.format(result))


    def test_is_available_start_time_of_slot_is_not_within_limit(self):
        self.interview_calendar.min_hours_notice = 50
        result = self.handler.is_available()
        self.assertFalse(result, 'slot start time is not within min hour notice limit? {}'.format(result))


    def test_is_available_end_time_of_slot_is_within_limit(self):
        result = self.handler.is_available()
        self.assertTrue(result, 'slot end time is within max hour out limit? {}'.format(result))


    def test_is_available_end_time_of_slot_is_not_within_limit(self):
        self.interview_calendar.min_hours_notice = 48
        result = self.handler.is_available()
        self.assertFalse(result, 'slot end time is not within max hour out limit? {}'.format(result))    

    def test_is_available_no_of_interviews_scheduled_in_given_slot_less_than_max_spots(self):
        start_time = self.interview_datetime
        tz = pytz.timezone(self.interview_calendar.timezone)
        end_time = datetime(year=2017, month=10, day=30, hour=16, minute=00, tzinfo=tz)
        Interview.objects.create(calendar=self.interview_calendar, start_time= start_time, end_time= end_time)
        result = self.handler.is_available()
        self.assertTrue(result, 'No. of interviews scheduled is less than max spots? {}'.format(result))


    def test_is_available_no_of_interviews_scheduled_in_given_slot_exceeds_max_spots(self):
        self.interview_slot.max_spots = 0
        start_time = self.interview_datetime
        tz = pytz.timezone(self.interview_calendar.timezone)
        end_time = (datetime(year=2017, month=10, day=30, hour=16, minute=00, tzinfo=tz))
        Interview.objects.create(calendar=self.interview_calendar, start_time= start_time, end_time= end_time)
        result = self.handler.is_available()
        self.assertFalse(result, 'No. of interviews scheduled exceeds max spots? {}'.format(result))     


    def test_is_available_no_interview_conflict_overlap_with_slot(self):
        tz = pytz.timezone(self.interview_calendar.timezone)
        start_time = (datetime(year=2017, month=10, day=30, hour=6, minute=00, tzinfo=tz))
        end_time = (datetime(year=2017, month=10, day=30, hour=10, minute=30, tzinfo=tz))
        InterviewConflict.objects.create(calendar=self.interview_calendar, start_time= start_time, end_time= end_time)
        result = self.handler.is_available()
        self.assertTrue(result, 'No interview conflict overlap occurs with slot? {}'.format(result))

    
    def test_is_available_interview_conflict_start_time_overlaps_with_slot(self):
        tz = pytz.timezone(self.interview_calendar.timezone)
        start_time = (datetime(year=2017, month=10, day=30, hour=15, minute=00, tzinfo=tz))
        end_time = (datetime(year=2017, month=10, day=30, hour=17, minute=30, tzinfo=tz))
        InterviewConflict.objects.create(calendar=self.interview_calendar, start_time= start_time, end_time= end_time)
        result = self.handler.is_available()
        self.assertFalse(result, 'Interview conflict start time overlaps with slot? {}'.format(result))    


    def test_is_available_interview_conflict_end_time_overlaps_with_slot(self):
        tz = pytz.timezone(self.interview_calendar.timezone)
        start_time = (datetime(year=2017, month=10, day=30, hour=12, minute=00, tzinfo=tz))
        end_time = (datetime(year=2017, month=10, day=30, hour=15, minute=30, tzinfo=tz))
        InterviewConflict.objects.create(calendar=self.interview_calendar, start_time= start_time, end_time= end_time)
        result = self.handler.is_available()                                                           
        self.assertFalse(result, 'Interview conflict end time overlaps with slot? {}'.format(result))       


    def test_is_available_conflict_when_slot_lies_entirely_between_interview_conflict(self):
        tz = pytz.timezone(self.interview_calendar.timezone)
        start_time = (datetime(year=2017, month=10, day=30, hour=13, minute=00, tzinfo=tz))
        end_time = (datetime(year=2017, month=10, day=30, hour=17, minute=30, tzinfo=tz))
        InterviewConflict.objects.create(calendar=self.interview_calendar, start_time= start_time, end_time= end_time)
        result = self.handler.is_available()
        self.assertFalse(result, 'Interview conflict when slot lies between it? {}'.format(result))


    def test_is_available_no_interview_conflict_when_no_objects_of_conflict(self):
        result = self.handler.is_available()
        self.assertTrue(result, 'Interview conflict when slot lies between it? {}'.format(result))                   