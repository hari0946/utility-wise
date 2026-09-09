import time

from fastapi import BackgroundTasks, Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import desc
from sqlalchemy.orm import Session

from config import settings
from database import Base, engine, get_db
from gmail_service import send_enquiry_notification
from models import Enquiry
from schemas import EnquiryCreate, EnquiryOut

Base.metadata.create_all(bind=engine)

app = FastAPI(title="UtilityWise Enquiry API", version="1.0.0")

origins = (
    ["*"]
    if settings.allowed_origins.strip() == "*"
    else [o.strip() for o in settings.allowed_origins.split(",") if o.strip()]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

_last_submission_by_ip: dict[str, float] = {}


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/enquiries", response_model=EnquiryOut, status_code=201)
def create_enquiry(
    payload: EnquiryCreate,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    # Honeypot: bots tend to fill every field, including ones hidden from real users.
    if payload.website:
        raise HTTPException(status_code=400, detail="Invalid submission")

    client_ip = request.client.host if request.client else "unknown"
    now = time.monotonic()
    last = _last_submission_by_ip.get(client_ip)
    if last is not None and now - last < settings.rate_limit_seconds:
        raise HTTPException(status_code=429, detail="Too many submissions, please try again shortly")
    _last_submission_by_ip[client_ip] = now

    enquiry = Enquiry(
        name=payload.name,
        email=payload.email,
        company=payload.company,
        message=payload.message,
        ip_address=client_ip,
    )
    db.add(enquiry)
    db.commit()
    db.refresh(enquiry)

    background_tasks.add_task(send_enquiry_notification, enquiry)

    return enquiry


def require_admin(x_admin_key: str = Header(default="")):
    if not x_admin_key or x_admin_key != settings.admin_api_key:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/api/enquiries", response_model=list[EnquiryOut], dependencies=[Depends(require_admin)])
def list_enquiries(db: Session = Depends(get_db), limit: int = 100, offset: int = 0):
    limit = max(1, min(limit, 500))
    return (
        db.query(Enquiry)
        .order_by(desc(Enquiry.created_at))
        .offset(offset)
        .limit(limit)
        .all()
    )
