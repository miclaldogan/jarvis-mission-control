import "./App.css";
import { useSystemVitals } from "./hooks/useSystemVitals";
import { useContextData } from "./hooks/useContextData";
import { useMissions } from "./hooks/useMissions";

function App() {
  const { data: vitals, loading: vitalsLoading } = useSystemVitals();
  const { data: context, loading: contextLoading } = useContextData();
  const { missions, loading: missionsLoading } = useMissions();

  return (
    <div style={{ padding: "2rem", fontFamily: "monospace" }}>
      <h1>🧠 Jarvis Mission Control</h1>

      {/* SYSTEM VITALS */}
      <section>
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
      </section>

      <hr />

      {/* CONTEXT */}
      <section>
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
      </section>

      <hr />

      {/* MISSIONS */}
      <section>
        <h2>🎯 Missions</h2>
        {missionsLoading ? (
          <p>Loading missions...</p>
        ) : (
          <ul>
            {missions.map((m) => (
              <li key={m.id}>
                [{m.priority.toUpperCase()}] {m.title}{" "}
                {m.completed ? "✅" : "⏳"}
              </li>

import "./App.css";
import { useSystemVitals } from "./hooks/useSystemVitals";
import { useContextData } from "./hooks/useContextData";
import { useMissions } from "./hooks/useMissions";

function App() {
  const { data: vitals, loading: vitalsLoading } = useSystemVitals();
  const { data: context, loading: contextLoading } = useContextData();
  const { missions, loading: missionsLoading } = useMissions();

  return (
    <div style={{ padding: "2rem", fontFamily: "monospace" }}>
      <h1>🧠 Jarvis Mission Control</h1>

      {/* SYSTEM VITALS */}
      <section>
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
      </section>

      <hr />

      {/* CONTEXT */}
      <section>
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
      </section>

      <hr />

      {/* MISSIONS */}
      <section>
        <h2>🎯 Missions</h2>
        {missionsLoading ? (
          <p>Loading missions...</p>
        ) : (
          <ul>
            {missions.map((m) => (
              <li key={m.id}>
                [{m.priority.toUpperCase()}] {m.title}{" "}
                {m.completed ? "✅" : "⏳"}
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

export default App;
