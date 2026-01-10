const API_URL = "http://127.0.0.1:8000/chat/message";

export async function sendChatMessage(text, chatId) {
  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        text,
        chat_id: chatId,
      }),
    });

    if (!response.ok) {
      return { reply: "Jarvis encountered an error." };
    }

    const data = await response.json();

    return {
      reply: data.reply,
      chatId: data.chat_id,
    };
  } catch (error) {
    console.error("Chat API Error:", error);
    return { reply: "Jarvis connection failed." };
  }
}
