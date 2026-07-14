import api from "./axios";

export const analyzeImage = async (file: File) => {
  const formData = new FormData();

  // MUST match the FastAPI parameter name
  formData.append("image", file);

  const response = await api.post(
    "/atlas/analyze",
    formData
  );

  return response.data;
};