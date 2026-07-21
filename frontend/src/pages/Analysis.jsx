import { useEffect, useState } from "react";
import {
  Link,
  useNavigate,
  useSearchParams,
} from "react-router-dom";
import axios from "axios";
import Navbar from "../components/Navbar";

function Analysis() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const [fileId, setFileId] = useState(
    searchParams.get("fileId") || ""
  );

  const [result, setResult] = useState(null);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const analyseFile = async (selectedFileId) => {
    if (!selectedFileId) {
      setMessage("Please enter a file ID.");
      return;
    }

    const token = localStorage.getItem("access_token");

    if (!token) {
      navigate("/");
      return;
    }

    setLoading(true);
    setMessage("");
    setResult(null);

    try {
      const response = await axios.get(
        `http://127.0.0.1:8000/analysis/${selectedFileId}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setResult(response.data);
    } catch (error) {
      setMessage(
        error.response?.data?.detail ||
          "Unable to analyse this file."
      );

      if (error.response?.status === 401) {
        localStorage.removeItem("access_token");
        navigate("/");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const queryFileId = searchParams.get("fileId");

    if (queryFileId) {
      setFileId(queryFileId);
      analyseFile(queryFileId);
    }
  }, []);

  const handleAnalysis = async (event) => {
    event.preventDefault();
    await analyseFile(fileId);
  };

  return (
    <>
      <Navbar />

      <main className="dashboard-page">
        <header className="page-header">
          <div>
            <h1>Analyse a File</h1>
            <p>View summaries, statistics and AI insights.</p>
          </div>

          <Link
            className="secondary-button"
            to="/dashboard"
          >
            Back to Dashboard
          </Link>
        </header>

        <section className="content-card">
          <form
            className="analysis-form"
            onSubmit={handleAnalysis}
          >
            <label>
              File ID

              <input
                type="number"
                min="1"
                value={fileId}
                onChange={(event) =>
                  setFileId(event.target.value)
                }
                placeholder="Example: 17"
                required
              />
            </label>

            <button type="submit" disabled={loading}>
              {loading ? "Analysing..." : "Analyse File"}
            </button>
          </form>

          {message && (
            <p className="error-message">{message}</p>
          )}
        </section>

        {result && (
          <section className="content-card result-card">
            <h2>Analysis Result</h2>

            <div className="result-meta">
              <span>
                <strong>File:</strong>{" "}
                {result.original_name}
              </span>

              <span>
                <strong>Type:</strong>{" "}
                {result.type?.toUpperCase()}
              </span>
            </div>

            {result.type === "pdf" && (
              <>
                <h3>Summary</h3>

                <p className="result-text">
                  {result.summary ||
                    "No summary available."}
                </p>

                <h3>Text Preview</h3>

                <p className="result-text preview-box">
                  {result.preview}
                </p>

                <p>
                  <strong>Character Count:</strong>{" "}
                  {result.character_count}
                </p>
              </>
            )}

            {result.type === "csv" && (
              <>
                <h3>Generated Report</h3>

                <p className="result-text">
                  {result.report}
                </p>

                <div className="stats-grid">
                  <article className="stat-card">
                    <span>Rows</span>
                    <strong>
                      {result.summary?.rows ?? 0}
                    </strong>
                  </article>

                  <article className="stat-card">
                    <span>Columns</span>
                    <strong>
                      {result.summary?.columns?.length ?? 0}
                    </strong>
                  </article>
                </div>

                <h3>Columns</h3>

                <p>
                  {result.summary?.columns?.join(", ")}
                </p>

                <h3>Missing Values</h3>

                <pre className="json-box">
                  {JSON.stringify(
                    result.summary?.missing_values,
                    null,
                    2
                  )}
                </pre>

                <h3>Sample Data</h3>

                <pre className="json-box">
                  {JSON.stringify(
                    result.summary?.sample_data,
                    null,
                    2
                  )}
                </pre>
              </>
            )}

            {result.type === "image" && (
              <>
                <h3>AI Description</h3>

                <div className="upload-result">
                  <p
                    style={{
                      fontSize: "18px",
                      fontWeight: "600",
                      margin: 0,
                    }}
                  >
                    {result.ai_caption ||
                      "No AI description was generated."}
                  </p>
                </div>

                <h3>Image Report</h3>

                <p className="result-text">
                  {result.message}
                </p>

                <div className="stats-grid">
                  <article className="stat-card">
                    <span>Format</span>
                    <strong>
                      {result.summary?.format || "-"}
                    </strong>
                  </article>

                  <article className="stat-card">
                    <span>Resolution</span>
                    <strong>
                      {result.summary?.resolution || "-"}
                    </strong>
                  </article>

                  <article className="stat-card">
                    <span>Orientation</span>
                    <strong>
                      {result.summary?.orientation || "-"}
                    </strong>
                  </article>

                  <article className="stat-card">
                    <span>Brightness</span>
                    <strong>
                      {result.summary?.brightness_level || "-"}
                    </strong>
                  </article>
                </div>

                <h3>Additional Details</h3>

                <div className="stats-grid">
                  <article className="stat-card">
                    <span>Colour Mode</span>
                    <strong>
                      {result.summary?.colour_mode || "-"}
                    </strong>
                  </article>

                  <article className="stat-card">
                    <span>Megapixels</span>
                    <strong>
                      {result.summary?.megapixels ?? "-"}
                    </strong>
                  </article>

                  <article className="stat-card">
                    <span>Aspect Ratio</span>
                    <strong>
                      {result.summary?.aspect_ratio ?? "-"}
                    </strong>
                  </article>

                  <article className="stat-card">
                    <span>File Size</span>
                    <strong>
                      {result.summary?.file_size_kb
                        ? `${result.summary.file_size_kb} KB`
                        : "-"}
                    </strong>
                  </article>
                </div>
              </>
            )}
          </section>
        )}
      </main>
    </>
  );
}

export default Analysis;