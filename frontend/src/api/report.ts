const API_BASE = "http://localhost:8000";

export async function exportAtlasReport(file: File) {
  const formData = new FormData();
  formData.append("image", file);

  const response = await fetch(`${API_BASE}/atlas/report`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Failed to generate report");
  }

  return await response.blob();
}