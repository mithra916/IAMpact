import { useEffect, useState } from "react";
import socketService from "../services/socket";

export default function LiveFeed() {
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    socketService.connect((data) => {
      setAlerts((prev) => [data, ...prev]);
    });

    return () => socketService.disconnect();
  }, []);

  return (
    <div className="bg-black text-green-400 p-4 rounded-lg h-[500px] overflow-auto">
      <h2 className="text-white text-xl mb-4">LIVE SOC FEED</h2>

      {alerts.map((alert, index) => (
        <div key={index} className="border-b border-gray-700 py-2">
          <p>IP: {alert.src_ip}</p>
          <p>Event: {alert.event_type}</p>
          <p>Severity: {alert.severity}</p>
          <p>Risk: {alert.risk_score}</p>
        </div>
      ))}
    </div>
  );
}