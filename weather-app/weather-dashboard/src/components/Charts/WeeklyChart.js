import React from "react";
import Highcharts from "highcharts";
import HighchartsReact from "highcharts-react-official";

const WeeklyChart = ({ data }) => {
  const options = {
    title: { text: "Last Week Data" },
    xAxis: { categories: data.time },
    series: [
      { name: "Temperature", data: data.temperature },
      { name: "Humidity", data: data.humidity },
    ],
  };

  return <HighchartsReact highcharts={Highcharts} options={options} />;
};

export default WeeklyChart;
