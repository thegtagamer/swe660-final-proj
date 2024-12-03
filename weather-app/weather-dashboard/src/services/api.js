import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:9080", // Backend base URL
});

// export const fetchTodayData = () => api.get("/data/today");
// export const fetchWeeklyData = () => api.get("/data/weekly");
// export const fetchStats = () => api.get("/data/stats");

// export default { fetchTodayData, fetchWeeklyData };
