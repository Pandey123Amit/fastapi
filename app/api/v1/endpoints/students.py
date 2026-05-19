from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.crud import student as crud_student
from app.db.session import get_db
from app.models.user import User
from app.schemas.student import StudentCreate, StudentList, StudentRead, StudentUpdate

router = APIRouter()


@router.get(
    "/",
    response_model=StudentList,
    summary="List students",
)
def list_students(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    include_inactive: bool = False,
    current_user: User = Depends(get_current_user),
) -> StudentList:
    rows, total = crud_student.get_students(
        db,
        skip=skip,
        limit=limit,
        include_inactive=include_inactive,
    )
    return StudentList(
        items=[StudentRead.model_validate(r) for r in rows],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post(
    "/",
    response_model=StudentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create student",
)
def create_student(
    payload: StudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StudentRead:
    try:
        row = crud_student.create_student(db, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A student with this email already exists.",
        ) from exc
    return StudentRead.model_validate(row)


@router.get(
    "/{student_id}",
    response_model=StudentRead,
    summary="Get student by id",
)
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StudentRead:
    row = crud_student.get_student(db, student_id)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found.",
        )
    return StudentRead.model_validate(row)


@router.put(
    "/{student_id}",
    response_model=StudentRead,
    summary="Replace student",
)
def replace_student(
    student_id: int,
    payload: StudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StudentRead:
    row = crud_student.get_student(db, student_id)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found.",
        )
    update = StudentUpdate(**payload.model_dump())
    try:
        row = crud_student.update_student(db, row, update)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A student with this email already exists.",
        ) from exc
    return StudentRead.model_validate(row)


@router.patch(
    "/{student_id}",
    response_model=StudentRead,
    summary="Partially update student",
)
def patch_student(
    student_id: int,
    payload: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StudentRead:
    row = crud_student.get_student(db, student_id)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found.",
        )
    if not payload.model_dump(exclude_unset=True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update.",
        )
    try:
        row = crud_student.update_student(db, row, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A student with this email already exists.",
        ) from exc
    return StudentRead.model_validate(row)


@router.delete(
    "/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete student",
)
def remove_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    row = crud_student.get_student(db, student_id)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found.",
        )
    crud_student.delete_student(db, row)
