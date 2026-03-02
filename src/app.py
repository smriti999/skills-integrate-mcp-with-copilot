"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# Database setup (SQLite) using SQLAlchemy
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, declarative_base
import json

DATABASE_URL = "sqlite:///./activities.db"
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Activity(Base):
    __tablename__ = "activities"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=False)
    schedule = Column(String, nullable=False)
    max_participants = Column(Integer, nullable=False)
    participants_json = Column(Text, default="[]")

    @property
    def participants(self):
        return json.loads(self.participants_json or "[]")

    @participants.setter
    def participants(self, value):
        self.participants_json = json.dumps(value)


# create tables on startup
Base.metadata.create_all(bind=engine)

# seed initial data if empty
def seed_data():
    db = SessionLocal()
    try:
        if db.query(Activity).count() == 0:
            initial = {
                "Chess Club": {
                    "description": "Learn strategies and compete in chess tournaments",
                    "schedule": "Fridays, 3:30 PM - 5:00 PM",
                    "max_participants": 12,
                    "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
                },
                "Programming Class": {
                    "description": "Learn programming fundamentals and build software projects",
                    "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
                    "max_participants": 20,
                    "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
                },
                "Gym Class": {
                    "description": "Physical education and sports activities",
                    "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
                    "max_participants": 30,
                    "participants": ["john@mergington.edu", "olivia@mergington.edu"]
                },
                "Soccer Team": {
                    "description": "Join the school soccer team and compete in matches",
                    "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
                    "max_participants": 22,
                    "participants": ["liam@mergington.edu", "noah@mergington.edu"]
                },
                "Basketball Team": {
                    "description": "Practice and play basketball with the school team",
                    "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
                    "max_participants": 15,
                    "participants": ["ava@mergington.edu", "mia@mergington.edu"]
                },
                "Art Club": {
                    "description": "Explore your creativity through painting and drawing",
                    "schedule": "Thursdays, 3:30 PM - 5:00 PM",
                    "max_participants": 15,
                    "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
                },
                "Drama Club": {
                    "description": "Act, direct, and produce plays and performances",
                    "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
                    "max_participants": 20,
                    "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
                },
                "Math Club": {
                    "description": "Solve challenging problems and participate in math competitions",
                    "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
                    "max_participants": 10,
                    "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
                },
                "Debate Team": {
                    "description": "Develop public speaking and argumentation skills",
                    "schedule": "Fridays, 4:00 PM - 5:30 PM",
                    "max_participants": 12,
                    "participants": ["charlotte@mergington.edu", "henry@mergington.edu"]
                }
            }
            for name, info in initial.items():
                act = Activity(
                    name=name,
                    description=info["description"],
                    schedule=info["schedule"],
                    max_participants=info["max_participants"],
                )
                act.participants = info["participants"]
                db.add(act)
            db.commit()
    finally:
        db.close()

seed_data()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    """Return a mapping of activity names to their details."""
    db = SessionLocal()
    try:
        rows = db.query(Activity).all()
        return {
            a.name: {
                "description": a.description,
                "schedule": a.schedule,
                "max_participants": a.max_participants,
                "participants": a.participants,
            }
            for a in rows
        }
    finally:
        db.close()


@app.get("/activities/{activity_name}")
def get_activity(activity_name: str):
    db = SessionLocal()
    try:
        act = db.query(Activity).filter(Activity.name == activity_name).first()
        if not act:
            raise HTTPException(status_code=404, detail="Activity not found")
        return {
            "name": act.name,
            "description": act.description,
            "schedule": act.schedule,
            "max_participants": act.max_participants,
            "participants": act.participants,
        }
    finally:
        db.close()


@app.post("/activities")
def create_activity(name: str, description: str, schedule: str, max_participants: int):
    db = SessionLocal()
    try:
        existing = db.query(Activity).filter(Activity.name == name).first()
        if existing:
            raise HTTPException(status_code=400, detail="Activity already exists")
        act = Activity(
            name=name,
            description=description,
            schedule=schedule,
            max_participants=max_participants,
        )
        act.participants = []
        db.add(act)
        db.commit()
        return {"message": f"Created activity {name}"}
    finally:
        db.close()


@app.put("/activities/{activity_name}")
def update_activity(activity_name: str,
                    description: str = None,
                    schedule: str = None,
                    max_participants: int = None):
    db = SessionLocal()
    try:
        act = db.query(Activity).filter(Activity.name == activity_name).first()
        if not act:
            raise HTTPException(status_code=404, detail="Activity not found")
        if description is not None:
            act.description = description
        if schedule is not None:
            act.schedule = schedule
        if max_participants is not None:
            act.max_participants = max_participants
        db.commit()
        return {"message": f"Updated activity {activity_name}"}
    finally:
        db.close()


@app.delete("/activities/{activity_name}")
def delete_activity(activity_name: str):
    db = SessionLocal()
    try:
        act = db.query(Activity).filter(Activity.name == activity_name).first()
        if not act:
            raise HTTPException(status_code=404, detail="Activity not found")
        db.delete(act)
        db.commit()
        return {"message": f"Deleted activity {activity_name}"}
    finally:
        db.close()



@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity (database-backed)."""
    db = SessionLocal()
    try:
        act = db.query(Activity).filter(Activity.name == activity_name).first()
        if not act:
            raise HTTPException(status_code=404, detail="Activity not found")
        if email in act.participants:
            raise HTTPException(status_code=400, detail="Student is already signed up")
        if len(act.participants) >= act.max_participants:
            raise HTTPException(status_code=400, detail="Activity is full")
        participants = act.participants
        participants.append(email)
        act.participants = participants
        db.commit()
        return {"message": f"Signed up {email} for {activity_name}"}
    finally:
        db.close()


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity (database-backed)."""
    db = SessionLocal()
    try:
        act = db.query(Activity).filter(Activity.name == activity_name).first()
        if not act:
            raise HTTPException(status_code=404, detail="Activity not found")
        if email not in act.participants:
            raise HTTPException(status_code=400, detail="Student is not signed up for this activity")
        participants = act.participants
        participants.remove(email)
        act.participants = participants
        db.commit()
        return {"message": f"Unregistered {email} from {activity_name}"}
    finally:
        db.close()
