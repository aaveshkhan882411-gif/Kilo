from fastapi import APIRouter
from app.schemas.contact import ContactCreate, ContactResponse
from app.schemas.company import CompanyCreate, CompanyResponse
from app.schemas.deal import DealCreate, DealResponse, DealStageUpdate
from app.schemas.customer import CustomerCreate, CustomerResponse
from app.auth.dependencies import get_current_active_user

router = APIRouter()


@router.post("/contacts", response_model=ContactResponse, status_code=201)
async def create_contact(contact_in: ContactCreate, current_user: User = Depends(get_current_active_user)):
    pass


@router.get("/contacts", response_model=list[ContactResponse])
async def list_contacts(current_user: User = Depends(get_current_active_user)):
    pass


@router.post("/companies", response_model=CompanyResponse, status_code=201)
async def create_company(company_in: CompanyCreate, current_user: User = Depends(get_current_active_user)):
    pass


@router.get("/companies", response_model=list[CompanyResponse])
async def list_companies(current_user: User = Depends(get_current_active_user)):
    pass


@router.post("/deals", response_model=DealResponse, status_code=201)
async def create_deal(deal_in: DealCreate, current_user: User = Depends(get_current_active_user)):
    pass


@router.get("/deals", response_model=list[DealResponse])
async def list_deals(current_user: User = Depends(get_current_active_user)):
    pass


@router.patch("/deals/{deal_id}")
async def update_deal_stage(deal_id: str, stage_update: DealStageUpdate, current_user: User = Depends(get_current_active_user)):
    pass


@router.post("/customers", response_model=CustomerResponse, status_code=201)
async def create_customer(customer_in: CustomerCreate, current_user: User = Depends(get_current_active_user)):
    pass
