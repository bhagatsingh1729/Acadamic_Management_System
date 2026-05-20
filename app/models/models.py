# =============================================================
# models.py
# SQLAlchemy Models — College ERP MVP
# =============================================================
# Every table from erp_schema_mvp.sql is represented here.
# Conversion map (SQLite → SQLAlchemy):
#
#   updated_at triggers        → TimestampMixin  (onupdate=)
#   BEFORE INSERT/UPDATE trigs → @validates()    (on Marks, ClassSession)
#   PRAGMA foreign_keys = ON   → event listener  (in database.py)
#   CREATE INDEX               → Index()         in __table_args__
#   CHECK constraints          → CheckConstraint() in __table_args__
#   UNIQUE constraints         → UniqueConstraint() in __table_args__
# =============================================================

from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, validates

from app.database import Base


# =============================================================
# TIMESTAMP MIXIN
# =============================================================
# Replaces ALL the updated_at triggers from the SQLite schema.
#
# SQLite trigger (replaced):
#   CREATE TRIGGER trg_user_updated_at AFTER UPDATE ON User ...
#   BEGIN UPDATE User SET updated_at = CURRENT_TIMESTAMP ... END;
#
# SQLAlchemy equivalent:
#   onupdate=datetime.utcnow → auto-stamps on every UPDATE.
#   Works across SQLite, Postgres, and MySQL with zero changes.
#
# Every model inherits this mixin — no repetition needed.
# =============================================================
class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow,  nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow, nullable=False)


# =============================================================
# USER
# =============================================================
# Central identity table. Every person in the system has a User row.
# Role-specific data lives in Student / Faculty / Admin tables.
#
# SQLite source:
#   CREATE TABLE "User" (role TEXT CHECK(role IN ('student','faculty','admin')), ...)
# =============================================================
class User(TimestampMixin, Base):
    __tablename__ = "user"

    id       = Column(Integer, primary_key=True, autoincrement=True)
    name     = Column(String,  nullable=False)
    email    = Column(String,  nullable=False, unique=True)
    role     = Column(String,  nullable=False)       # 'student' | 'faculty' | 'admin'|'hod'
    password = Column(String,  nullable=False)       # ALWAYS store bcrypt/argon2 hash
    phone_no = Column(String,  nullable=True)
    dob      = Column(String,  nullable=True)
    address  = Column(String,  nullable=True)

    __table_args__ = (
        # Replaces: CHECK(role IN ('student', 'faculty', 'admin'))
        CheckConstraint("role IN ('student', 'faculty', 'admin', 'hod')", name="ck_user_role"),
        # Replaces: CREATE INDEX idx_user_email ON "User" (email)
        Index("idx_user_email", "email"),
        # Replaces: CREATE INDEX idx_user_name ON "User" (name)
        Index("idx_user_name", "name"),
    )

    # One User IS exactly one of these (one-to-one)
    student = relationship("Student", back_populates="user", uselist=False)
    faculty = relationship("Faculty", back_populates="user", uselist=False)
    admin   = relationship("Admin",   back_populates="user", uselist=False)

    # UPDATE AFTER ADDING HOD TABLE
    hod = relationship("HOD",back_populates="user",uselist=False)

    def __repr__(self):
        return f"<User id={self.id} name={self.name!r} role={self.role!r}>"


# =============================================================
# BRANCH
# =============================================================
# Engineering branches: CSE, ECE, Mechanical, Civil, etc.
# =============================================================
class Branch(TimestampMixin, Base):
    __tablename__ = "branch"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    name       = Column(String,  nullable=False, unique=True)
    branch_uid = Column(String,  nullable=False, unique=True)

    # One Branch → one Admin (MVP: UNIQUE on Admin.branch_id)
    admin = relationship("Admin", back_populates="branch", uselist=False)

    # One Branch → many Students
    students = relationship("Student", back_populates="branch")

    # One Branch → many BranchSubject rows
    branch_subjects = relationship(
        "BranchSubject",
        back_populates="branch",
        cascade="all, delete-orphan",  # deleting a Branch removes its BranchSubject rows
    )

    # Shortcut: branch.subjects → list of Subject objects (read-only)
    # To add a subject: create a BranchSubject row directly
    subjects = relationship(
        "Subject",
        secondary="branch_subject",
        back_populates="branches",
        viewonly=True,
    )

    def __repr__(self):
        return f"<Branch id={self.id} name={self.name!r}>"


