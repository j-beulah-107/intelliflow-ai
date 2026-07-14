import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";

function Upload() {
  const navigate = useNavigate();

  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const handleUpload = async (event) => {
    event.preventDefault();

    if (!selectedFile) {
      setMessage("Please select a file.");
      return;
    }

    const token = localStorage.getItem("access_token");

    if (!token) {
      navigate("/");
      return;
    }

    setLoading(true);
    setMessage("");
    setUploadedFile(null);

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);

      const response = await axios.post(
        "http://127.0.0.1:8000/files/upload",
        formData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const savedFile = response.data.file;

      if (!savedFile || !savedFile.id) {
        throw new Error("File ID was not returned by the backend.");
      }

      setUploadedFile(savedFile);
      setMessage("File uploaded successfully.");
    } catch (error) {
      setMessage(
        error.response?.data?.detail ||
          error.message ||
          "Upload failed."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyse = () => {
    if (!uploadedFile?.id) {
      setMessage("Uploaded file ID is missing.");
      return;
    }

    navigate(`/analysis?fileId=${uploadedFile.id}`);
  };

  const handleCharts = () => {
    if (!uploadedFile?.id) {
      setMessage("Uploaded file ID is missing.");
      return;
    }

    navigate(`/charts?fileId=${uploadedFile.id}`);
  };

  const isCsv =
    uploadedFile?.original_name
      ?.toLowerCase()
      .endsWith(".csv");

  return (
    <main className="dashboard-page">
      <header className="page-header">
        <div>
          <div className="brand">IntelliFlow AI</div>
          <h1>Upload a file</h1>
          <p>
            Upload a PDF, CSV, PNG, JPG, or JPEG file.
          </p>
        </div>

        <Link
          className="secondary-button"
          to="/dashboard"
        >
          Back to dashboard
        </Link>
      </header>

      <section className="content-card">
        <form
          className="upload-form"
          onSubmit={handleUpload}
        >
          <label>
            Choose file
            <input
              type="file"
              accept=".pdf,.csv,.png,.jpg,.jpeg"
              onChange={(event) => {
                const file =
                  event.target.files?.[0] || null;

                setSelectedFile(file);
                setUploadedFile(null);
                setMessage("");
              }}
            />
          </label>

          <button
            type="submit"
            disabled={loading}
          >
            {loading
              ? "Uploading..."
              : "Upload file"}
          </button>
        </form>

        {message && <p>{message}</p>}

        {uploadedFile && (
          <div className="upload-result">
            <h2>Upload completed</h2>

            <p>
              <strong>File:</strong>{" "}
              {uploadedFile.original_name}
            </p>

            <p>
              <strong>File ID:</strong>{" "}
              {uploadedFile.id}
            </p>

            <div className="upload-actions">
              <button
                type="button"
                onClick={handleAnalyse}
              >
                Analyse file
              </button>

              {isCsv && (
                <button
                  type="button"
                  onClick={handleCharts}
                >
                  Generate charts
                </button>
              )}
            </div>
          </div>
        )}
      </section>
    </main>
  );
}

export default Upload;