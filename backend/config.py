import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://wasteguard:wasteguard_password@127.0.0.1:5432/wasteguard"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Google Earth Engine project
    GEE_PROJECT_ID = os.getenv(
        "GEE_PROJECT_ID",
        "kiambu-ardhikodi"
    )

    # Detection configuration
    DEFAULT_CHANGE_THRESHOLD = float(
        os.getenv("CHANGE_THRESHOLD", "0.15")
    )

    DEFAULT_MIN_AREA_M2 = float(
        os.getenv("MIN_AREA_M2", "100")
    )