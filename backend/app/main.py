from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.kp_engine import placidus_cusps, planet_positions, prediction_json
from app.models import SavedChart, UserQuery
from app.schemas import ChartRequest, ChartResponse

Base.metadata.create_all(bind=engine)

app = FastAPI(title="KP Astrology API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/charts", response_model=ChartResponse)
def create_chart(payload: ChartRequest, db: Session = Depends(get_db)) -> ChartResponse:
    positions = planet_positions(payload.birth_datetime)
    cusps = placidus_cusps(payload.birth_datetime, payload.latitude, payload.longitude)
    prediction = prediction_json(payload.question, payload.birth_datetime, positions["Moon"], positions, cusps)
    chart_payload = {"planet_positions": positions, "cusps": cusps}

    chart = SavedChart(
        name=payload.name,
        birth_datetime=payload.birth_datetime,
        latitude=str(payload.latitude),
        longitude=str(payload.longitude),
        timezone=payload.timezone,
        chart_payload=chart_payload,
    )
    db.add(chart)
    db.flush()
    db.add(UserQuery(chart_id=chart.id, question=payload.question, context_payload=chart_payload, prediction_payload=prediction))
    db.commit()
    return ChartResponse(chart=chart_payload, prediction=prediction)
