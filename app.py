from flask import Flask, request
import requests
import threading
import time

app = Flask(__name__)

# =========================================================
# DISCORD WEBHOOKS
# =========================================================

DISCORD_WEBHOOKS = {

    "nse": [
      "https://discord.com/api/webhooks/1506972179437453392/Ac21oW-4iluBB8ReuJ8HcR3r85v-39goUp7s7nHT3ClMAA_4xFIbIyJYmF8DzDWmIiNg",
      "https://discord.com/api/webhooks/1506972284437528576/IcZiXrkYg-QqkbWDYUkQ1CBw-0AiEo0jX5ADHr_37cg7V5zLRa0qjXkIyWH7y9q64Bx7",
      "https://discord.com/api/webhooks/1506972338195922945/w0zHFqMnY1ZW3sNnih6YYlV6hZoZeFmKhHvshmasVr-kGA7I2X5S9FOLHBNBQxpeQE-T",
      "https://discord.com/api/webhooks/1506972392499445760/KkegXNcqfrn1DRRRSW4pEuKWUnAS3LD78W74rh7J1YPym6nWJpP6NOvDvF4QjEVFMW0G"
    ],

    "sp500": [
        "https://discord.com/api/webhooks/1506975860857638934/LcIU0lXeWZnAjr7oklkTY_b7soC-jhysJIh_WH4nRul7vUeo3n3TlktwxedIfhqA_CFL",
        "https://discord.com/api/webhooks/1506975868872822814/ySPgi_o_ba3F4QnJ2DvAihZsl8k8fTqefmXEi1vG6zVZJKllGo5bsghXOlZx1Ge5v0w7",
        "https://discord.com/api/webhooks/1506975878025056357/lE5tsCfJxIFVc8_n5lQX_lU5Ta4DKJULWFCTzgIAVzBpcHI7IeyQwwrLh_FUckfxSffN",
        "https://discord.com/api/webhooks/1506975888158363713/VxMbsTJuLjSpab86DMGQh17H0n8fMORKYgzLARx38_wiqRvZMOHC-K6pA9okwHaIMryZ"
    ]

}

# =========================================================
# MARKET-WISE STORAGE
# =========================================================

market_buffers = {
    "nse": [],
    "sp500": []
}

market_timers = {
    "nse": False,
    "sp500": False
}

# =========================================================
# SEND SUMMARY
# =========================================================

def send_summary(market):

    global market_buffers
    global market_timers

    # Wait before sending summary
    time.sleep(45)

    parsed_alerts = {}

    # =====================================================
    # GET MARKET BUFFER
    # =====================================================

    buffer = market_buffers[market]

    # =====================================================
    # PARSE ALERTS
    # =====================================================

    for msg in buffer:

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

    # =====================================================
    # SORT BY RSI DESCENDING
    # =====================================================

    alerts.sort(
        key=lambda x: x["rsi"],
        reverse=True
    )

    # =====================================================
    # BUILD MESSAGE
    # =====================================================

    if alerts:

        # Market-specific title
        if market == "nse":
            message = "📊 NSE DAILY BREAKOUTS\n\n"

        elif market == "sp500":
            message = "📊 S&P500 DAILY BREAKOUTS\n\n"

        else:
            message = "📊 DAILY BREAKOUTS\n\n"

        # Add stock alerts
        for idx, a in enumerate(alerts, start=1):

            message += (
                f"{idx}. {a['ticker']}\n"
                f"Close {a['close']:.2f}\n"
                f"Cross↑ {a['cross']:.2f}\n"
                f"RSI {a['rsi']:.2f}\n\n"
            )

        # =================================================
        # SELECT WEBHOOK
        # =================================================

        market_webhooks = DISCORD_WEBHOOKS.get(market, [])

        if market_webhooks:

            webhook = market_webhooks[
                int(time.time()) % len(market_webhooks)
            ]

            # =============================================
            # SEND TO DISCORD
            # =============================================

            requests.post(
                webhook,
                json={"content": message}
            )

    # =====================================================
    # RESET MARKET BUFFER
    # =====================================================

    market_buffers[market] = []
    market_timers[market] = False

# =========================================================
# WEBHOOK ENDPOINT
# =========================================================

@app.route("/webhook/<market>", methods=["POST"])
def webhook(market):

    global market_buffers
    global market_timers

    # Invalid market protection
    if market not in market_buffers:
        return "Invalid market", 400

    data = request.json

    message = data.get("content", "")

    # Ignore empty alerts
    if not message:
        return "No message", 400

    # =====================================================
    # ADD TO MARKET BUFFER
    # =====================================================

    if message not in market_buffers[market]:
        market_buffers[market].append(message)

    # =====================================================
    # START MARKET TIMER
    # =====================================================

    if not market_timers[market]:

        market_timers[market] = True

        threading.Thread(
            target=send_summary,
            args=(market,)
        ).start()

    return "OK", 200

# =========================================================
# HOME ROUTE
# =========================================================

@app.route("/")
def home():
    return "TradingView Discord Bot Running"

# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
