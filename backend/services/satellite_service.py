from datetime import datetime, timedelta

import ee


GEE_PROJECT_ID = "kiambu-ardhikodi"


def initialize_earth_engine():
    """Initialize Google Earth Engine."""
    try:
        ee.Initialize(project=GEE_PROJECT_ID)
    except Exception as error:
        raise RuntimeError(
            f"Failed to initialize Google Earth Engine: {error}"
        )


def get_monitoring_area():
    """
    Define the initial WasteGuard monitoring area.

    Prototype area around Nairobi.
    """

    initialize_earth_engine()

    return ee.Geometry.Rectangle(
        [
            36.75,
            -1.35,
            36.90,
            -1.20,
        ]
    )


def mask_clouds(image):
    """
    Basic Sentinel-2 cloud masking using the QA60 band.
    """

    qa = image.select("QA60")

    cloud_bit_mask = 1 << 10
    cirrus_bit_mask = 1 << 11

    mask = (
        qa.bitwiseAnd(cloud_bit_mask)
        .eq(0)
        .And(
            qa.bitwiseAnd(cirrus_bit_mask).eq(0)
        )
    )

    return (
        image
        .updateMask(mask)
        .divide(10000)
        .copyProperties(
            image,
            image.propertyNames()
        )
    )


def get_sentinel_composite(
    start_date,
    end_date,
    region=None,
):
    """
    Fetch a cloud-filtered Sentinel-2 median composite.
    """

    initialize_earth_engine()

    if region is None:
        region = get_monitoring_area()

    collection = (
        ee.ImageCollection(
            "COPERNICUS/S2_SR_HARMONIZED"
        )
        .filterBounds(region)
        .filterDate(start_date, end_date)
        .filter(
            ee.Filter.lt(
                "CLOUDY_PIXEL_PERCENTAGE",
                30
            )
        )
        .map(mask_clouds)
    )

    image_count = collection.size().getInfo()

    if image_count == 0:
        raise RuntimeError(
            f"No Sentinel-2 imagery found between "
            f"{start_date} and {end_date}"
        )

    composite = collection.median().clip(region)

    return {
        "image": composite,
        "region": region,
        "image_count": image_count,
        "start_date": start_date,
        "end_date": end_date,
    }


def get_before_after_images(
    recent_days=30,
    baseline_days=30,
):
    """
    Get two Sentinel-2 composites:

    1. Earlier baseline period.
    2. Recent observation period.
    """

    initialize_earth_engine()

    today = datetime.utcnow().date()

    recent_end = today
    recent_start = (
        recent_end -
        timedelta(days=recent_days)
    )

    baseline_end = recent_start

    baseline_start = (
        baseline_end -
        timedelta(days=baseline_days)
    )

    region = get_monitoring_area()

    before = get_sentinel_composite(
        baseline_start.isoformat(),
        baseline_end.isoformat(),
        region,
    )

    after = get_sentinel_composite(
        recent_start.isoformat(),
        recent_end.isoformat(),
        region,
    )

    return {
        "before": before,
        "after": after,
        "region": region,
    }