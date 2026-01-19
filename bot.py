import logging
import os
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import requests

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# توكن البوت
BOT_TOKEN = "8343772483:AAElQuvcUwMROBW3PKbX1B4V0Sq2wHQgZsw"
# رابط سيرفرك على Railway (عدله بعد ال deployment)
API_SERVER = "https://facematch-pro-production.up.railway.app"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    
    # رابط الموقع مع ID المستخدم
    website_link = f"https://ahmed-fawzy11.github.io/facematch-pro/?tgid={user_id}"
    
    try:
        # تسجيل المستخدم في السيرفر
        requests.post(f"{API_SERVER}/api/register-user", json={
            "user_id": user_id,
            "username": user.first_name,
            "telegram_username": user.username
        }, timeout=5)
    except:
        pass  # تجاهل الخطأ إذا السيرفر مش شغال
    
    await update.message.reply_text(
        f"🎭 **Welcome {user.first_name} to FaceMatch Pro!**\n\n"
        f"📸 *Discover which celebrity you look like!*\n\n"
        f"✨ **Features:**\n"
        f"• Take a selfie with camera\n"
        f"• Match with 200+ celebrities\n"
        f"• Get personality analysis\n"
        f"• Save results with photos\n"
        f"• View your match history\n\n"
        f"🚀 **Get Started:**\n"
        f"Click the link below:\n{website_link}\n\n"
        f"📱 *Open on mobile for best experience!*\n\n"
        f"🎯 **Commands:**\n"
        f"/start - Get your personal link\n"
        f"/myresults - View your saved matches\n"
        f"/stats - Your statistics\n"
        f"/leaderboard - Top users\n"
        f"/help - Show all commands",
        parse_mode='Markdown'
    )

async def myresults(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    
    try:
        # جلب النتائج من السيرفر
        response = requests.get(f"{API_SERVER}/api/get-user-results/{user_id}", timeout=10)
        data = response.json()
        
        if data.get("success") and data.get("total_results", 0) > 0:
            results = data["results"][:5]  # أول 5 نتائج
            
            message = f"📋 **{user.first_name}'s Recent Matches:**\n\n"
            
            for i, result in enumerate(results, 1):
                date_str = datetime.fromisoformat(result["timestamp"]).strftime("%Y-%m-%d")
                message += f"{i}. **{result['celebrity']}** - {result['match']}%\n"
                message += f"   📅 {date_str}\n\n"
            
            message += f"🔗 View all results on website:\n"
            message += f"https://ahmed-fawzy11.github.io/facematch-pro/?tgid={user_id}"
            
            await update.message.reply_text(message, parse_mode='Markdown')
            return
            
    except Exception as e:
        logger.error(f"Error fetching results: {e}")
    
    # Fallback message
    website_link = f"https://ahmed-fawzy11.github.io/facematch-pro/?tgid={user_id}"
    await update.message.reply_text(
        f"📋 **{user.first_name}'s Results**\n\n"
        f"Visit our website to view all your matches:\n{website_link}",
        parse_mode='Markdown'
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    
    try:
        # جلب الإحصائيات من السيرفر
        response = requests.get(f"{API_SERVER}/api/get-user-results/{user_id}", timeout=10)
        data = response.json()
        
        if data.get("success"):
            total = data.get("total_results", 0)
            
            # حساب أفضل نتيجة
            best_match = 0
            if data.get("results"):
                best_match = max([r.get("match", 0) for r in data["results"]])
            
            await update.message.reply_text(
                f"📊 **{user.first_name}'s Statistics**\n\n"
                f"🎯 Total Matches: {total}\n"
                f"👑 Best Match: {best_match}%\n"
                f"🏆 Total Points: {total * 10}\n\n"
                f"🔗 View details on website:\n"
                f"https://ahmed-fawzy11.github.io/facematch-pro/?tgid={user_id}",
                parse_mode='Markdown'
            )
            return
            
    except:
        pass
    
    # Fallback
    await update.message.reply_text(
        f"📊 **{user.first_name}'s Statistics**\n\n"
        f"Visit our website to see detailed stats:\n"
        f"https://ahmed-fawzy11.github.io/facematch-pro/?tgid={user_id}",
        parse_mode='Markdown'
    )

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        response = requests.get(f"{API_SERVER}/api/leaderboard", timeout=10)
        data = response.json()
        
        if data.get("success"):
            leaderboard_data = data.get("leaderboard", [])[:10]
            
            message = "🏆 **FaceMatch Pro Leaderboard**\n\n"
            
            medals = ["🥇", "🥈", "🥉", "4.", "5.", "6.", "7.", "8.", "9.", "10."]
            
            for i, user in enumerate(leaderboard_data):
                rank = medals[i] if i < len(medals) else f"{i+1}."
                message += f"{rank} **{user['username']}**\n"
                message += f"   Points: {user['total_points']} | Matches: {user['total_matches']}\n\n"
            
            message += f"👤 Total Users: {data.get('total_users', 0)}\n"
            message += f"📊 Total Results: {data.get('total_results', 0)}\n\n"
            message += "🔗 https://ahmed-fawzy11.github.io/facematch-pro/"
            
            await update.message.reply_text(message, parse_mode='Markdown')
            return
            
    except:
        pass
    
    await update.message.reply_text(
        "🏆 **FaceMatch Pro Leaderboard**\n\n"
        "Check the top users on our website!\n\n"
        "🔗 https://ahmed-fawzy11.github.io/facematch-pro/",
        parse_mode='Markdown'
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🆘 **FaceMatch Pro Help**\n\n"
        "🌐 **Website Features:**\n"
        "• Take photo - Use camera\n"
        "• View results - My Profile\n"
        "• Hall of Fame - See celebrities\n\n"
        "🤖 **Bot Commands:**\n"
        "/start - Get personal website link\n"
        "/myresults - View your matches\n"
        "/stats - Your statistics\n"
        "/leaderboard - Top users\n"
        "/help - This message\n\n"
        "📞 **Need help?**\n"
        "Contact: @your_username",
        parse_mode='Markdown'
    )

def main():
    TOKEN = BOT_TOKEN
    
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("myresults", myresults))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("leaderboard", leaderboard))
    app.add_handler(CommandHandler("help", help_cmd))
    
    print("🤖 FaceMatch Pro Bot is running...")
    print("🌐 Website: https://ahmed-fawzy11.github.io/facematch-pro/")
    print("🔗 API Server: ", API_SERVER)
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
