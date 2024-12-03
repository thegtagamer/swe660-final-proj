import React from "react";
import Highcharts from "highcharts";
import HighchartsReact from "highcharts-react-official";

const TodayChart = ({ data }) => {
  const options = {
    title: { text: "Today vs Yesterday" },
    xAxis: { categories: data.time },
    series: [
      { name: "Temperature", data: data.temperature },
      { name: "Humidity", data: data.humidity },
    ],
  };

  return <HighchartsReact highcharts={Highcharts} options={options} />;
};

export default TodayChart;
