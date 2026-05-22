from flask import Flask, request
import requests
import threading
import time

app = Flask(__name__)

# =========================
# DISCORD WEBHOOKS
# =========================

DISCORD_WEBHOOKS = [
      "https://discord.com/api/webhooks/1506972179437453392/Ac21oW-4iluBB8ReuJ8HcR3r85v-39goUp7s7nHT3ClMAA_4xFIbIyJYmF8DzDWmIiNg",
      "https://discord.com/api/webhooks/1506972284437528576/IcZiXrkYg-QqkbWDYUkQ1CBw-0AiEo0jX5ADHr_37cg7V5zLRa0qjXkIyWH7y9q64Bx7",
      "https://discord.com/api/webhooks/1506972338195922945/w0zHFqMnY1ZW3sNnih6YYlV6hZoZeFmKhHvshmasVr-kGA7I2X5S9FOLHBNBQxpeQE-T",
      "https://discord.com/api/webhooks/1506972392499445760/KkegXNcqfrn1DRRRSW4pEuKWUnAS3LD78W74rh7J1YPym6nWJpP6NOvDvF4QjEVFMW0G"
]

# =========================
# STORAGE
# =========================

alert_buffer = []
timer_running = False

# =========================
# SEND SUMMARY
# =========================

def send_summary():

    global alert_buffer
    global timer_running

    # Wait 2 minutes
    time.sleep(120)

    # Remove duplicates
    unique_alerts = list(set(alert_buffer))

    if unique_alerts:

        message = "📊 DAILY ALERTS\n\n"

        message += "\n".join(unique_alerts)

        # Rotate webhook
        webhook = DISCORD_WEBHOOKS[
            int(time.time()) % len(DISCORD_WEBHOOKS)
        ]

        requests.post(
            webhook,
            json={"content": message}
        )

    # Reset
    alert_buffer = []
    timer_running = False

# =========================
# WEBHOOK
# =========================

@app.route("/webhook", methods=["POST"])
def webhook():

    global alert_buffer
    global timer_running

    data = request.json

    message = data.get("content", "")

    if not message:
        return "No message", 400

    # Add unique only
    if message not in alert_buffer:
        alert_buffer.append(message)

    # Start timer once
    if not timer_running:

        timer_running = True

        threading.Thread(
            target=send_summary
        ).start()

    return "OK", 200

# =========================
# START SERVER
# =========================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)