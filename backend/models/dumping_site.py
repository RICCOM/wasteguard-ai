# from datetime import datetime

# from geoalchemy2 import Geometry
# from sqlalchemy import String, Float, Integer, DateTime, Text

# from extensions import db


# class DumpingSite(db.Model):
#     __tablename__ = "dumping_sites"

#     id = db.Column(Integer, primary_key=True)

#     case_id = db.Column(
#         String(50),
#         unique=True,
#         nullable=False,
#         index=True
#     )

#     latitude = db.Column(
#         Float,
#         nullable=False
#     )

#     longitude = db.Column(
#         Float,
#         nullable=False
#     )

#     geometry = db.Column(
#         Geometry(
#             geometry_type="POINT",
#             srid=4326
#         ),
#         nullable=False
#     )

#     area_m2 = db.Column(
#         Float,
#         nullable=True
#     )

#     waste_probability = db.Column(
#         Float,
#         nullable=True
#     )

#     confidence = db.Column(
#         Float,
#         nullable=True
#     )

#     risk_score = db.Column(
#         Integer,
#         nullable=True
#     )

#     risk_level = db.Column(
#         String(20),
#         nullable=True
#     )

#     status = db.Column(
#         String(30),
#         nullable=False,
#         default="DETECTED"
#     )

#     ai_summary = db.Column(
#         Text,
#         nullable=True
#     )

#     first_detected = db.Column(
#         DateTime,
#         nullable=True
#     )

#     last_detected = db.Column(
#         DateTime,
#         nullable=True
#     )

#     created_at = db.Column(
#         DateTime,
#         default=datetime.utcnow,
#         nullable=False
#     )

#     updated_at = db.Column(
#         DateTime,
#         default=datetime.utcnow,
#         onupdate=datetime.utcnow,
#         nullable=False
#     )

#     def to_dict(self):
#         return {
#             "id": self.id,
#             "case_id": self.case_id,
#             "latitude": self.latitude,
#             "longitude": self.longitude,
#             "area_m2": self.area_m2,
#             "waste_probability": self.waste_probability,
#             "confidence": self.confidence,
#             "risk_score": self.risk_score,
#             "risk_level": self.risk_level,
#             "status": self.status,
#             "ai_summary": self.ai_summary,
#             "first_detected": (
#                 self.first_detected.isoformat()
#                 if self.first_detected
#                 else None
#             ),
#             "last_detected": (
#                 self.last_detected.isoformat()
#                 if self.last_detected
#                 else None
#             ),
#             "created_at": self.created_at.isoformat(),
#             "updated_at": self.updated_at.isoformat(),
#         }
from datetime import datetime

from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape

from extensions import db


class DumpingSite(db.Model):
    __tablename__ = "dumping_sites"

    id = db.Column(db.Integer, primary_key=True)

    case_id = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    latitude = db.Column(
        db.Float,
        nullable=False
    )

    longitude = db.Column(
        db.Float,
        nullable=False
    )

    geometry = db.Column(
        Geometry("POINT", srid=4326),
        nullable=False
    )

    area_m2 = db.Column(db.Float)

    waste_probability = db.Column(db.Float)

    confidence = db.Column(db.Float)

    risk_score = db.Column(db.Integer)

    risk_level = db.Column(db.String(20))

    status = db.Column(
        db.String(30),
        nullable=False
    )

    ai_summary = db.Column(db.Text)

    first_detected = db.Column(db.DateTime)

    last_detected = db.Column(db.DateTime)

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "case_id": self.case_id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "area_m2": self.area_m2,
            "waste_probability": self.waste_probability,
            "confidence": self.confidence,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "status": self.status,
            "ai_summary": self.ai_summary,
            "first_detected": (
                self.first_detected.isoformat()
                if self.first_detected else None
            ),
            "last_detected": (
                self.last_detected.isoformat()
                if self.last_detected else None
            ),
            "created_at": (
                self.created_at.isoformat()
                if self.created_at else None
            ),
            "updated_at": (
                self.updated_at.isoformat()
                if self.updated_at else None
            ),
            "geometry": self.geometry_geojson()
        }

    def geometry_geojson(self):
        if not self.geometry:
            return None

        point = to_shape(self.geometry)

        return {
            "type": "Point",
            "coordinates": [
                point.x,
                point.y
            ]
        }