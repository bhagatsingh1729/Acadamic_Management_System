from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.core.dependencies import (
    require_roles, 
    get_current_faculty, 
    get_current_student, 
    get_current_admin
)
from app.models.models import User, Marks, Faculty, Student, Admin
from app.schemas.response_schemas.API_Response import ApiResponse
from app.schemas.services_schemas.marks_schemas.marks_schemas import (
    AssignMarksRequest,
    AssignMarksResponse,
)
from app.services.marks_services.marks_services import (
    assign_marks_service,
    update_marks_service,
    get_marks_of_exam_service,
    get_student_marks_service,
    delete_marks_service
)

router = APIRouter(prefix="/marks", tags=['Marks'])

# =========================================================================
# 1. ASSIGN MARKS (Faculty Only)
# =========================================================================
@router.post("/assign", response_model=ApiResponse[AssignMarksResponse], status_code=status.HTTP_201_CREATED)
def assign_marks_route(
    data: AssignMarksRequest,
    db: Session = Depends(get_db),
    faculty: Faculty = Depends(get_current_faculty)
):
    result = assign_marks_service(db=db, data=data, faculty_id=faculty.id)
    return ApiResponse(success=True, message="Marks assigned successfully", data=result)


# =========================================================================
# 2. GET MY MARKS (Student Only)
# =========================================================================
@router.get("/me", response_model=ApiResponse[List[AssignMarksResponse]])
def students_get_marks_route(
    db: Session = Depends(get_db),
    student: Student = Depends(get_current_student)
):
    db_marks = db.query(Marks).filter(Marks.student_id == student.id).all()
    if not db_marks:
        raise HTTPException(status_code=404, detail='No marks records found for your academic profile.')
    
    formatted_data = [
        AssignMarksResponse(
            id=row.id,
            usn=student.usn,
            exam_id=row.exam_id,
            subject_code=row.exam.subject.code,
            score=row.score
        ) for row in db_marks
    ]
    return ApiResponse(success=True, data=formatted_data)


# =========================================================================
# 3. GET MARKS OF AN EXAM (Faculty / Admin / Super Admin)
# =========================================================================
@router.get("/exam/{exam_id}", response_model=ApiResponse[List[AssignMarksResponse]])
def get_all_exam_marks_route(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("faculty", "admin", "super_admin"))
):
    # If Admin, check branch isolation boundary constraints
    if current_user.role == "admin":
        admin = get_current_admin(current_user=current_user, db=db)
        # Verify the exam's subject belongs to admin's branch via a localized check if necessary
        
    results = get_marks_of_exam_service(db=db, exam_id=exam_id)
    return ApiResponse(success=True, data=results)


# =========================================================================
# 4. GET STUDENT MARKS BY USN (Multi-Role Authorized)
# =========================================================================
@router.get("/students/{usn}", response_model=ApiResponse[List[AssignMarksResponse]])
def get_student_marks_route(
    usn: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("faculty", "admin", "super_admin", "student"))
):
    usn_upper = usn.upper()

    # Data Isolation Boundary Logic Checks
    if current_user.role == "student":
        student = get_current_student(current_user=current_user, db=db)
        if student.usn.upper() != usn_upper:
            raise HTTPException(status_code=403, detail='Access Denied. You can only view your own marks.')
            
    elif current_user.role == "admin":
        admin = get_current_admin(current_user=current_user, db=db)
        target_student = db.query(Student).filter(Student.usn == usn_upper).first()
        if not target_student or target_student.branch_id != admin.branch_id:
            raise HTTPException(status_code=403, detail='Access Denied. Target student profile falls outside your branch context domain.')

    results = get_student_marks_service(db=db, student_usn=usn_upper)
    return ApiResponse(success=True, data=results)


# =========================================================================
# 5. UPDATE STUDENT MARKS (Faculty Only)
# =========================================================================
@router.patch("/student/{usn}/exam/{exam_id}", response_model=ApiResponse[AssignMarksResponse])
def update_student_marks_route(
    usn: str,
    exam_id: int,
    score: int,
    db: Session = Depends(get_db),
    faculty: Faculty = Depends(get_current_faculty)
):
    result = update_marks_service(db=db, usn=usn, exam_id=exam_id, score=score, faculty_id=faculty.id)
    return ApiResponse(success=True, message="Marks record updated successfully", data=result)


# =========================================================================
# 6. DELETE MARKS RECORD (Faculty Only)
# =========================================================================
@router.delete("/delete/{marks_id}", response_model=ApiResponse[None])
def delete_marks_route(
    marks_id: int,
    db: Session = Depends(get_db),
    faculty: Faculty = Depends(get_current_faculty)
):
    delete_marks_service(db=db, marks_id=marks_id, faculty_id=faculty.id)
    return ApiResponse(success=True, message="Marks record deleted successfully.")