
import { useEffect, useState } from "react";
import DumpingMap from "./components/DumpingMap";
import {
  getDumpingSites,
  runAIDetection,
} from "./services/api";

function App() {
  const [sites, setSites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [detecting, setDetecting] = useState(false);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);

  async function loadSites() {
    try {
      setError(null);

      const result = await getDumpingSites();
      setSites(result.data || []);
    } catch (err) {
      console.error(err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadSites();
  }, []);

  async function handleRunDetection() {
    try {
      setDetecting(true);
      setError(null);
      setMessage(null);

      const result = await runAIDetection();

      setMessage(
        `${result.data.case_id} detected successfully`
      );

      await loadSites();
    } catch (err) {
      console.error(err);
      setError(err.message);
    } finally {
      setDetecting(false);
    }
  }

  const highRisk = sites.filter(
    (site) =>
      site.risk_level === "HIGH" ||
      site.risk_level === "CRITICAL"
  ).length;

  const criticalRisk = sites.filter(
    (site) => site.risk_level === "CRITICAL"
  ).length;

  const totalArea = sites.reduce(
    (total, site) => total + (site.area_m2 || 0),
    0
  );

  const averageConfidence =
    sites.length > 0
      ? sites.reduce(
          (total, site) => total + (site.confidence || 0),
          0
        ) / sites.length
      : 0;

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <div>
            <h1>WasteGuard AI</h1>
            <p>
              Illegal Dumping Monitoring & Intelligence Platform
            </p>
          </div>

          <button
            className="detect-button"
            onClick={handleRunDetection}
            disabled={detecting}
          >
            {detecting
              ? "Running AI Detection..."
              : "Run AI Detection"}
          </button>
        </div>
      </header>

      <main className="main-content">

        {error && (
          <div className="error-message">
            API Error: {error}
          </div>
        )}

        {message && (
          <div className="success-message">
            {message}
          </div>
        )}

        <div className="stats-grid">

          <div className="stat-card">
            <p className="stat-label">
              Total Cases
            </p>
            <p className="stat-value">
              {loading ? "..." : sites.length}
            </p>
          </div>

          <div className="stat-card">
            <p className="stat-label">
              High Risk Cases
            </p>
            <p className="stat-value high-risk">
              {loading ? "..." : highRisk}
            </p>
          </div>

          <div className="stat-card">
            <p className="stat-label">
              Critical Cases
            </p>
            <p className="stat-value critical-risk">
              {loading ? "..." : criticalRisk}
            </p>
          </div>

          <div className="stat-card">
            <p className="stat-label">
              Detected Area
            </p>
            <p className="stat-value">
              {loading
                ? "..."
                : `${totalArea.toFixed(1)} m²`}
            </p>
          </div>

          <div className="stat-card">
            <p className="stat-label">
              Avg AI Confidence
            </p>
            <p className="stat-value">
              {loading
                ? "..."
                : `${Math.round(
                    averageConfidence * 100
                  )}%`}
            </p>
          </div>

        </div>

        <section className="map-section">

          <div className="map-header">
            <div>
              <h2>Dumping Site Monitoring Map</h2>
              <p>
                AI-detected potential illegal dumping
                locations
              </p>
            </div>
          </div>

          <div className="map-container">
            <DumpingMap />
          </div>

        </section>

        <section className="cases-section">

          <div className="section-header">
            <h2>Detected Dumping Sites</h2>
            <span>
              {sites.length} cases
            </span>
          </div>

          <div className="cases-table">

            <div className="table-header">
              <span>Case ID</span>
              <span>Risk</span>
              <span>Score</span>
              <span>Waste Probability</span>
              <span>Confidence</span>
              <span>Area</span>
            </div>

            {sites.map((site) => (
              <div
                className="table-row"
                key={site.id}
              >
                <span>
                  <strong>{site.case_id}</strong>
                </span>

                <span
                  className={`risk-${site.risk_level.toLowerCase()}`}
                >
                  {site.risk_level}
                </span>

                <span>
                  {site.risk_score}
                </span>

                <span>
                  {Math.round(
                    site.waste_probability * 100
                  )}
                  %
                </span>

                <span>
                  {Math.round(
                    site.confidence * 100
                  )}
                  %
                </span>

                <span>
                  {site.area_m2} m²
                </span>
              </div>
            ))}

          </div>

        </section>

      </main>
    </div>
  );
}

export default App;
