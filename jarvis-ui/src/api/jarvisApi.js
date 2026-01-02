const API_URL = "http://127.0.0.1:8000/command";

export async function sendCommand(command) {
  const response = await fetch(API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ command }),
  });

  if (!response.ok) {
    throw new Error("Failed to send command");
  }

  return response.json();
}
