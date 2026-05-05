from sqlalchemy import Column, Integer, String
from app_v2.database import Base



# ================================
# IMPORTS
# ================================

from sqlalchemy import Column, Integer, String, ForeignKey, Date, Time, Enum
from sqlalchemy.orm import relationship
import enum


# ================================
# BASE
# ================================

#Base = declarative_base()


# ================================
# ENUMS
# ================================

class RoleEnum(str, enum.Enum):
    admin = "admin"
    faculty = "faculty"
    student = "student"


class AttendanceStatus(str, enum.Enum):
    present = "present"
    absent = "absent"


# ================================
# USER TABLE (AUTH TABLE)
# ================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)

    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    role = Column(Enum(RoleEnum), nullable=False)

    # One-to-one relationships
    student = relationship("Student", back_populates="user", uselist=False)
    faculty = relationship("Faculty", back_populates="user", uselist=False)
    admin = relationship("Admin", back_populates="user", uselist=False)


# ================================
# STUDENT TABLE
# ================================

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    usn = Column(String, unique=True)
    branch = Column(String)

    user = relationship("User", back_populates="student")

    # Relationships
    enrollments = relationship("Enrollment", back_populates="student")
    attendance = relationship("Attendance", back_populates="student")
    marks = relationship("Mark", back_populates="student")


# ================================
# FACULTY TABLE
# ================================

class Faculty(Base):
    __tablename__ = "faculty"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    uid = Column(String, unique=True)
    dept = Column(String)

    user = relationship("User", back_populates="faculty")

    subjects = relationship("Subject", back_populates="faculty")


# ================================
# ADMIN TABLE
# ================================

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    dept = Column(String)

    user = relationship("User", back_populates="admin")


# ================================
# SUBJECT TABLE
# ================================

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True)
    name = Column(String)

    faculty_id = Column(Integer, ForeignKey("faculty.id"))

    faculty = relationship("Faculty", back_populates="subjects")

    enrollments = relationship("Enrollment", back_populates="subject")
    classes = relationship("Class", back_populates="subject")
    exams = relationship("Exam", back_populates="subject")


# ================================
# ENROLLMENT TABLE (JUNCTION TABLE)
# ================================

class Enrollment(Base):
    __tablename__ = "enrollments"

    # Composite Primary Key
    student_id = Column(Integer, ForeignKey("students.id"), primary_key=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), primary_key=True)

    student = relationship("Student", back_populates="enrollments")
    subject = relationship("Subject", back_populates="enrollments")


# ================================
# CLASS / TIMETABLE TABLE
# ================================

class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True)

    subject_id = Column(Integer, ForeignKey("subjects.id"))
    faculty_id = Column(Integer, ForeignKey("faculty.id"))

    day = Column(String)
    start_time = Column(Time)
    end_time = Column(Time)

    subject = relationship("Subject", back_populates="classes")
    faculty = relationship("Faculty")


# ================================
# ATTENDANCE TABLE
# ================================

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True)

    student_id = Column(Integer, ForeignKey("students.id"))
    class_id = Column(Integer, ForeignKey("classes.id"))

    date = Column(Date)
    status = Column(Enum(AttendanceStatus))

    student = relationship("Student", back_populates="attendance")
    class_ = relationship("Class")  # class is reserved keyword


# ================================
# EXAM TABLE
# ================================

class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True)

    subject_id = Column(Integer, ForeignKey("subjects.id"))
    max_marks = Column(Integer)
    date = Column(Date)

    subject = relationship("Subject", back_populates="exams")
    marks = relationship("Mark", back_populates="exam")


# ================================
# MARKS TABLE
# ================================

class Mark(Base):
    __tablename__ = "marks"

    id = Column(Integer, primary_key=True)

    student_id = Column(Integer, ForeignKey("students.id"))
    exam_id = Column(Integer, ForeignKey("exams.id"))

    marks_obtained = Column(Integer)

    student = relationship("Student", back_populates="marks")
    exam = relationship("Exam", back_populates="marks")