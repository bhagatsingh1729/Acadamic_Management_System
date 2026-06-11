from sqlalchemy.orm import Session
from app.models.models import User, Faculty, Department
from app.schemas.fundamental_schemas.faculty_schema import FacultyCreate, FacultyUpdate
from app.core.security import hash_password

# =============================================================
# CREATE FACULTY (STAGING ONLY)
# =============================================================
def create_faculty(db: Session, faculty_data: FacultyCreate):
    # 1. Validation Logic (Raises ValueError for Service Translation)
    existing_email = db.query(User).filter(User.email == faculty_data.email).first()
    if existing_email:
        raise ValueError("email already exists")

    existing_employee = (
        db.query(Faculty)
        .filter(Faculty.employee_id == faculty_data.employee_id.upper())
        .first()
    )
    if existing_employee:
        raise ValueError("employee_id already exists")

    if faculty_data.dept_id is not None:
        department = db.query(Department).filter(Department.id == faculty_data.dept_id).first()
        if not department:
            raise ValueError("department not found")

    # 2. Stage User Entity
    new_user = User(
        name=faculty_data.name,
        email=faculty_data.email,
        password=hash_password(faculty_data.password),
        role="faculty",
        phone_no=faculty_data.phone_no,
        dob=faculty_data.dob,
        address=faculty_data.address
    )
    db.add(new_user)
    db.flush() 

    # 3. Stage Faculty Entity
    new_faculty = Faculty(
        user_id=new_user.id,
        employee_id=faculty_data.employee_id.upper(),
        dept_id=faculty_data.dept_id
    )
    db.add(new_faculty)
    db.flush() 

    return new_faculty


# =============================================================
# READ OPERATIONS
# =============================================================
def get_all_faculty(db: Session):
    return db.query(Faculty).limit(50).all()


def get_faculty_by_id(db: Session, faculty_id: int):
    return db.query(Faculty).filter(Faculty.id == faculty_id).first()


def get_faculty_by_emp_id(db: Session, emp_id: str):
    return db.query(Faculty).filter(Faculty.employee_id == emp_id.upper()).first()


# =============================================================
# UPDATE FACULTY (STAGING ONLY)
# =============================================================
def update_faculty(db: Session, faculty_id: int, faculty_data: FacultyUpdate):
    faculty = get_faculty_by_id(db, faculty_id)
    if not faculty:
        raise ValueError("faculty not found")

    if faculty_data.dept_id is not None:
        department = db.query(Department).filter(Department.id == faculty_data.dept_id).first()
        if not department:
            raise ValueError("department not found")
        faculty.dept_id = faculty_data.dept_id

    # Update User Info Cascade
    user = faculty.user
    if faculty_data.name is not None:
        user.name = faculty_data.name
    if faculty_data.phone_no is not None:
        user.phone_no = faculty_data.phone_no
    if faculty_data.dob is not None:
        user.dob = faculty_data.dob
    if faculty_data.address is not None:
        user.address = faculty_data.address

    db.flush()
    return faculty


# =============================================================
# DELETE FACULTY (STAGING ONLY)
# =============================================================
def delete_faculty(db: Session, faculty_id: int):
    faculty = get_faculty_by_id(db, faculty_id)
    if not faculty:
        raise ValueError("faculty not found")

    user = faculty.user
    db.delete(faculty)
    if user:
        db.delete(user)
        
    db.flush()
    return True