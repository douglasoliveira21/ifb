"""API pública de transparência institucional do IFB."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.transparency import (
    GovernanceMember,
    InstitutionalContract,
    InstitutionalDocument,
    InstitutionalExpense,
    InstitutionalRevenue,
)

router = APIRouter(prefix="/transparency", tags=["Transparência"])


@router.get("/revenues")
async def list_revenues(
    year: int | None = Query(None),
    category: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """Lista receitas institucionais publicadas."""
    query = select(InstitutionalRevenue).where(InstitutionalRevenue.public == True)
    if year:
        query = query.where(func.extract("year", InstitutionalRevenue.date) == year)
    if category:
        query = query.where(InstitutionalRevenue.category == category)
    query = query.order_by(desc(InstitutionalRevenue.date))

    result = await db.execute(query.offset((page - 1) * limit).limit(limit))
    revenues = result.scalars().all()

    return {
        "data": [
            {"id": r.id, "date": str(r.date), "category": r.category,
             "description": r.description, "gross_amount": float(r.gross_amount),
             "net_amount": float(r.net_amount), "source_type": r.source_type}
            for r in revenues
        ],
        "pagination": {"page": page, "limit": limit},
    }


@router.get("/expenses")
async def list_expenses(
    year: int | None = Query(None),
    category: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """Lista despesas institucionais publicadas."""
    query = select(InstitutionalExpense).where(InstitutionalExpense.public == True)
    if year:
        query = query.where(func.extract("year", InstitutionalExpense.date) == year)
    if category:
        query = query.where(InstitutionalExpense.category == category)
    query = query.order_by(desc(InstitutionalExpense.date))

    result = await db.execute(query.offset((page - 1) * limit).limit(limit))
    expenses = result.scalars().all()

    return {
        "data": [
            {"id": e.id, "date": str(e.date), "category": e.category,
             "supplier": e.supplier_name, "description": e.description,
             "gross_amount": float(e.gross_amount), "net_amount": float(e.net_amount)}
            for e in expenses
        ],
        "pagination": {"page": page, "limit": limit},
    }


@router.get("/contracts")
async def list_contracts(db: AsyncSession = Depends(get_db)):
    """Lista contratos institucionais."""
    result = await db.execute(
        select(InstitutionalContract).where(InstitutionalContract.public == True)
        .order_by(desc(InstitutionalContract.start_date))
    )
    contracts = result.scalars().all()
    return {
        "data": [
            {"id": c.id, "title": c.title, "supplier": c.supplier_name,
             "status": c.status, "total_value": float(c.total_value) if c.total_value else None,
             "start_date": str(c.start_date) if c.start_date else None,
             "end_date": str(c.end_date) if c.end_date else None}
            for c in contracts
        ],
    }


@router.get("/documents")
async def list_documents(
    category: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Lista documentos institucionais públicos."""
    query = select(InstitutionalDocument).where(InstitutionalDocument.public == True)
    if category:
        query = query.where(InstitutionalDocument.category == category)
    query = query.order_by(desc(InstitutionalDocument.published_at))

    result = await db.execute(query)
    docs = result.scalars().all()

    return {
        "data": [
            {"id": d.id, "category": d.category, "title": d.title,
             "description": d.description, "file_url": d.file_url,
             "version": d.version,
             "published_at": d.published_at.isoformat() if d.published_at else None}
            for d in docs
        ],
    }


@router.get("/governance")
async def list_governance(db: AsyncSession = Depends(get_db)):
    """Lista membros de governança."""
    result = await db.execute(
        select(GovernanceMember).where(
            GovernanceMember.active == True, GovernanceMember.public == True
        )
    )
    members = result.scalars().all()
    return {
        "data": [
            {"name": m.name, "role": m.role, "body": m.body, "bio": m.bio,
             "started_at": str(m.started_at) if m.started_at else None}
            for m in members
        ],
    }


@router.get("/summary")
async def get_transparency_summary(db: AsyncSession = Depends(get_db)):
    """Resumo financeiro do IFB."""
    total_revenue = (await db.execute(
        select(func.sum(InstitutionalRevenue.net_amount))
        .where(InstitutionalRevenue.public == True)
    )).scalar_one_or_none() or 0

    total_expense = (await db.execute(
        select(func.sum(InstitutionalExpense.net_amount))
        .where(InstitutionalExpense.public == True)
    )).scalar_one_or_none() or 0

    active_contracts = (await db.execute(
        select(func.count(InstitutionalContract.id))
        .where(InstitutionalContract.status == "active")
    )).scalar_one()

    return {
        "total_revenue": float(total_revenue),
        "total_expenses": float(total_expense),
        "balance": float(total_revenue - total_expense),
        "active_contracts": active_contracts,
        "message": "Todos os valores publicados são reais e auditáveis.",
    }
