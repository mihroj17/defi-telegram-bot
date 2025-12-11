import requests
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# === ⚙️ НАСТРОЙКИ — ЗАМЕНИ НА СВОИ ===
TELEGRAM_TOKEN = "8582343463:AAG2cTaWdZZ7vxFgOOwqvFw0JmEoaeCywOk
"
CHAT_ID = 0  # ID: 910867347

# Логирование (для отладки)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def get_best_usdt_pools():
    url = "https://yields.llama.fi/pools"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        pools = [
            p for p in data["data"]
            if "USDT" in p.get("symbol", "") and
               p.get("chain") == "Polygon" and
               p.get("tvlUsd", 0) > 500000 and
               p.get("apy", 0) > 1
        ]
        pools.sort(key=lambda x: x["apy"], reverse=True)
        return pools[:3]
    except Exception as e:
        print("Ошибка получения данных:", e)
        return []

async def send_defi_update(context):
    pools = get_best_usdt_pools()
    if not pools:
        msg = "❌ Нет подходящих пулов с USDT на Polygon."
    else:
        msg = "📈 Топ DeFi-доходность (USDT, Polygon):\n\n"
        for p in pools:
            msg += f"🔹 {p['project']} — {p['apy']:.2f}% APY\n"
            msg += f"🔗 {p.get('url', '—')}\n\n"
    await context.bot.send_message(chat_id=CHAT_ID, text=msg)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Бот активен! Обновления приходят каждый час.")
    # Отправляем первое обновление сразу
    await send_defi_update(context)

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    job_queue = app.job_queue
    job_queue.run_repeating(send_defi_update, interval=3600, first=10)  # Каждый час
    app.run_polling()

if __name__ == "__main__":

  
    main()
