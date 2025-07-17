from sqlalchemy import or_
from fastapi.exceptions import HTTPException, RequestValidationError
from starlette.responses import JSONResponse
from typing import List
import httpx
from fastapi import FastAPI, Depends, status, Request, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from schema import LabTemplateRead, LabTemplateCreate

from db import get_async_session, create_all_tables
from models import LabTemplate
from config import Config
import contextlib


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Creating tables...")
    await create_all_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=-1,  # change to 3600 -> cache preflight for 1 hour
)


@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    details = []

    for err in errors:
        loc = ".".join([str(loc_part) for loc_part in err.get("loc", [])])
        msg = err.get("msg", "invalid input")
        details.append(f"{loc}: {msg}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": "Validation failed", "details": details},
    )


async def verify_token(authorization: str = Header(...)):
    LARAVEL_AUTH_PATH = f"{Config.CONFIRMATION_URL}/staff/profile"
    headers = {"Authorization": authorization}
    async with httpx.AsyncClient() as client:
        response = await client.get(LARAVEL_AUTH_PATH, headers=headers)

        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid token")
        try:
            return response.json()
        except Exception:
            raise HTTPException(status_code=500, detail="Failed to parse JSON")


async def get_single_template(
    name: str, facility_id: int, db: AsyncSession, user=Depends(verify_token)
):
    try:
        query = select(LabTemplate).where(
            LabTemplate.name.ilike(f"%{name}%"), LabTemplate.facility_id == facility_id
        )
        result = await db.execute(query)
        template = result.scalar_one_or_none()
        return template
    except Exception as e:
        print(e)
        return None


@app.get(
    "/templates", response_model=List[LabTemplateRead], status_code=status.HTTP_200_OK
)
async def get_templates(
    name: List[str] = Query(..., description="List of template names"),
    facility_id: int = Query(..., description="Facility ID"),
    db: AsyncSession = Depends(get_async_session),
    user=Depends(verify_token),
):
    templates = await get_templates_by_names(name, facility_id, db)
    if not templates:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No templates found for names {name} in facility ID {facility_id}",
        )
    return templates


@app.get(
    "/all-templates",
    response_model=List[LabTemplateRead],
    status_code=status.HTTP_200_OK,
)
async def all_facility_lab_templates(
    facility_id: int = Query(..., description="Facility ID"),
    db: AsyncSession = Depends(get_async_session),
    user=Depends(verify_token),
):
    try:
        query = select(LabTemplate)
        results = await db.execute(query)
        return results.scalars().all()
    except Exception as e:
        print(e)
        return []


async def get_templates_by_names(names: List[str], facility_id: int, db: AsyncSession):
    try:
        filters = [LabTemplate.name.ilike(f"%{n}%") for n in names]
        query = select(LabTemplate).where(
            or_(*filters), LabTemplate.facility_id == facility_id
        )
        result = await db.execute(query)
        return result.scalars().all()
    except Exception as e:
        print(f"Error: {e}")
        return []


@app.post(
    "/templates", response_model=LabTemplateRead, status_code=status.HTTP_201_CREATED
)
async def create_template(
    template: LabTemplateCreate,
    db: AsyncSession = Depends(get_async_session),
    user=Depends(verify_token),
):
    existing_template = await get_single_template(
        template.name, template.facility_id, db
    )
    print(existing_template)
    if existing_template is None:
        new_template = LabTemplate(**template.dict())
        db.add(new_template)
        await db.commit()
        await db.refresh(new_template)
        return new_template
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT, detail="Template already exists"
    )


@app.get("/templates", response_model=LabTemplateRead, status_code=status.HTTP_200_OK)
async def get_template(
    name: str = Query(..., description="Template name"),
    facility_id: int = Query(..., description="Facility ID"),
    db: AsyncSession = Depends(get_async_session),
    user=Depends(verify_token),
):
    template = await get_single_template(name, facility_id, db)
    if template is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template with name '{name}' and facility_id '{facility_id}' not found",
        )
    return template


@app.put("/templates/{id}", response_model=LabTemplateRead)
async def update_template(
    id: int,
    updated_data: LabTemplateCreate,
    db: AsyncSession = Depends(get_async_session),
    user=Depends(verify_token),
):
    template = await db.get(LabTemplate, id)

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    for key, value in updated_data.dict().items():
        setattr(template, key, value)

    await db.commit()
    await db.refresh(template)
    return template


@app.get("/verify-token")
async def get_secure_data(user=Depends(verify_token)):
    return {"message": "valid token from laravel"}
