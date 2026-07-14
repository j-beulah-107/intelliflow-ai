import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";

function Dashboard() {
  const navigate = useNavigate();

  const [stats, setStats] = useState({
    total_files: 0,
    pdf_files: 0,
    csv_files: 0,
    image_files: 0,
  });

  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");

  useEffect(() => {
    const fetchStats = async () => {
      const token = localStorage.getItem("access_token");

      if (!token) {
        navigate("/");
        return;
      }

      try {
        const response = await axios.get(
          "http://127.0.0.1:8000/dashboard/stats",
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        setStats(response.data);
      } catch (error) {
        setMessage(
          error.response?.data?.detail ||
            "Unable to load dashboard."
        );

        if (error.response?.status === 401) {
          localStorage.removeItem("access_token");
          navigate("/");
        }
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    navigate("/");
  };

  return (
    <main className="dashboard-page">
      <header className="dashboard-header">
        <div>
          <div className="brand">IntelliFlow AI</div>
          <h1>Dashboard</h1>
          <p>Manage and analyse your uploaded files.</p>
        </div>

        <button
          className="secondary-button"
          onClick={handleLogout}
        >
          Log out
        </button>
      </header>

      {loading && <p>Loading dashboard...</p>}

      {message && (
        <p className="error-message">{message}</p>
      )}

      {!loading && !message && (
        <>
          <section className="stats-grid">
            <article className="stat-card">
              <span>Total files</span>
              <strong>{stats.total_files}</strong>
            </article>

            <article className="stat-card">
              <span>PDF files</span>
              <strong>{stats.pdf_files}</strong>
            </article>

            <article className="stat-card">
              <span>CSV files</span>
              <strong>{stats.csv_files}</strong>
            </article>

            <article className="stat-card">
              <span>Images</span>
              <strong>{stats.image_files}</strong>
            </article>
          </section>

          <section className="action-grid">
            <Link className="action-card" to="/upload">
              <h2>Upload a file</h2>
              <p>Add a PDF, CSV, or image for analysis.</p>
            </Link>

            <Link className="action-card" to="/analysis">
              <h2>Analyse a file</h2>
              <p>View summaries and dataset insights.</p>
            </Link>

            <Link className="action-card" to="/charts">
              <h2>View charts</h2>
              <p>Generate visualisations from CSV files.</p>
            </Link>
          </section>
        </>
      )}
    </main>
  );
}

export default Dashboard;