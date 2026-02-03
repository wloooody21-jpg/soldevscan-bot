import os
import json
from datetime import datetime, timezone

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def norm_user(arg: str) -> str:
    return arg.strip().lstrip("@").lower()

def ensure_user(data, user):
    if user not in data:
        data[user] = {"done": 0, "fail": 0, "notes": [], "updated_at": None}

async def add_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        return await update.message.reply_text("الاستخدام: /add @dev 3 (واختياري سبب)\nمثال: /add @ali 2 fix bugs")
    user = norm_user(context.args[0])
    try:
        n = int(context.args[1])
    except:
        return await update.message.reply_text("الرقم لازم يكون عدد صحيح.")
    note = " ".join(context.args[2:]).strip()
    data = load_data()
    ensure_user(data, user)
    data[user]["done"] += n
    if note:
        data[user]["notes"].append({"type": "done", "n": n, "note": note, "at": datetime.now(timezone.utc).isoformat()})
    data[user]["updated_at"] = datetime.now(timezone.utc).isoformat()
    save_data(data)
    await update.message.reply_text(f"تم ✅ @{user}: +{n} منجز")

async def fail_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        return await update.message.reply_text("الاستخدام: /fail @dev 1 (واختياري سبب)\nمثال: /fail @ali 1 تأخير")
    user = norm_user(context.args[0])
    try:
        n = int(context.args[1])
    except:
        return await update.message.reply_text("الرقم لازم يكون عدد صحيح.")
    note = " ".join(context.args[2:]).strip()
    data = load_data()
    ensure_user(data, user)
    data[user]["fail"] += n
    if note:
        data[user]["notes"].append({"type": "fail", "n": n, "note": note, "at": datetime.now(timezone.utc).isoformat()})
    data[user]["updated_at"] = datetime.now(timezone.utc).isoformat()
    save_data(data)
    await update.message.reply_text(f"تم ⚠️ @{user}: +{n} فشل/سقوط")

async def report_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    if not data:
        return await update.message.reply_text("ما فيه بيانات للحين. استخدم /add و /fail.")
    lines = ["تقرير الديفات:\n"]
    for user, s in sorted(data.items(), key=lambda x: (-(x[1].get("done", 0)), x[0])):
        done = s.get("done", 0)
        fail = s.get("fail", 0)
        updated = s.get("updated_at") or "-"
        lines.append(f"- @{user}: منجز={done} | سقط/فشل={fail} | آخر تحديث={updated}")
    await update.message.reply_text("\n".join(lines))

async def reset_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # بسيطة: تمسح كل شيء (تقدر لاحقًا نخليها للأدمن فقط)
    save_data({})
    await update.message.reply_text("تم تصفير البيانات.")

def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN env var is missing")
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("add", add_cmd))
    app.add_handler(CommandHandler("fail", fail_cmd))
    app.add_handler(CommandHandler("report", report_cmd))
    app.add_handler(CommandHandler("reset", reset_cmd))
    app.run_polling()

if __name__ == "__main__":
    main()
