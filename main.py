from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from schema import LabTemplateRead, LabTemplateCreate
from db import get_async_session, create_all_tables
from models import LabTemplate
import contextlib


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Creating tables...")
    await create_all_tables()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/templates")#, response_model=LabTemplateRead)
def create_template(template: LabTemplateCreate, db: AsyncSession = Depends(get_async_session)):
    new_template = LabTemplate(**template.dict())
    print(new_template)
    return {"hello": "world"}