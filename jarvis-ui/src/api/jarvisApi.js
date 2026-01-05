const API_URL = "http://127.0.0.1:8000/command";

export async function sendCommand(command) {
  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ command }),
    });

    if (!response.ok) {
      return { reply: "Jarvis encountered an error." };
    }

    const data = await response.json();

    return {
      reply: data?.reply ?? "No response from Jarvis",
      intent: data?.intent,
      confidence: data?.confidence,
    };
  } catch (error) {
    console.error("API Error:", error);
    return { reply: "Jarvis connection failed." };
  }
}
