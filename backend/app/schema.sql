CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    hash_password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS courses (
    course_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    absence_limit INTEGER NOT NULL DEFAULT 0 CHECK (absence_limit >= 0),
    default_presence BOOLEAN NOT NULL DEFAULT TRUE,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    CHECK (end_date >= start_date)
);

CREATE TABLE IF NOT EXISTS schedule (
    schedule_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    course_id INTEGER NOT NULL REFERENCES courses(course_id) ON DELETE CASCADE,
    weekday INTEGER NOT NULL CHECK (weekday BETWEEN 0 AND 6),
    qtd_classes INTEGER NOT NULL DEFAULT 1 CHECK (qtd_classes > 0),
    UNIQUE (course_id, weekday)
);

CREATE TABLE IF NOT EXISTS attendance (
    attendance_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    course_id INTEGER NOT NULL REFERENCES courses(course_id) ON DELETE CASCADE,
    date DATE NOT NULL,
    qtd_classes INTEGER NOT NULL DEFAULT 1 CHECK (qtd_classes >= 0),
    absences INTEGER NOT NULL DEFAULT 0,
    UNIQUE (course_id, date),
    CHECK (absences BETWEEN 0 AND qtd_classes)
);

CREATE TABLE IF NOT EXISTS holidays (
    holiday_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    description TEXT NOT NULL,
    CHECK (end_date >= start_date)
);