# =============================================================
# DEPARTMENT
# =============================================================
# Academic departments: Dept of CS, Dept of Maths, etc.
# Separate from Branch so one Maths dept can serve all branches.
# =============================================================
class Department(TimestampMixin, Base):
    __tablename__ = "department"

    id       = Column(Integer, primary_key=True, autoincrement=True)
    name     = Column(String,  nullable=False, unique=True)
    dept_uid = Column(String,  nullable=False, unique=True)

    # One Department → many Faculty members
    faculty = relationship("Faculty", back_populates="department")

    #UPDATE AFTER ADDING HOD TABLE
    hod = relationship("HOD",back_populates="department",uselist=False)

    def __repr__(self):
        return f"<Department id={self.id} name={self.name!r}>"


# =============================================================
# SUBJECT
# =============================================================
# Stands alone — NOT tied to a single branch (unlike SQLite v1).
# Branch linkage is through BranchSubject junction table.
#
# SQLite source:
#   branch_id was removed; now handled via Branch_Subject junction.
# =============================================================
class Subject(TimestampMixin, Base):
    __tablename__ = "subject"

    id       = Column(Integer, primary_key=True, autoincrement=True)
    name     = Column(String,  nullable=False, unique=True)
    code     = Column(String,  nullable=False, unique=True)  # e.g. "CS301", "MA201"
    semester = Column(Integer, nullable=False)

    __table_args__ = (
        # Replaces: CHECK(semester >= 1 AND semester <= 8)
        CheckConstraint("semester >= 1 AND semester <= 8", name="ck_subject_semester"),
        # Replaces: CREATE INDEX idx_subject_code ON "Subject" (code)
        Index("idx_subject_code", "code"),
    )

    # Junction relationships
    branch_subjects  = relationship("BranchSubject",  back_populates="subject", cascade="all, delete-orphan")
    faculty_subjects = relationship("FacultySubject", back_populates="subject", cascade="all, delete-orphan")
    student_subjects = relationship("StudentSubject", back_populates="subject", cascade="all, delete-orphan")

    # Direct relationships
    class_sessions = relationship("ClassSession", back_populates="subject")
    exams          = relationship("Exam",         back_populates="subject")

    # Shortcuts (read-only)
    branches = relationship(
        "Branch",
        secondary="branch_subject",
        back_populates="subjects",
        viewonly=True,
    )
    faculty_members = relationship(
        "Faculty",
        secondary="faculty_subject",
        back_populates="subjects",
        viewonly=True,
    )
    students = relationship(
        "Student",
        secondary="student_subject",
        back_populates="subjects",
        viewonly=True,
    )

    def __repr__(self):
        return f"<Subject id={self.id} code={self.code!r} semester={self.semester}>"


