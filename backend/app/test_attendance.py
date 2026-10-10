from attendance import Course, holiday_desc, day_info, course_stats
from datetime import date

# How to run tests:
# cd backend/app
# python -m pytest test_attendance.py -v

# Calendar reference (Aug 2026): Mon 3, Tue 4, Wed 5, Thu 6, Mon 10, Wed 12, Mon 17, Wed 19

def create_course(default_present=True):
    c = Course(
        name="Cálculo",
        max_abs=10,
        default_present=default_present,
        start_date=date(2026, 8, 1),
        end_date=date(2026, 12, 15),
    )
    c.schedule = {0: 2, 2: 2}  # Monday and Wednesday have 2 classes
    return c

def test_holiday_desc():
    c = create_course()
    c.holidays = [
        (date(2026, 9, 1), date(2026, 9, 3), "Feriado"),
        (date(2026, 10, 10), date(2026, 10, 12), "Outro Feriado"),
    ]
    assert holiday_desc(c, date(2026, 9, 1)) == "Feriado"
    assert holiday_desc(c, date(2026, 9, 3)) == "Feriado"
    assert holiday_desc(c, date(2026, 10, 11)) == "Outro Feriado"
    assert holiday_desc(c, date(2026, 9, 4)) is None

def test_day_info_out_of_range():
    c = create_course()
    today = date(2026, 8, 10)

    assert day_info(c, date(2026, 7, 31), today) == {"type": "out"}
    assert day_info(c, date(2026, 12, 16), today) == {"type": "out"}

def test_day_info_no_class():
    c = create_course()
    today = date(2026, 8, 10)

    assert day_info(c, date(2026, 8, 4), today) == {"type": "none"}  # Tuesday
    assert day_info(c, date(2026, 8, 6), today) == {"type": "none"}  # Thursday

def test_day_info_holiday():
    c = create_course()
    c.holidays = [(date(2026, 8, 10), date(2026, 8, 12), "Feriado")]
    today = date(2026, 8, 20)

    assert day_info(c, date(2026, 8, 10), today) == {"type": "holiday", "desc": "Feriado", "schedules": 0, "absences": 0}

def test_day_info_recorded():
    c = create_course()
    c.attendances = {
        date(2026, 8, 3): (2, 0),   # Attended all classes
        date(2026, 8, 5): (2, 1),   # Missed one class
        date(2026, 8, 10): (2, 2),  # Missed all classes
        date(2026, 8, 12): (0, 0),  # Class cancelled
    }
    today = date(2026, 8, 20)

    assert day_info(c, date(2026, 8, 3), today) == {"type": "present", "schedules": 2, "absences": 0}
    assert day_info(c, date(2026, 8, 5), today) == {"type": "partial", "schedules": 2, "absences": 1}
    assert day_info(c, date(2026, 8, 10), today) == {"type": "missed", "schedules": 2, "absences": 2}
    assert day_info(c, date(2026, 8, 12), today) == {"type": "noclass", "schedules": 0, "absences": 0}

def test_day_info_not_recorded():
    c = create_course()
    today = date(2026, 8, 10)

    assert day_info(c, date(2026, 8, 3), today) == {"type": "present", "schedules": 2, "absences": 0, "auto": True}
    assert day_info(c, date(2026, 8, 10), today) == {"type": "pending", "schedules": 2, "absences": 0}
    assert day_info(c, date(2026, 8, 12), today) == {"type": "future", "schedules": 2, "absences": 0}

def test_day_info_not_recorded_default_absent():
    c = create_course(default_present=False)
    today = date(2026, 8, 10)

    assert day_info(c, date(2026, 8, 3), today) == {"type": "missed", "schedules": 2, "absences": 2, "auto": True}

def test_course_stats_safe():
    c = create_course()
    c.attendances = {
        date(2026, 8, 3): (2, 0),
        date(2026, 8, 5): (2, 1),
    }
    today = date(2026, 8, 6)

    assert course_stats(c, today, 50) == {"used": 1, "max": 10, "status": "safe"}

def test_course_stats_warn():
    c = create_course()
    c.attendances = {
        date(2026, 8, 3): (2, 0),
        date(2026, 8, 5): (2, 1),
    }
    today = date(2026, 8, 6)

    # 1 of 10 absences = 10%, which reaches warn_at = 5%
    assert course_stats(c, today, 5) == {"used": 1, "max": 10, "status": "warn"}

def test_course_stats_risk():
    c = create_course(default_present=False)
    today = date(2026, 8, 20)

    # Aug 3, 5, 10, 12, 17, 19 auto-missed: 6 days x 2 classes = 12 absences
    assert course_stats(c, today, 50) == {"used": 12, "max": 10, "status": "risk"}
