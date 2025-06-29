import { useState, useRef, useEffect } from "react";
import "./App.css";

function App() {
  const [prompt, setPrompt] = useState("");
  const [messages, setMessages] = useState([]);
  const [output, setOutput] = useState(null);
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  const handleGenerate = async () => {
    if (!prompt.trim()) return;

    const userMessage = { type: "user", text: prompt };
    setMessages((prev) => [...prev, userMessage]);
    setPrompt("");
    setLoading(true);

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 60000); // 60 seconds timeout

    try {
      const res = await fetch("http://localhost:5000/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId); // clear timeout if completed in time

      const data = await res.json();

      if (data.error) {
        setMessages((prev) => [
          ...prev,
          { type: "bot", text: `⚠️ ${data.error}` },
        ]);
        setOutput(null);
      } else {
        setMessages((prev) => [
          ...prev,
          { type: "bot", text: data.explanation },
        ]);
        setOutput({
          code: data.code || "No code returned.",
          narration: data.narration || "No narration returned.",
        });
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { type: "bot", text: "❌ Error contacting backend. Possibly timed out." },
      ]);
    }

    setLoading(false);
  };

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="app-container">
      {/* Left: Chat Section */}
      <div className="chat-section">
        <h2>EduMateAI Chat</h2>
        <div className="chat-history">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`chat-message ${msg.type === "user" ? "user-msg" : "bot-msg"}`}
            >
              <strong>{msg.type === "user" ? "You" : "EduMateAI"}:</strong>
              <div>{msg.text}</div>
            </div>
          ))}
          <div ref={bottomRef} />
        </div>
        <div className="chat-input">
          <textarea
            rows="3"
            placeholder="Ask any concept, like 'Photosynthesis' or 'Pythagorean theorem'..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
          />
          <button onClick={handleGenerate} disabled={loading}>
            {loading ? "Thinking..." : "Generate"}
          </button>
        </div>
      </div>

      {/* Right: Output Section */}
      <div className="output-section">
        <h2>AI Output</h2>
        {output ? (
          <>
            <h3>🎬 Manim Code:</h3>
            <pre className="code-block">{output.code}</pre>

            <h3>🔊 Narration:</h3>
            <p>{output.narration}</p>

            <h3>📹 Animation:</h3>
            {output.videoUrl ? (
              <video
                controls
                width="100%"
                style={{ maxHeight: "400px", marginTop: "10px" }}
                src={output.videoUrl}
              />
            ) : (
              <p>No video generated.</p>
            )}
          </>
        ) : (
          <p style={{ marginTop: "1rem" }}>AI animation and narration will appear here.</p>
        )} 

      </div>
    </div>
  );
}

export default App;
