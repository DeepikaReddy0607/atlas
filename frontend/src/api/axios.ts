import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
  timeout: 60000,
  headers: {
    "Content-Type": "multipart/form-data",
  },
});

export default api;