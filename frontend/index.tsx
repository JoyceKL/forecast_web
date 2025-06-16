
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Line } from "react-chartjs-2";
import "chart.js/auto";

export default function ForecastDashboard() {
  const [file, setFile] = useState(null);
  const [forecastData, setForecastData] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch("/api/forecast", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    setForecastData(data);
    setLoading(false);
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">Forecast Web Interface</h1>

      <Card>
        <CardContent className="p-4 space-y-4">
          <Input
            type="file"
            accept=".csv, .xlsx"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
          />
          <Button onClick={handleUpload} disabled={loading || !file}>
            {loading ? "Đang dự báo..." : "Dự báo với mô hình đã lưu"}
          </Button>
        </CardContent>
      </Card>

      {forecastData && (
        <Card>
          <CardContent className="p-4">
            <h2 className="text-xl font-semibold mb-4">Biểu đồ dự báo</h2>
            <Line
              data={{
                labels: forecastData.dates,
                datasets: [
                  {
                    label: "Thực tế",
                    data: forecastData.actual,
                    borderColor: "blue",
                    fill: false,
                  },
                  {
                    label: "Dự báo",
                    data: forecastData.predicted,
                    borderColor: "red",
                    fill: false,
                  },
                ],
              }}
              options={{
                responsive: true,
                plugins: {
                  legend: { position: "top" },
                  title: {
                    display: true,
                    text: "So sánh Thực tế và Dự báo",
                  },
                },
              }}
            />
          </CardContent>
        </Card>
      )}
    </div>
  );
}
