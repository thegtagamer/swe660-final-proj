import React, { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import axios from "axios";

const TrendsGraph = ({ apiUrl, title }) => {
  const [trends, setTrends] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTrends = async () => {
      try {
        const response = await axios.get(apiUrl);
        setTrends(response.data);
      } catch (err) {
        setError(err.message);
      }
    };
    fetchTrends();
  }, [apiUrl]);

// Determine label type dynamically
const getLabelKey = (trends) => {
  if (trends.length > 0) {
    if (trends[0].day) return "day"; // For daily data
    if (trends[0].week) return "week"; // For weekly data
    if (trends[0].month) return "month"; // For monthly data
  }
  return "timestamp"; // Default fallback (though unlikely for trends)
};

const labelKey = getLabelKey(trends);

const chartData = {
  labels: trends.map((entry) => entry[labelKey]), // Dynamically select label type
  datasets: [
    {
      label: "Avg Temperature (°C)",
      data: trends.map((entry) => entry.avg_temperature),
      borderColor: "rgba(75, 192, 192, 1)",
      backgroundColor: "rgba(75, 192, 192, 0.2)",
      fill: true,
      tension: 0.4,
    },
    {
      label: "Min Temperature (°C)",
      data: trends.map((entry) => entry.min_temperature),
      borderColor: "rgba(54, 162, 235, 1)",
      backgroundColor: "rgba(54, 162, 235, 0.2)",
      fill: true,
      tension: 0.4,
    },
    {
      label: "Max Temperature (°C)",
      data: trends.map((entry) => entry.max_temperature),
      borderColor: "rgba(255, 99, 132, 1)",
      backgroundColor: "rgba(255, 99, 132, 0.2)",
      fill: true,
      tension: 0.4,
    },
  ],
};

const options = {
  responsive: true,
  plugins: {
    legend: {
      position: "top",
    },
  },
  scales: {
    x: {
      title: {
        display: true,
        text:
          labelKey === "day"
            ? "Day (YYYY-MM-DD)"
            : labelKey === "week"
            ? "Week (Year)"
            : labelKey === "month"
            ? "Month (YYYY-MM)"
            : "Time",
      },
    },
    y: {
      title: {
        display: true,
        text: "Temperature (°C)",
      },
    },
  },
};



  return (
    <div>
      <h2>{title}</h2>
      {error ? (
        <p>Error: {error}</p>
      ) : trends.length === 0 ? (
        <p>Loading...</p>
      ) : (
        <Line data={chartData} options={options} />
      )}
    </div>
  );
};

export default TrendsGraph;
