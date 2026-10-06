from dataclasses import dataclass, field
from datetime import date
@dataclass
class Course:
    name: str
    max_abs: int
    default_present: bool
    start_date: date
    end_date: date
    schedule: dict = field(default_factory=dict)
    attendances: dict = field(default_factory=dict)
    holidays: list = field(default_factory=list)

def holiday_desc(course, day):
    for inicio, fim, desc in course.holidays:
        if inicio <= day <= fim:
            return desc
    return None

def day_info(course, day, today):
    if (day < course.start_date or day > course.end_date):
        return {"type": "out"}

    schedules_day = course.schedule.get(day.weekday(), 0)
    attendances_day = course.attendances.get(day)
    holiday_description = holiday_desc(course, day)

    if (holiday_description):
        return {"type": "holiday", "desc": holiday_description, "schedules": 0, "absences": 0}

    if not schedules_day and not attendances_day:
        return {"type": "none"}
    
    if (attendances_day):
        classes, absences = attendances_day
        if (classes == 0):
            return {"type": "noclass", "schedules": 0, "absences": 0}

        if (absences == 0):
            t = "present"
        elif (absences >= classes):
            t = "missed"
        else:
            t = "partial"
        return {"type": t, "schedules": classes, "absences": absences}
    
    if day > today:
        return {"type": "future", "schedules": schedules_day, "absences": 0}
    
    if day == today:
        return {"type": "pending", "schedules": schedules_day, "absences": 0}

    if (course.default_present):
        return {"type": "present", "schedules": schedules_day, "absences": 0, "auto": True}
    
    return {"type": "missed", "schedules": schedules_day, "absences": schedules_day, "auto": True}
    
def course_stats(course, today, warn_at):
    used = 0
    day = course.start_date

    while day <= course.end_date:
        info = day_info(course, day, today)
        if info["type"] in ["present", "partial", "missed"]:
            used += info["absences"]
        day += timedelta(days=1)
    
    if used >= course.max_abs:
        return {"used": used, "max": course.max_abs, "status": "risk"}
    elif used / course.max_abs * 100 >= warn_at:
        return {"used": used, "max": course.max_abs, "status": "warn"}
    else:
        return {"used": used, "max": course.max_abs, "status": "safe"}

