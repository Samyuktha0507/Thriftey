from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import models, database
from database import engine

from routers import (
    auth, dashboard, obligations, whatif,
    health_score, gst, email_draft, community, onboarding
)

models.Base.metadata.create_all(bind=engine)

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import date, timedelta
import logging

def check_gst_deadlines():
    db = database.SessionLocal()
    try:
        businesses = db.query(models.Business).all()
        today = date.today()
        reminders = db.query(models.GSTReminder).all()
        for rem in reminders:
            try:
                deadline = date(today.year, today.month, rem.deadline_day)
            except ValueError:
                continue
            if deadline < today:
                m, y = today.month + 1, today.year
                if m > 12: m, y = 1, y + 1
                try:
                    deadline = date(y, m, rem.deadline_day)
                except ValueError:
                    continue
            days_diff = (deadline - today).days
            if 0 <= days_diff <= 7:
                logging.info(f"GST reminder: business_id {rem.business_id} — {rem.form_name} due in {days_diff} days")
    except Exception as e:
        logging.error(f"GST check error: {e}")
    finally:
        db.close()

scheduler = BackgroundScheduler()
scheduler.add_job(check_gst_deadlines, trigger='cron', hour=9)

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(title="Thriftey API", lifespan=lifespan, swagger_ui_parameters={"persistAuthorization": True})

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

from fastapi.exceptions import HTTPException

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if isinstance(exc.detail, dict) and "error" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail, headers=exc.headers)
    return JSONResponse(status_code=exc.status_code, content={"error": "http_error", "message": str(exc.detail)}, headers=exc.headers)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"error": "internal_server_error", "message": str(exc)})

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(obligations.router)
app.include_router(whatif.router)
app.include_router(health_score.router)
app.include_router(gst.router)
app.include_router(email_draft.router)
app.include_router(community.router)
app.include_router(onboarding.router)

@app.get("/")
def root():
    return {"message": "Welcome to Thriftey API"}
