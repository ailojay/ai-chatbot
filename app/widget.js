(function () {
  const API_URL = "https://8b1cdlmrng.execute-api.us-east-1.amazonaws.com/chat";

  // Create chat button
  const button = document.createElement("div");
  button.innerHTML = "💬";
  button.style.position = "fixed";
  button.style.bottom = "20px";
  button.style.right = "20px";
  button.style.width = "60px";
  button.style.height = "60px";
  button.style.borderRadius = "50%";
  button.style.background = "#28a745";
  button.style.color = "white";
  button.style.display = "flex";
  button.style.alignItems = "center";
  button.style.justifyContent = "center";
  button.style.cursor = "pointer";
  button.style.fontSize = "24px";
  button.style.zIndex = "9999";

  document.body.appendChild(button);

  // Create chat box
  const chatBox = document.createElement("div");
  chatBox.style.position = "fixed";
  chatBox.style.bottom = "90px";
  chatBox.style.right = "20px";
  chatBox.style.width = "300px";
  chatBox.style.height = "400px";
  chatBox.style.background = "white";
  chatBox.style.border = "1px solid #ddd";
  chatBox.style.borderRadius = "10px";
  chatBox.style.display = "none";
  chatBox.style.flexDirection = "column";
  chatBox.style.zIndex = "9999";

  chatBox.innerHTML = `
    <div style="padding:10px;background:#28a745;color:white;border-radius:10px 10px 0 0;">
      Chat with us
    </div>
    <div id="messages" style="flex:1; padding:10px; overflow-y:auto;"></div>
    <div style="display:flex;">
      <input id="input" style="flex:1; padding:10px; border:none; border-top:1px solid #ddd;" placeholder="Type a message"/>
      <button id="send" style="padding:10px;">Send</button>
    </div>
  `;

  document.body.appendChild(chatBox);

  // Toggle chat
  button.onclick = () => {
    chatBox.style.display = chatBox.style.display === "none" ? "flex" : "none";
  };

  const messagesDiv = chatBox.querySelector("#messages");
  const input = chatBox.querySelector("#input");
  const sendBtn = chatBox.querySelector("#send");

  const sessionId = "web-" + Math.random().toString(36).substring(2);

  function addMessage(text, sender) {
    const msg = document.createElement("div");
    msg.style.marginBottom = "10px";
    msg.innerHTML = `<strong>${sender}:</strong> ${text}`;
    messagesDiv.appendChild(msg);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
  }

  async function sendMessage() {
    const text = input.value;
    if (!text) return;

    addMessage(text, "You");
    input.value = "";

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          message: text,
          session_id: sessionId
        })
      });

      const data = await res.json();
      addMessage(data.response, "Bot");

    } catch (err) {
      addMessage("Error connecting to server", "Bot");
    }
  }

  sendBtn.onclick = sendMessage;
  input.addEventListener("keypress", e => {
    if (e.key === "Enter") sendMessage();
  });

})();
