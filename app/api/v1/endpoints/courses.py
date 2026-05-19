from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.crud import course as crud_course
from app.db.session import get_db
from app.models.user import User
from app.schemas.course import (
    CourseCreate,
    CourseList,
    CourseRead,
    CourseUpdate,
)

router = APIRouter()


@router.get(
    "/",
    response_model=CourseList,
    summary="List courses",
)
def list_courses(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    include_inactive: bool = False,
    current_user: User = Depends(get_current_user),
) -> CourseList:
    rows, total = crud_course.get_courses(
        db,
        skip=skip,
        limit=limit,
        include_inactive=include_inactive,
    )
    return CourseList(
        items=[CourseRead.model_validate(r) for r in rows],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post(
    "/",
    response_model=CourseRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create course",
)
def create_course(
    payload: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CourseRead:
    try:
        row = crud_course.create_course(db, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A course with this code already exists.",
        ) from exc
    return CourseRead.model_validate(row)


@router.get(
    "/{course_id}",
    response_model=CourseRead,
    summary="Get course by id",
)
def get_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CourseRead:
    row = crud_course.get_course(db, course_id)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found.",
        )
    return CourseRead.model_validate(row)


@router.put(
    "/{course_id}",
    response_model=CourseRead,
    summary="Replace course",
)
def replace_course(
    course_id: int,
    payload: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CourseRead:
    row = crud_course.get_course(db, course_id)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found.",
        )
    update = CourseUpdate(**payload.model_dump(mode="json"))
    try:
        row = crud_course.update_course(db, row, update)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A course with this code already exists.",
        ) from exc
    return CourseRead.model_validate(row)


@router.patch(
    "/{course_id}",
    response_model=CourseRead,
    summary="Partially update course",
)
def patch_course(
    course_id: int,
    payload: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CourseRead:
    row = crud_course.get_course(db, course_id)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found.",
        )
    if not payload.model_dump(exclude_unset=True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update.",
        )
    try:
        row = crud_course.update_course(db, row, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A course with this code already exists.",
        ) from exc
    return CourseRead.model_validate(row)


@router.delete(
    "/{course_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete course",
)
def remove_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    row = crud_course.get_course(db, course_id)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found.",
        )
    crud_course.delete_course(db, row)
