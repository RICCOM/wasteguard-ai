import { useEffect, useState } from "react";
import DumpingMap from "./components/DumpingMap";
import { getDumpingSites, runAIDetection } from "./services/api";

function App() {
  const [sites, setSites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [detecting, setDetecting] = useState(false);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);

  const [selectedSite, setSelectedSite] = useState(null);

  async function loadSites() {
    try {
      setError(null);
      setLoading(true);

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

      setMessage(`${result.data.case_id} detected successfully`);

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

  function formatDateTime(dateString) {
    if (!dateString) {
      return "Not available";
    }

    const date = new Date(dateString);

    return date.toLocaleString("en-KE", {
      dateStyle: "medium",
      timeStyle: "short",
    });
  }

  function getRiskClass(riskLevel) {
    return `risk-${riskLevel?.toLowerCase()}`;
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <div className="brand">
            <div>
              <h1>WasteGuard AI</h1>

              <p>
                Illegal Dumping Monitoring & Intelligence Platform
              </p>
            </div>
          </div>

          <div className="header-actions">
            <div className="system-status">
              <span className="status-dot"></span>
              System Online
            </div>

            <button
              className="detect-button"
              onClick={handleRunDetection}
              disabled={detecting}
            >
              {detecting
                ? "Running AI Detection..."
                : "↻ Run AI Detection"}
            </button>
          </div>
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
            ✓ {message}
          </div>
        )}

        <section className="stats-grid">

          <div className="stat-card">
            <p className="stat-label">
              Detected Sites
            </p>

            <p className="stat-value">
              {loading ? "..." : sites.length}
            </p>

            <p className="stat-description">
              Total monitored cases
            </p>
          </div>

          <div className="stat-card critical-card">
            <p className="stat-label">
              Critical Cases
            </p>

            <p className="stat-value critical-risk">
              {loading ? "..." : criticalRisk}
            </p>

            <p className="stat-description">
              Immediate attention required
            </p>
          </div>

          <div className="stat-card high-card">
            <p className="stat-label">
              High Risk
            </p>

            <p className="stat-value high-risk">
              {loading ? "..." : highRisk - criticalRisk}
            </p>

            <p className="stat-description">
              Requires investigation
            </p>
          </div>

          <div className="stat-card">
            <p className="stat-label">
              Affected Area
            </p>

            <p className="stat-value">
              {loading
                ? "..."
                : `${totalArea.toLocaleString(
                    undefined,
                    {
                      maximumFractionDigits: 1,
                    }
                  )} m²`}
            </p>

            <p className="stat-description">
              Estimated dumping footprint
            </p>
          </div>

          <div className="stat-card">
            <p className="stat-label">
              AI Confidence
            </p>

            <p className="stat-value">
              {loading
                ? "..."
                : `${Math.round(
                    averageConfidence * 100
                  )}%`}
            </p>

            <p className="stat-description">
              Average detection confidence
            </p>
          </div>

        </section>

        <section className="map-section">

          <div className="map-header">
            <div>
              <h2>⌖ Dumping Site Monitoring Map</h2>

              <p>
                Satellite and AI-detected potential illegal dumping locations
              </p>
            </div>

            <span className="case-badge">
              {sites.length} active cases
            </span>
          </div>

          <div className="map-container">
            <DumpingMap
              sites={sites}
              selectedSite={selectedSite}
              setSelectedSite={setSelectedSite}
            />
          </div>

        </section>

        {selectedSite && (
          <section className="selected-site-section">

            <div className="selected-site-header">
              <div>
                <h2>
                  Selected Case: {selectedSite.case_id}
                </h2>

                <p>
                  Detailed detection information
                </p>
              </div>

              <button
                className="close-button"
                onClick={() => setSelectedSite(null)}
              >
                Close
              </button>
            </div>

            <div className="site-details-grid">

              <div className="site-detail">
                <span>Risk Level</span>

                <strong
                  className={getRiskClass(
                    selectedSite.risk_level
                  )}
                >
                  {selectedSite.risk_level}
                </strong>
              </div>

              <div className="site-detail">
                <span>Risk Score</span>

                <strong>
                  {selectedSite.risk_score}
                </strong>
              </div>

              <div className="site-detail">
                <span>Waste Probability</span>

                <strong>
                  {Math.round(
                    selectedSite.waste_probability * 100
                  )}
                  %
                </strong>
              </div>

              <div className="site-detail">
                <span>AI Confidence</span>

                <strong>
                  {Math.round(
                    selectedSite.confidence * 100
                  )}
                  %
                </strong>
              </div>

              <div className="site-detail">
                <span>Area</span>

                <strong>
                  {selectedSite.area_m2} m²
                </strong>
              </div>

              <div className="site-detail">
                <span>Detected Date & Time</span>

                <strong>
                  {formatDateTime(
                    selectedSite.first_detected ||
                    selectedSite.created_at
                  )}
                </strong>
              </div>

            </div>

            <div className="ai-summary">
              <h3>AI Analysis</h3>

              <p>
                {selectedSite.ai_summary}
              </p>
            </div>

          </section>
        )}

        <section className="cases-section">

          <div className="section-header">
            <div>
              <h2>Detection Intelligence</h2>

              <p>
                AI-generated illegal dumping cases
              </p>
            </div>

            <span className="case-badge">
              {sites.length} cases
            </span>
          </div>

          <div className="table-wrapper">

            <table className="cases-table">

              <thead>
                <tr>
                  <th>Case ID</th>
                  <th>Risk Level</th>
                  <th>Score</th>
                  <th>Waste Probability</th>
                  <th>Confidence</th>
                  <th>Area</th>
                  <th>Detected Date & Time</th>
                  <th>Status</th>
                </tr>
              </thead>

              <tbody>

                {sites.map((site) => (
                  <tr
                    key={site.id}
                    onClick={() => setSelectedSite(site)}
                    className={
                      selectedSite?.id === site.id
                        ? "selected-row"
                        : ""
                    }
                  >
                    <td>
                      <strong>
                        {site.case_id}
                      </strong>
                    </td>

                    <td>
                      <span
                        className={`risk-badge ${getRiskClass(
                          site.risk_level
                        )}`}
                      >
                        {site.risk_level}
                      </span>
                    </td>

                    <td>
                      {site.risk_score}
                    </td>

                    <td>
                      {Math.round(
                        site.waste_probability * 100
                      )}
                      %
                    </td>

                    <td>
                      {Math.round(
                        site.confidence * 100
                      )}
                      %
                    </td>

                    <td>
                      {site.area_m2} m²
                    </td>

                    <td className="date-time">
                      {formatDateTime(
                        site.first_detected ||
                        site.created_at
                      )}
                    </td>

                    <td>
                      <span className="status-badge">
                        {site.status
                          ?.replace("_", " ")
                          .replace(
                            /\b\w/g,
                            (char) =>
                              char.toUpperCase()
                          )}
                      </span>
                    </td>

                  </tr>
                ))}

              </tbody>

            </table>

          </div>

        </section>

      </main>
    </div>
  );
}

export default App;