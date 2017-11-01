# Scheduler System

## Introduction

An interview calendar contains one or more interview slot objects which define what times are available to book,
as well as the maximum number of candidates that can be booked in each slot. A calendar can also contain interview
conflicts. Interview conflicts specify a date and time range during which no interviews can be booked.

An interview calendar also specifies the shortest time in hours from the current time when any interview slot can
be booked, and the maximum number of hours away from the current time when an interview slot can be booked.

## Getting the Application Running

The scheduler is a Dockerized Django REST application. You'll need to make sure that Python and Docker are installed on
your system and correctly configured in order to run the application. The files in this package should be set up
such that once Docker is configured, you can simply run `docker-compose up --build` to rebuild and run the
application. Depending on your environment, you might need to run `docker-compose` as an administrator in order for
the container to start correctly.

If you don't already have Docker on your machine, Docker provides an [installation guide](https://docs.docker.com/engine/installation/).

Note that if you're running Windows or MacOS X, you'll need to use `docker-machine` to set up a virtual environment
that your containers can run in.

### Troubleshooting Port Conflicts

You may run into a problem if you already have applications using port 8000 (for the web server) or port 5432 (for the Postgres instance).

In this case, you can modify the `docker-compose.yml` file to change the port mappings on the host machine.

On lines 8 and 21, you will see lines formatted as
```
      - '<host_machine_port>:<docker_machine_port>'
```

This maps a port on the Docker virtual machine to an actual port on the host machine.

If you are encountering a conflict on port 5432, for example, line 8 currently reads
```
      - '5432:5432'
```

You can change the port on the left side of the colon to remap to a port which is actually available on
your machine, for example:
```
      - '5435:5432'
```

Which will resolve the conflict.

Be aware that if you remap the web server from port 8000 on the host machine, all of the web addresses
you use to access the admin console, etc. will need to use the new host port number.


### Setting up a Superuser

Once the Docker container is up, you'll probably want to add a superuser to the application, so that you can access the
Django admin console and add calendars, interview slots, and conflicts to the database.

To do this, first run `sudo docker-compose exec web bash` from the root of the project to get a root shell on the Docker machine.
Then you can run `python manage.py createsuperuser` to create a superuser.

You'll be prompted to create a username, provide an email address, and set up a password. You can choose whatever is convenient for you.

After you create the superuser, if you navigate to the `/admin` path in the application, you should be able to log in as the superuser
you created and add items to the database through Django's GUI. This will help you test your implementation. Again, if the admin console
doesn't work for some reason and `manage.py` reports that you successfully created the superuser, let us know and we'll try to get things
sorted as soon as we can.


## Class Documentation

There are four major important classes in this project's code that you should be concerned with:
`InterviewSlot`, `InterviewCalender`, `Interview`, and `InterviewConflict`.

### InterviewSlot

`InterviewSlot` represents a repeating block of available time for an interview. An interview
slot is not associated with any particular date--it is an availability from a start time of day
to an end time of day, paired with flags which indicate what day of the week it is.

Additionally, a single `InterviewSlot` may accommodate multiple concurrent `Interview`s on the same
date.

`InterviewSlot` has the following fields:

`calendar` is the `InterviewCalendar` that this `InterviewSlot` is valid on.

`start_time` is the time of day on which this `InterviewSlot` begins.
`end_time` is the time of day on which this `InterviewSlot` ends.

`monday`, `tuesday`, `wednesday`, `thursday`, `friday`, `saturday`, `sunday` are boolean flags
which represent whether this `InterviewSlot` is valid on the corresponding day of the week.

`max_spots` is the maximum number of concurrent `Interview`s that can be scheduled in this
`InterviewSlot`.

`InterviewSlot` also has two methods on it:

`InterviewSlot.local_tz()` returns the local timezone for the calendar that the `InterviewSlot`
is on.

`InterviewSlot.is_available(interview_date)` accepts a `date` as an argument, and determines
whether or not the `InterviewSlot` is currently available to be scheduled on that date.

### InterviewCalendar

An `InterviewCalendar` represents a calendar on which `Interviews` may be scheduled.
`InterviewCalendar` has the following fields:

`description` is a human-readable descripton of the `InterviewCalendar`

`timezone` is the local timezone of the calendar, which may be different from the timezone in
which it is viewed.

`min_hours_notice` represents the smallest amount time in hours ahead of the current time
that an `InterviewSlot` may be considered available for scheduling. For example,
if `min_hours_notice` were `24`, then on Monday at 8 AM in the calendar's local timezone, a candidate
would be able to schedule an `Interview` in a slot that begins on Tuesday at 8 AM or later, but not
at any time before 7 AM on Tuesday, assuming no daylight saving time changes.

`max_hours_out` represents the largest amount of time in hours ahead of the current time
that an `InterviewSlot` may be considered available for scheduling. For example,
if `max_hours_out` were `72`, then on Monday at 8 AM in the calendar's local timezone, a candidate
would be able to schedule an `Interview` in a slot that begins on Thursday at 8 AM or earlier,
but not at any time after Thursday at 8 AM.

`InterviewCalendar` also has a `__str__` method for stringifying itself, which you do not need to
worry about.

### Interview

The `Interview` represents a scheduled candidate interview. It has the following fields:

`calendar` is the calendar this `Interview` appears on.

`created` is a datetime representing when the `Interview` object was created.

`canceled` is a boolean value stating whether or not an interview has been canceled.
`canceled_at` is a datetime value stating when the `Interview` was canceled if it has been canceled.

`start_time` is the start time of the `Interview`.
`end_time` is the end time of the `Interview`.

An Interview also has a `cancel_previous` method which is used to reschedule an interview, and a
`__str__` method which stringifies itself. For the purposes of the coding sample, you can assume that
these methods work correctly and you do not need to modify them.

An `Interview` which is canceled does not count against the number of `Interviews` scheduled
in a given slot.

### InterviewConflict

An `InterviewConflict` represents a block of time during which no interviews may be scheduled.
`InterviewConflict`s have the following fields:

`calendar` is the calendar this `InterviewConflict` appears on.

`start_time` is a datetime value that specifies the date and time at which the conflict begins.

`end_time` is a datetime value that specifies the date and time at which the conflict ends.

An `InterviewSlot` is considered to be unavailabe during an `InterviewConflict` if they overlap at
all, no matter how much or how little time the overlap encompasses.
