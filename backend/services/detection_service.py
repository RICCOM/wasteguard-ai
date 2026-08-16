from datetime import datetime

from geoalchemy2.elements import WKTElement

from extensions import db
from models.dumping_site import DumpingSite
from services.change_detection_service import extract_ranked_candidates


def calculate_risk_score(
    waste_probability,
    confidence,
    area_m2,
):
    """
    Calculate a risk score between 0 and 100.
    """

    probability_score = waste_probability * 50
    confidence_score = confidence * 30

    # Larger candidate areas increase risk,
    # capped so area does not dominate the score.
    area_score = min(area_m2 / 500, 20)

    score = (
        probability_score
        + confidence_score
        + area_score
    )

    return min(round(score), 100)


def get_risk_level(score):
    """
    Convert a numerical risk score into a risk category.
    """

    if score >= 85:
        return "CRITICAL"

    if score >= 70:
        return "HIGH"

    if score >= 40:
        return "MEDIUM"

    return "LOW"


def generate_case_id():
    """
    Generate the next WasteGuard Kenya case ID.
    """

    count = DumpingSite.query.count() + 1

    return f"WG-KE-{count:04d}"


def calculate_detection_metrics(candidate):
    """
    Convert satellite change metrics into prototype
    probability and confidence scores.

    These values represent a satellite-derived
    suspicion score, not confirmation of illegal dumping.
    """

    change_score = candidate["change_score"]
    candidate_score = candidate["candidate_score"]

    # Normalize the satellite change score.
    normalized_change = min(change_score / 0.75, 1.0)

    # Combine change intensity and candidate ranking.
    waste_probability = (
        normalized_change * 0.6
        + candidate_score * 0.4
    )

    # Confidence reflects the strength and consistency
    # of the satellite-derived candidate.
    confidence = (
        normalized_change * 0.5
        + candidate_score * 0.5
    )

    # Keep prototype scores within sensible bounds.
    waste_probability = round(
        min(max(waste_probability, 0.0), 0.99),
        2,
    )

    confidence = round(
        min(max(confidence, 0.0), 0.99),
        2,
    )

    return waste_probability, confidence


def run_detection():
    """
    Run real satellite-based candidate detection.

    Workflow:
    Sentinel-2 imagery
        ->
    spectral change detection
        ->
    candidate filtering
        ->
    candidate ranking
        ->
    strongest candidate stored in PostGIS
    """

    candidates = extract_ranked_candidates(
        threshold=0.25,
        min_area_m2=500,
        max_area_m2=10000,
        min_change_score=0.30,
        limit=1,
    )

    if not candidates:
        raise RuntimeError(
            "No suitable satellite change candidates were found."
        )

    candidate = candidates[0]

    latitude = candidate["latitude"]
    longitude = candidate["longitude"]
    area_m2 = round(candidate["area_m2"], 2)

    change_score = candidate["change_score"]
    candidate_score = candidate["candidate_score"]

    waste_probability, confidence = (
        calculate_detection_metrics(candidate)
    )

    risk_score = calculate_risk_score(
        waste_probability,
        confidence,
        area_m2,
    )

    risk_level = get_risk_level(risk_score)

    # PostGIS requires POINT(longitude latitude)
    geometry = WKTElement(
        f"POINT({longitude} {latitude})",
        srid=4326,
    )

    now = datetime.utcnow()

    site = DumpingSite(
        case_id=generate_case_id(),
        latitude=latitude,
        longitude=longitude,
        geometry=geometry,
        area_m2=area_m2,
        waste_probability=waste_probability,
        confidence=confidence,
        risk_score=risk_score,
        risk_level=risk_level,

        # Important: this is a satellite-derived candidate,
        # not a confirmed dumping site.
        status="satellite_candidate",

        ai_summary=(
            "Satellite change analysis identified a suspicious "
            "localized area with "
            f"{change_score * 100:.1f}% normalized spectral change "
            f"and a candidate ranking score of "
            f"{candidate_score * 100:.1f}%. "
            "This location requires further AI classification "
            "or human verification."
        ),

        first_detected=now,
        last_detected=now,
    )

    db.session.add(site)
    db.session.commit()

    return site