# =============================================================
# BRANCH_SUBJECT  (junction)
# =============================================================
# Replaces Subject.branch_id from SQLite v1.
# "Maths" can now belong to CSE, ECE, and ME — one row each.
#
# SQLite source:
#   CREATE TABLE "Branch_Subject" (branch_id, subject_id, UNIQUE(branch_id, subject_id))
# =============================================================
class BranchSubject(Base):
    __tablename__ = "branch_subject"

    id         = Column(Integer,  primary_key=True, autoincrement=True)
    branch_id  = Column(Integer,  ForeignKey("branch.id",  ondelete="CASCADE"), nullable=False)
    subject_id = Column(Integer,  ForeignKey("subject.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        # Replaces: UNIQUE(branch_id, subject_id)
        UniqueConstraint("branch_id", "subject_id", name="uq_branch_subject"),
    )

    branch  = relationship("Branch",  back_populates="branch_subjects")
    subject = relationship("Subject", back_populates="branch_subjects")

    def __repr__(self):
        return f"<BranchSubject branch_id={self.branch_id} subject_id={self.subject_id}>"


# =============================================================
# FACULTY
# =============================================================
class Faculty(TimestampMixin, Base):
    __tablename__ = "faculty"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    user_id     = Column(Integer, ForeignKey("user.id",       ondelete="CASCADE"),  nullable=False, unique=True)
    employee_id = Column(String,  nullable=False, unique=True)
    dept_id     = Column(Integer, ForeignKey("department.id", ondelete="SET NULL"), nullable=True)

    __table_args__ = (
        # Replaces: CREATE INDEX idx_faculty_employee_id ON "Faculty" (employee_id)
        Index("idx_faculty_employee_id", "employee_id"),
    )

    user       = relationship("User",       back_populates="faculty")
    department = relationship("Department", back_populates="faculty")

    faculty_subjects = relationship(
        "FacultySubject",
        back_populates="faculty",
        cascade="all, delete-orphan",
    )
    class_sessions = relationship("ClassSession", back_populates="faculty")

    # Shortcut: faculty.subjects → list of Subject objects (read-only)
    subjects = relationship(
        "Subject",
        secondary="faculty_subject",
        back_populates="faculty_members",
        viewonly=True,
    )

    def __repr__(self):
        return f"<Faculty id={self.id} employee_id={self.employee_id!r}>"


# =============================================================
# STUDENT
# =============================================================
# batch:   "2023-27" — the 4-year enrollment span.
#          Without this, Sem-3 CSE students from 2023 and 2024
#          are the same thing in your DB. That breaks everything.
#
# section: "A", "B", "C" — class section within branch+semester.
#          DEFAULT "A" so colleges without sections work fine.
#
# SQLite source:
#   "batch" TEXT NOT NULL, "section" TEXT NOT NULL DEFAULT 'A'
# =============================================================
class Student(TimestampMixin, Base):
    __tablename__ = "student"

    id        = Column(Integer, primary_key=True, autoincrement=True)
    user_id   = Column(Integer, ForeignKey("user.id",   ondelete="CASCADE"),  nullable=False, unique=True)
    branch_id = Column(Integer, ForeignKey("branch.id", ondelete="SET NULL"), nullable=False) #made branch_id nullable=False to enforce that every student must belong to a branch
    usn       = Column(String,  nullable=False, unique=True)
    semester  = Column(Integer, nullable=False)
    batch     = Column(String,  nullable=False)              # e.g. "2023-27"
    section   = Column(String,  nullable=False, default="A") # e.g. "A", "B", "C"

    __table_args__ = (
        # Replaces: CHECK(semester >= 1 AND semester <= 8)
        CheckConstraint("semester >= 1 AND semester <= 8", name="ck_student_semester"),
        # Replaces: CREATE INDEX idx_student_usn   ON "Student" (usn)
        Index("idx_student_usn",   "usn"),
        # Replaces: CREATE INDEX idx_student_batch ON "Student" (batch)
        Index("idx_student_batch", "batch"),
    )

    user   = relationship("User",   back_populates="student")
    branch = relationship("Branch", back_populates="students")

    student_subjects = relationship(
        "StudentSubject",
        back_populates="student",
        cascade="all, delete-orphan",
    )
    marks       = relationship("Marks",      back_populates="student", cascade="all, delete-orphan")
    attendances = relationship("Attendance", back_populates="student", cascade="all, delete-orphan")

    # Shortcut: student.subjects → list of Subject objects (read-only)
    subjects = relationship(
        "Subject",
        secondary="student_subject",
        back_populates="students",
        viewonly=True,
    )

    def __repr__(self):
        return f"<Student id={self.id} usn={self.usn!r} batch={self.batch!r} section={self.section!r}>"


# =============================================================
# ADMIN
# =============================================================
# MVP: one admin per branch — UNIQUE on branch_id.
#
# To scale later (multi-admin):
#   Remove unique=True from branch_id.
#   That's the only change needed.
#
# SQLite source:
#   "branch_id" INTEGER UNIQUE  ← one admin per branch
# =============================================================
class Admin(TimestampMixin, Base):
    __tablename__ = "admin"

    id        = Column(Integer, primary_key=True, autoincrement=True)
    user_id   = Column(Integer, ForeignKey("user.id",   ondelete="CASCADE"),  nullable=False, unique=True)
    branch_id = Column(Integer, ForeignKey("branch.id", ondelete="SET NULL"), nullable=True,  unique=True)

    user   = relationship("User",   back_populates="admin")
    branch = relationship("Branch", back_populates="admin")

    def __repr__(self):
        return f"<Admin id={self.id} branch_id={self.branch_id}>"


# =============================================================
# FACULTY_SUBJECT  (junction)
# =============================================================
# Which faculty teaches which subjects (many-to-many).
#
# SQLite source:
#   CREATE TABLE "Faculty_Subject" (faculty_id, subject_id, UNIQUE(faculty_id, subject_id))
# =============================================================
class FacultySubject(Base):
    __tablename__ = "faculty_subject"

    id         = Column(Integer,  primary_key=True, autoincrement=True)
    faculty_id = Column(Integer,  ForeignKey("faculty.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Integer,  ForeignKey("subject.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        # Replaces: UNIQUE(faculty_id, subject_id)
        UniqueConstraint("faculty_id", "subject_id", name="uq_faculty_subject"),
    )

    faculty = relationship("Faculty", back_populates="faculty_subjects")
    subject = relationship("Subject", back_populates="faculty_subjects")

    def __repr__(self):
        return f"<FacultySubject faculty_id={self.faculty_id} subject_id={self.subject_id}>"


# =============================================================
# STUDENT_SUBJECT  (junction)
# =============================================================
# Which students are enrolled in which subjects (many-to-many).
#
# SQLite source:
#   CREATE TABLE "Student_Subject" (student_id, subject_id, UNIQUE(student_id, subject_id))
# =============================================================
class StudentSubject(Base):
    __tablename__ = "student_subject"

    id         = Column(Integer,  primary_key=True, autoincrement=True)
    student_id = Column(Integer,  ForeignKey("student.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Integer,  ForeignKey("subject.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        # Replaces: UNIQUE(student_id, subject_id)
        UniqueConstraint("student_id", "subject_id", name="uq_student_subject"),
    )

    student = relationship("Student", back_populates="student_subjects")
    subject = relationship("Subject", back_populates="student_subjects")

    def __repr__(self):
        return f"<StudentSubject student_id={self.student_id} subject_id={self.subject_id}>"


# =============================================================
# CLASS SESSION
# =============================================================
# One physical class that happened or is scheduled.
# batch + section tie each session to the right student cohort.
#
# SQLite source:
#   CHECK(end_time > start_time)
#   UNIQUE(faculty_id, subject_id, date, start_time, section)
#
# The CHECK is enforced two ways:
#   1. CheckConstraint → enforced at DB level
#   2. @validates      → enforced at Python level (catches it before hitting DB)
# =============================================================
class ClassSession(TimestampMixin, Base):
    __tablename__ = "class_session"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    faculty_id = Column(Integer, ForeignKey("faculty.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subject.id", ondelete="CASCADE"), nullable=False)
    date       = Column(Date,    nullable=False)
    start_time = Column(Time,    nullable=False)
    end_time   = Column(Time,    nullable=False)
    #Adding Semester to make sure that students of only that semester can attend the class session
    semester = Column(Integer, nullable=False)
    batch      = Column(String,  nullable=False)               # matches Student.batch
    section    = Column(String,  nullable=False, default="A")  # matches Student.section

    __table_args__ = (
        # Replaces: CHECK(end_time > start_time)
        CheckConstraint("end_time > start_time", name="ck_classsession_time"),
        #Adding an check constraint for semester
        CheckConstraint("semester >= 1 AND semester <= 8",name="ck_classsession_semester"),
        # Replaces: UNIQUE(faculty_id, subject_id, date, start_time, section)
        UniqueConstraint(
            "faculty_id", "subject_id", "date", "start_time", "section",
            name="uq_classsession",
        ),
    )

    faculty     = relationship("Faculty",    back_populates="class_sessions")
    subject     = relationship("Subject",    back_populates="class_sessions")
    attendances = relationship("Attendance", back_populates="class_session", cascade="all, delete-orphan")

    @validates("end_time")
    def validate_end_time(self, key, end_time):
        """
        Replaces: CHECK(end_time > start_time) at the Python layer.
        Fires whenever end_time is assigned — catches bad data
        before it even reaches the DB.
        """
        if self.start_time and end_time <= self.start_time:
            raise ValueError(
                f"end_time ({end_time}) must be after start_time ({self.start_time})"
            )
        return end_time

    def __repr__(self):
        return (
            f"<ClassSession id={self.id} date={self.date} "
            f"batch={self.batch!r} section={self.section!r}>"
        )


# =============================================================
# EXAM
# =============================================================
# semester + batch scope every exam to the right cohort.
# Without them "IA1 for CS301" is ambiguous across years.
#
# SQLite source:
#   "semester" INTEGER NOT NULL CHECK(semester >= 1 AND semester <= 8)
#   "batch"    TEXT    NOT NULL
#   CHECK(type IN ('IA1', 'IA2', 'MID_SEM', 'END_SEM'))
#   CHECK(max_marks > 0)
# =============================================================
class Exam(TimestampMixin, Base):
    __tablename__ = "exam"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    type       = Column(String,  nullable=False)   # 'IA1' | 'IA2' | 'MID_SEM' | 'END_SEM'
    subject_id = Column(Integer, ForeignKey("subject.id", ondelete="CASCADE"), nullable=False)
    max_marks  = Column(Integer, nullable=False)
    semester   = Column(Integer, nullable=False)
    batch      = Column(String,  nullable=False)   # e.g. "2023-27"
    date       = Column(Date,    nullable=False)

    __table_args__ = (
        # Replaces: CHECK(type IN ('IA1', 'IA2', 'MID_SEM', 'END_SEM'))
        CheckConstraint(
            "type IN ('IA1', 'IA2', 'MID_SEM', 'END_SEM')",
            name="ck_exam_type",
        ),
        # Replaces: CHECK(max_marks > 0)
        CheckConstraint("max_marks > 0", name="ck_exam_max_marks"),
        # Replaces: CHECK(semester >= 1 AND semester <= 8)
        CheckConstraint("semester >= 1 AND semester <= 8", name="ck_exam_semester"),
    )

    subject = relationship("Subject", back_populates="exams")
    marks   = relationship("Marks",   back_populates="exam", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Exam id={self.id} type={self.type!r} batch={self.batch!r} semester={self.semester}>"


# =============================================================
# MARKS
# =============================================================
# score >= 0    → CheckConstraint (DB level)
# score <= max  → @validates      (Python level)
#
# SQLite source (two triggers replaced):
#   trg_marks_score_insert → BEFORE INSERT check
#   trg_marks_score_update → BEFORE UPDATE check
#
# Both are replaced by one @validates("score") method below,
# which fires on both INSERT and UPDATE automatically.
# =============================================================
class Marks(TimestampMixin, Base):
    __tablename__ = "marks"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("student.id", ondelete="CASCADE"), nullable=False)
    exam_id    = Column(Integer, ForeignKey("exam.id",    ondelete="CASCADE"), nullable=False)
    score      = Column(Integer, nullable=False)

    __table_args__ = (
        # Replaces: CHECK(score >= 0)
        CheckConstraint("score >= 0", name="ck_marks_score_min"),
        # Replaces: UNIQUE(student_id, exam_id)
        UniqueConstraint("student_id", "exam_id", name="uq_marks"),
    )

    student = relationship("Student", back_populates="marks")
    exam    = relationship("Exam",    back_populates="marks")

    @validates("score")
    def validate_score(self, key, score):
        """
        Replaces both SQLite triggers:
          trg_marks_score_insert  (BEFORE INSERT)
          trg_marks_score_update  (BEFORE UPDATE)

        @validates fires on both assignment and update — one method
        covers both cases. The exam relationship must be loaded for
        the upper-bound check to work (it will be when you do things
        the normal SQLAlchemy way).
        """
        if score < 0:
            raise ValueError("score cannot be negative")
        if self.exam is not None and score > self.exam.max_marks:
            raise ValueError(
                f"score {score} exceeds exam max_marks {self.exam.max_marks}"
            )
        return score

    def __repr__(self):
        return f"<Marks id={self.id} student_id={self.student_id} score={self.score}>"


# =============================================================
# ATTENDANCE
# =============================================================
# status: 1 = present, 0 = absent
# No structural changes from SQLite — was already solid.
# Gets batch+section scoping for free via ClassSession.
#
# SQLite source:
#   "status" INTEGER NOT NULL CHECK(status IN (0, 1))
#   UNIQUE(student_id, class_session_id)
# =============================================================
class Attendance(TimestampMixin, Base):
    __tablename__ = "attendance"

    id               = Column(Integer, primary_key=True, autoincrement=True)
    student_id       = Column(Integer, ForeignKey("student.id",      ondelete="CASCADE"), nullable=False)
    class_session_id = Column(Integer, ForeignKey("class_session.id", ondelete="CASCADE"), nullable=False)
    status           = Column(Integer, nullable=False)  # 1 = present, 0 = absent

    __table_args__ = (
        # Replaces: CHECK(status IN (0, 1))
        CheckConstraint("status IN (0, 1)", name="ck_attendance_status"),
        # Replaces: UNIQUE(student_id, class_session_id)
        UniqueConstraint("student_id", "class_session_id", name="uq_attendance"),
    )

    student       = relationship("Student",      back_populates="attendances")
    class_session = relationship("ClassSession", back_populates="attendances")

    def __repr__(self):
        return f"<Attendance id={self.id} student_id={self.student_id} status={self.status}>"
    


# ADDING HOD TABLE
class HOD(TimestampMixin, Base):

    __tablename__ = "hod"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )

    department_id = Column(
        Integer,
        ForeignKey("department.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )

    user = relationship("User", back_populates="hod")

    department = relationship(
        "Department",
        back_populates="hod"
    )