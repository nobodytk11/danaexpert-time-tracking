"""Reporting endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import User
from app.repositories.report_repository import ReportRepository
from app.schemas.report import Summary
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/summary", response_model=Summary)
def summary(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return ReportService(ReportRepository(db)).summary(user.id)
