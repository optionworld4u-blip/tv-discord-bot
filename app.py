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

    # Wait before sending summary
    time.sleep(45)

    parsed_alerts = {}

    # =========================
    # PARSE ALERTS
    # =========================

    for msg in alert_buffer:

        try:

            # Example:
            # TECHNOE Close: 1339.90 Crossed Above: 1335.6 RSI: 67.20

            parts = msg.split(" RSI: ")

            left = parts[0]
            rsi = float(parts[1])

            ticker = left.split(" Close: ")[0]

            close_part = left.split(" Close: ")[1]

            close = float(
                close_part.split(" Crossed Above: ")[0]
            )

            cross = float(
                left.split(" Crossed Above: ")[1]
            )

            parsed_alerts[ticker] = {
                "ticker": ticker,
                "close": close,
                "cross": cross,
                "rsi": rsi
            }

        except:
            pass

    alerts = list(parsed_alerts.values())

    # =========================
    # SORT BY RSI DESCENDING
    # =========================

    alerts.sort(
        key=lambda x: x["rsi"],
        reverse=True
    )

    # =========================
    # BUILD MESSAGE
    # =========================

    if alerts:

        message = "📊 DAILY BREAKOUTS\n```"

        message += (
            "+---------+----------------+----------+----------------+--------+\n"
            "| Sr. No. |     STOCK      |  CLOSE   |  CROSS ABOVE   |  RSI   |\n"
            "+---------+----------------+----------+----------------+--------+\n"
        )

        for idx, a in enumerate(alerts, start=1):

            sr = str(idx).center(7)
            stock = f"{a['ticker']:^14}"[:14]
            close = f"{a['close']:.2f}".center(8)
            cross = f"{a['cross']:.2f}".center(14)
            rsi = f"{a['rsi']:.2f}".center(6)

            message += (
                f"| {sr} | "
                f"{stock} | "
                f"{close} | "
                f"{cross} | "
                f"{rsi} |\n"
            )

        message += (
            "+---------+----------------+----------+----------------+--------+"
        )

        message += "\n```"

        # =========================
        # ROTATE WEBHOOK
        # =========================

        webhook = DISCORD_WEBHOOKS[
            int(time.time()) % len(DISCORD_WEBHOOKS)
        ]

        # =========================
        # SEND TO DISCORD
        # =========================

        requests.post(
            webhook,
            json={"content": message}
        )

    # =========================
    # RESET
    # =========================

    alert_buffer = []
    timer_running = False

# =========================
# WEBHOOK ENDPOINT
# =========================

@app.route("/webhook", methods=["POST"])
def webhook():

    global alert_buffer
    global timer_running

    data = request.json

    message = data.get("content", "")

    # Ignore empty alerts
    if not message:
        return "No message", 400

    # Prevent duplicates
    if message not in alert_buffer:
        alert_buffer.append(message)

    # Start timer only once
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
