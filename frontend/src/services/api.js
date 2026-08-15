const API_BASE_URL = "http://127.0.0.1:5000/api";

export async function getDumpingSites() {
  const response = await fetch(`${API_BASE_URL}/dumping-sites`);

  if (!response.ok) {
    throw new Error("Failed to fetch dumping sites");
  }

  return response.json();
}

export async function getDumpingSitesGeoJSON() {
  const response = await fetch(
    `${API_BASE_URL}/dumping-sites/geojson`
  );

  if (!response.ok) {
    throw new Error("Failed to fetch GeoJSON");
  }

  return response.json();
}