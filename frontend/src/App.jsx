import { useState } from "react";

function App() {
  const [prompt, setPrompt] = useState("");
  const [response, setResponse] = useState("");

  const handleGenerate = async () => {
    try {
      const res = await fetch("http://localhost:5000/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });

      const data = await res.json();
      setResponse(JSON.stringify(data, null, 2));
    } catch (error) {
      setResponse("Error contacting backend.");
    }
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h1>EduMateAI</h1>
      <textarea
        rows="4"
        cols="60"
        placeholder="Type your prompt..."
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
      />
      <br />
      <button onClick={handleGenerate}>Generate</button>
      <pre>{response}</pre>
    </div>
  );
}

export default App;
