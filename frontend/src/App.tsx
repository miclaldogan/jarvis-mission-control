import "./App.css";
import { useSystemVitals } from "./hooks/useSystemVitals";
import { useContextData } from "./hooks/useContextData";
import { useMissions } from "./hooks/useMissions";

function App() {
  const { data: vitals, loading: vitalsLoading } = useSystemVitals();
  const { data: context, loading: contextLoading } = useContextData();
  const { missions, loading: missionsLoading } = useMissions();

  return (
    <div style={{ padding: "2rem", maxWidth: 900, margin: "0 auto" }}>
      <h1>🧠 Jarvis Mission Control</h1>

      <div className="section">
        <h2>⚙️ System Vitals</h2>
        {vitalsLoading ? (
          <p>Loading vitals...</p>
        ) : (
          <ul>
            <li>CPU: {vitals?.cpu}%</li>
            <li>Memory: {vitals?.memory} GB</li>
            <li>Load: {vitals?.load}</li>
          </ul>
        )}
      </div>

      <div className="section">
        <h2>🌍 Context</h2>
        {contextLoading ? (
          <p>Loading context...</p>
        ) : (
          <ul>
            <li>Weather: {context?.weather}</li>
            <li>Calendar events: {context?.calendarEvents}</li>
            <li>Unread emails: {context?.unreadEmails}</li>
          </ul>
        )}
      </div>

      <div className="section">
        <h2>🎯 Missions</h2>
        {missionsLoading ? (
          <p>Loading missions...</p>
        ) : (
          <ul>
            {missions.map((m) => (
              <li key={m.id}>
                <span className={`badge ${m.priority}`}>
                  {m.priority.toUpperCase()}
                </span>
                {m.title} {m.completed ? "✅" : "⏳"}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default App;
