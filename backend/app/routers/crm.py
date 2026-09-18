from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import Contact, Company, Deal, Customer
from app.models.user import User
from app.schemas.contact import ContactCreate, ContactResponse
from app.schemas.company import CompanyCreate, CompanyResponse
from app.schemas.deal import DealCreate, DealResponse, DealStageUpdate
from app.schemas.customer import CustomerCreate, CustomerResponse
from app.auth.dependencies import get_current_active_user

router = APIRouter()


@router.post("/contacts", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    contact_in: ContactCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if contact_in.lead_id:
        result = await db.execute(
            select(__import__("app.models", fromlist=["Lead"]).Lead).where(
                __import__("app.models", fromlist=["Lead"]).Lead.id == contact_in.lead_id,
                __import__("app.models", fromlist=["Lead"]).Lead.org_id == current_user.org_id,
            )
        )
        if result.scalar_one_or_none() is None:
            raise HTTPException(status_code=404, detail="Lead not found")

    contact = Contact(
        **contact_in.model_dump(),
        org_id=current_user.org_id,
    )
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


@router.get("/contacts", response_model=list[ContactResponse])
async def list_contacts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Contact)
        .where(Contact.org_id == current_user.org_id)
        .order_by(Contact.created_at.desc())
    )
    return result.scalars().all()


@router.post("/companies", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    company_in: CompanyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    company = Company(
        **company_in.model_dump(),
        org_id=current_user.org_id,
    )
    db.add(company)
    await db.commit()
    await db.refresh(company)
    return company


@router.get("/companies", response_model=list[CompanyResponse])
async def list_companies(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Company)
        .where(Company.org_id == current_user.org_id)
        .order_by(Company.created_at.desc())
    )
    return result.scalars().all()


@router.post("/deals", response_model=DealResponse, status_code=status.HTTP_201_CREATED)
async def create_deal(
    deal_in: DealCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    company_result = await db.execute(
        select(Company).where(
            Company.id == deal_in.company_id,
            Company.org_id == current_user.org_id,
        )
    )
    if company_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Company not found")

    contact_result = await db.execute(
        select(Contact).where(
            Contact.id == deal_in.contact_id,
            Contact.org_id == current_user.org_id,
        )
    )
    if contact_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Contact not found")

    deal = Deal(
        **deal_in.model_dump(),
        org_id=current_user.org_id,
    )
    db.add(deal)
    await db.commit()
    await db.refresh(deal)
    return deal


@router.get("/deals", response_model=list[DealResponse])
async def list_deals(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Deal)
        .where(Deal.org_id == current_user.org_id)
        .order_by(Deal.created_at.desc())
    )
    return result.scalars().all()


@router.patch("/deals/{deal_id}", response_model=DealResponse)
async def update_deal_stage(
    deal_id: str,
    stage_update: DealStageUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Deal).where(
            Deal.id == deal_id,
            Deal.org_id == current_user.org_id,
        )
    )
    deal = result.scalar_one_or_none()

    if deal is None:
        raise HTTPException(status_code=404, detail="Deal not found")

    deal.stage = stage_update.stage

    if stage_update.probability is not None:
        deal.probability = stage_update.probability

    await db.commit()
    await db.refresh(deal)
    return deal


@router.post("/customers", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer_in: CustomerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    contact_result = await db.execute(
        select(Contact).where(
            Contact.id == customer_in.contact_id,
            Contact.org_id == current_user.org_id,
        )
    )
    if contact_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Contact not found")

    if customer_in.company_id:
        company_result = await db.execute(
            select(Company).where(
                Company.id == customer_in.company_id,
                Company.org_id == current_user.org_id,
            )
        )
        if company_result.scalar_one_or_none() is None:
            raise HTTPException(status_code=404, detail="Company not found")

    customer = Customer(
        **customer_in.model_dump(),
        org_id=current_user.org_id,
    )
    db.add(customer)
    await db.commit()
    await db.refresh(customer)
    return customer
