import React, { useEffect, useState } from "react";
import socket from "../services/socketService";
import Header from "../components/Header";
import Footer from "../components/Footer";
// import StatCard from "../components/Card/StatCard";
// import TodayChart from "../components/Charts/TodayChart";
// import WeeklyChart from "../components/Charts/WeeklyChart";
// import RealTimeData from "../components/RealTimeData";
// import LatestTemperature from "../components/LatestTemperature";
import TodayTrends from "../components/TodayTrends";
import TrendsGraph from "../components/TrendsGraph";
import { FaTree, FaHome, FaRegSnowflake, FaSun } from "react-icons/fa";
import DatePicker from "react-datepicker";
import Card from "../components/Card/Card";
import "./Dashboard.css"

// import api from "../services/api";

const Dashboard = () => {
  const [temperature, setTemperature] = useState(null);
  const [error, setError] = useState(null);
  const [trend, setTrend] = useState('weekly');
  const [date, setDate] = useState(new Date());
  // const [startDate, setStartDate] = useState();
  // const [endDate, setEndDate] = useState();
  const [startDate, setStartDate] = useState( new Date('2024-12-01T00:00:00'));
  const [endDate, setEndDate] = useState( new Date('2024-12-07T23:59:59'));


  useEffect(() => {
    // Connect to the WebSocket
    socket.on("connect", () => {
      console.log("Connected to WebSocket server");

      // Request the latest temperature
      socket.emit("latest_temperature");
    });

    // Listen for the latest temperature updates
    socket.on("latest_temperature_response", (data) => {
      console.log("latest");
      setTemperature(data);
    });

    // Handle WebSocket errors
    socket.on("connect_error", (err) => {
      console.error("WebSocket connection error:", err);
      setError("Failed to connect to the server.");
    });

    // Cleanup on unmount
    return () => {
      socket.off("latest_temperature_response");
      socket.off("connect_error");
    };
  }, []);


  const cardsData = [
    {
      icon: <FaHome size={40} color="#fff" />,
      temperature: temperature && temperature.temperature || 'Loading',
      title: "Current Temperature",
      bgColor: "#007bff", // Blue
    },
    {
      icon: <FaTree size={40} color="#fff" />,
      humidity: temperature && temperature.humidity || 'Loading',
      title: "Current Humidity",
      // subtitle: "",
      bgColor: "#28a745", // Green
    },
    // Change conditions in below 
    {
      icon: 'sunny' ? <FaSun size={40} color="#fff" /> : <FaRegSnowflake size={40} color="#fff" />,
      temperature: temperature && temperature.temperature || 'Loading',
      title: "Tommorow Forecast",
      subtitle: "Details on Forecast.io",
      bgColor: "#ffc107", // Yellow
    },
  ];

  return (
    <div>
      <Header />

      <div className="cards-container">
        {cardsData.map((card, index) => (
          <div
            key={index}
            style={{ backgroundColor: card.bgColor, color: "#fff" }}
            className="card-wrapper"
          >
            <Card
              icon={card.icon}
              temperature={card.temperature}
              humidity={card.humidity}
              title={card.title}
              subtitle={card.subtitle}
            />
          </div>
        ))}
      </div>

      {/* <LatestTemperature /> */}

      <TodayTrends />

      <div>
        <h1 style={{ textAlign: 'center' }}>Weather Trends</h1>
        <div className="trend-container">
          <div className={trend === 'weekly' ? 'trend-tab active' : 'trend-tab'} onClick={() => setTrend('weekly')}>Weekly</div>
          <div className={trend === 'monthly' ? 'trend-tab active' : 'trend-tab'} onClick={() => setTrend('monthly')}>Monthly</div>
          <div className={trend === 'yearly' ? 'trend-tab active' : 'trend-tab'} onClick={() => setTrend('yearly')}>Yearly</div>
          <div className={trend === 'custom' ? 'trend-tab active' : 'trend-tab'} onClick={() => setTrend('custom')}>Custom</div>
        </div>
        <div style={{ display: (trend === 'weekly' ? 'block' : 'none') }}>
          <TrendsGraph apiUrl="http://localhost:9080/trends/weekly" />
        </div>
        <div style={{ display: (trend === 'monthly' ? 'block' : 'none') }}>
          <TrendsGraph apiUrl="http://localhost:9080/trends/monthly" />
        </div>
        <div style={{ display: (trend === 'yearly' ? 'block' : 'none') }}>
          <TrendsGraph apiUrl="http://localhost:9080/trends/yearly" />
        </div>
        <div style={{ display: (trend === 'custom' ? 'block' : 'none') }}>
          <div className="custom-container">
            <div>
              <p>Start Date</p>
              <DatePicker
                selectsStart
                selected={startDate}
                onChange={(date) => setStartDate(date)}
                startDate={startDate}
              />
            </div>
            <div>
              <p>End Date</p>
              <DatePicker
                selectsEnd
                selected={endDate}
                onChange={(date) => setEndDate(date)}
                endDate={endDate}
                startDate={startDate}
                minDate={startDate}
              />
            </div>
          </div>
          <TrendsGraph apiUrl={`http://localhost:9080/trends/custom?start_date=` + startDate + `&end_date=` + endDate} />
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default Dashboard;
