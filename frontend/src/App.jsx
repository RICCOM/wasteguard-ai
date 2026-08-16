import { useEffect, useState } from "react";
import {
  Activity,
  AlertTriangle,
  Bot,
  MapPinned,
  RefreshCw,
  ShieldAlert,
} from "lucide-react";

import DumpingMap from "./components/DumpingMap";

import {
  getDumpingSites,
  runAIDetection,
} from "./services/api";

function StatCard({
  title,
  value,
  description,
  icon,
  variant = "",
}) {
  return (
    <div className={`stat-card ${variant}`}>
      <div className="stat-card-top">
        <div>
          <p className="stat-label">{title}</p>
          <p className="stat-value">{value}</p>
        </div>

        <div className="stat-icon">
          {icon}
        </div>
      </div>

      <p className="stat-description">
        {description}
      </p>
    </div>
  );
}

function getRiskClass(riskLevel) {
  switch (riskLevel) {
    case "CRITICAL":
      return "risk-critical";
    case "HIGH":
      return "risk-high";
    case "MEDIUM":
      return "risk-medium";
    case "LOW":
      return "risk-low";
    default:
      return "";
  }
}

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

  const criticalRisk = sites.filter(
    (site) => site.risk_level === "CRITICAL"
  ).length;

  const highRisk = sites.filter(
    (site) => site.risk_level === "HIGH"
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
          <div className="brand">
            <div className="brand-icon">
              <ShieldAlert size={28} />
            </div>

            <div>
              <h1>WasteGuard AI</h1>
              <p>
                Illegal Dumping Monitoring &
                Intelligence Platform
              </p>
            </div>
          </div>

          <div className="header-actions">
            <div className="system-status">
              <span className="status-dot" />
              System Online
            </div>

            <button
              className="detect-button"
              onClick={handleRunDetection}
              disabled={detecting}
            >
              <RefreshCw
                size={18}
                className={
                  detecting ? "spin-icon" : ""
                }
              />

              {detecting
                ? "Running Detection..."
                : "Run AI Detection"}
            </button>
          </div>
        </div>
      </header>

      <main className="main-content">
        {error && (
          <div className="error-message">
            <AlertTriangle size={20} />
            <div>
              <strong>API Error</strong>
              <p>{error}</p>
            </div>
          </div>
        )}

        {message && (
          <div className="success-message">
            <Activity size={20} />
            {message}
          </div>
        )}

        <section className="stats-grid">
          <StatCard
            title="Detected Sites"
            value={loading ? "..." : sites.length}
            description="Total monitored cases"
            icon={<MapPinned size={24} />}
          />

          <StatCard
            title="Critical Cases"
            value={loading ? "..." : criticalRisk}
            description="Immediate attention required"
            icon={<ShieldAlert size={24} />}
            variant="critical-card"
          />

          <StatCard
            title="High Risk"
            value={loading ? "..." : highRisk}
            description="Requires investigation"
            icon={<AlertTriangle size={24} />}
            variant="high-card"
          />

          <StatCard
            title="Affected Area"
            value={
              loading
                ? "..."
                : `${totalArea.toLocaleString(
                    undefined,
                    {
                      maximumFractionDigits: 0,
                    }
                  )} m²`
            }
            description="Estimated dumping footprint"
            icon={<MapPinned size={24} />}
          />

          <StatCard
            title="AI Confidence"
            value={
              loading
                ? "..."
                : `${Math.round(
                    averageConfidence * 100
                  )}%`
            }
            description="Average detection confidence"
            icon={<Bot size={24} />}
          />
        </section>

        <section className="map-section">
          <div className="map-header">
            <div>
              <div className="section-title-row">
                <MapPinned size={22} />

                <h2>
                  Dumping Site Monitoring Map
                </h2>
              </div>

              <p>
                Satellite and AI-detected potential
                illegal dumping locations
              </p>
            </div>

            <div className="map-count">
              {sites.length} active cases
            </div>
          </div>

          <div className="map-container">
            <DumpingMap />
          </div>
        </section>

        <section className="cases-section">
          <div className="section-header">
            <div>
              <h2>Detection Intelligence</h2>

              <p>
                AI-generated illegal dumping cases
              </p>
            </div>

            <span className="case-count">
              {sites.length} cases
            </span>
          </div>

          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Case ID</th>
                  <th>Risk Level</th>
                  <th>Score</th>
                  <th>Waste Probability</th>
                  <th>Confidence</th>
                  <th>Area</th>
                  <th>Status</th>
                </tr>
              </thead>

              <tbody>
                {sites.map((site) => (
                  <tr key={site.id}>
                    <td>
                      <strong>{site.case_id}</strong>
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

                    <td>{site.risk_score}</td>

                    <td>
                      {Math.round(
                        site.waste_probability * 100
                      )}%
                    </td>

                    <td>
                      {Math.round(
                        site.confidence * 100
                      )}%
                    </td>

                    <td>
                      {Number(
                        site.area_m2 || 0
                      ).toLocaleString()} m²
                    </td>

                    <td>
                      <span className="status-badge">
                        {site.status.replace(
                          "_",
                          " "
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