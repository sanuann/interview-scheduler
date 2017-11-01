import calendar
from datetime import timedelta, datetime
from scheduler.models import Interview, InterviewConflict


class InterviewScheduleHandler():
    def __init__(self, interview_datetime, interview_slot):
        self.interview_datetime = interview_datetime
        self.interview_slot = interview_slot

    def is_available(self):

        interview_date = self.interview_datetime.date()
        validation_result = False
        if interview_date != None:
            print('INSIDE THE VALIDATION METHOD ' + str(interview_date))
            validation_result = self.check_day_is_valid(interview_date) and \
                                self.check_start_and_end_time_of_slot(interview_date) \
                                and self.check_no_of_interviews_scheduled_in_given_slot() \
                                and self.check_interview_conflict_overlap_with_slot(interview_date)

        return validation_result


    def check_day_is_valid(self, interview_date):

        """
        returns true if interview date falls on a day of week for which the given interview slot is valid

        """
        validation_result = False
        interview_day = calendar.day_name[interview_date.weekday()][:3]
        if interview_day == 'Mon':
            validation_result = self.interview_slot.monday
        elif interview_day == 'Tue':
            validation_result = self.interview_slot.tuesday
        elif interview_day == 'Wed':
            validation_result = self.interview_slot.wednesday
        elif interview_day == 'Thu':
            validation_result = self.interview_slot.thursday
        elif interview_day == 'Fri':
            validation_result = self.interview_slot.friday

        if not validation_result:
            print("check 1 fail. No Interview Slot available on given day")

        return validation_result

    def check_start_and_end_time_of_slot(self, interview_date):
        """
        returns true if start time of given slot is min_hours_notice away from current time and
        at most max_hours_out hours away from current time.

        """
        current_time = self.get_current_time()
        min_limit_time = self.get_min_limit_time(current_time)
        max_limit_time = self.get_max_limit_time(current_time)
        interview_slot_start_time = self.localize_time(interview_date, self.interview_slot.start_time)

        validation_result = (min_limit_time <= interview_slot_start_time <= max_limit_time)
        if not validation_result:
            print("check 2 fail. Start time and end time of interview slots is not within limits")

        return validation_result


    def check_no_of_interviews_scheduled_in_given_slot(self):
        """
        returns true if no. of interviews scheduled in given slot is less than max no. of spots

        """
        interviews = Interview.objects.filter(calendar=self.interview_slot.calendar, canceled=False,
                                              start_time=self.interview_datetime)

        validation_result = (interviews.count() <= self.interview_slot.max_spots)
        if not validation_result:
            print("Check #3 fail. Interview slot is full!!")
        return validation_result


    def check_interview_conflict_overlap_with_slot(self, interview_date):
        """
        returns true if no interview conflicts occur with the given interview slot

        """
        validation_result = True
        interview_conflicts = InterviewConflict.objects.filter(calendar=self.interview_slot.calendar)
        interview_slot_start_time = self.localize_time(interview_date, self.interview_slot.start_time)
        interview_slot_end_time = self.localize_time(interview_date, self.interview_slot.end_time)

        for interview_conflict in interview_conflicts:
            conflict_start_time = interview_conflict.start_time.astimezone(self.interview_slot.local_tz)
            conflict_end_time = interview_conflict.end_time.astimezone(self.interview_slot.local_tz)

            if not (((conflict_start_time < interview_slot_start_time) and (conflict_end_time <= interview_slot_start_time)) or
                        ((conflict_start_time >= interview_slot_end_time) and (conflict_end_time > interview_slot_end_time))):
                validation_result = False
                print('Slot is Conflicting')
                break
        return validation_result


    def localize_time(self, interview_date, slot_time):

        """
        combines date and time and returns local timezone aware datetime for slot

        """
        tz = self.interview_slot.local_tz
        return tz.localize(datetime.combine(interview_date, slot_time))


    def get_current_time(self):
        """
        returns local timezone aware datetime for current time

        """
        tz = self.interview_slot.local_tz
        return datetime.now(tz)


    def get_min_limit_time(self, current_time):
        """
        returns the min time limit for start time of given slot

        """
        return current_time + timedelta(hours=self.interview_slot.calendar.min_hours_notice)


    def get_max_limit_time(self, current_time):
        """
        returns max time limit for start time of given slot

        """
        return current_time + timedelta(hours=self.interview_slot.calendar.max_hours_out)





