from flask import Flask, request, jsonify
import json
import os
import uuid
from datetime import datetime
import base64
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app, origins=["https://ahmed-fawzy11.github.io", "http://localhost:*"])

# إعدادات
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# قاعدة بيانات بسيطة
RESULTS_DB = 'results.json'

# توكن البوت - احتفظ به هنا أو في متغير بيئة
BOT_TOKEN = "8343772483:AAElQuvcUwMROBW3PKbX1B4V0Sq2wHQgZsw"
WEBSITE_URL = "https://ahmed-fawzy11.github.io/facematch-pro/"

def load_db():
    try:
        if os.path.exists(RESULTS_DB):
            with open(RESULTS_DB, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return {"users": {}, "results": []}

def save_db(data):
    with open(RESULTS_DB, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "service": "FaceMatch Pro API",
        "version": "1.0",
        "website": WEBSITE_URL
    })

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/api/save-result', methods=['POST'])
def save_result():
    """استقبال النتيجة من الموقع وحفظها"""
    try:
        data = request.json
        
        # التحقق من البيانات المطلوبة
        required_fields = ['user_id', 'username', 'celebrity', 'match', 'personality']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing field: {field}'
                }), 400
        
        user_id = str(data['user_id'])
        username = data['username']
        celebrity = data['celebrity']
        match_percentage = data['match']
        personality = data['personality']
        image_data = data.get('image', '')  # Base64 image
        
        # توليد ID فريد للنتيجة
        result_id = str(uuid.uuid4().hex)[:12]
        
        # حفظ الصورة إذا كانت موجودة
        image_filename = None
        image_url = None
        
        if image_data and len(image_data) > 100:
            try:
                # إزالة header الـ base64
                if 'base64,' in image_data:
                    image_data = image_data.split('base64,')[1]
                
                # تحويل base64 إلى bytes
                image_bytes = base64.b64decode(image_data)
                
                # حفظ الصورة
                image_filename = f"{result_id}.jpg"
                image_path = os.path.join(UPLOAD_FOLDER, image_filename)
                
                with open(image_path, 'wb') as f:
                    f.write(image_bytes)
                
                # رابط الصورة (سيكون static على Railway)
                image_url = f"/uploads/{image_filename}"
                
            except Exception as img_error:
                print(f"⚠️ Error saving image: {img_error}")
                image_filename = None
        
        # تحضير بيانات النتيجة
        result_data = {
            "id": result_id,
            "user_id": user_id,
            "username": username,
            "celebrity": celebrity,
            "match": match_percentage,
            "personality": personality,
            "image_filename": image_filename,
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # حفظ في قاعدة البيانات
        db = load_db()
        
        # إضافة للمستخدم
        if user_id not in db["users"]:
            db["users"][user_id] = {
                "username": username,
                "first_seen": datetime.now().isoformat(),
                "result_count": 0
            }
        
        db["users"][user_id]["result_count"] = db["users"][user_id].get("result_count", 0) + 1
        
        # إضافة للنتائج العامة
        db["results"].append(result_data)
        
        # حفظ فقط آخر 1000 نتيجة
        if len(db["results"]) > 1000:
            db["results"] = db["results"][-1000:]
        
        save_db(db)
        
        # إرسال للبوت التليجرام
        telegram_sent = send_to_telegram_bot(user_id, username, celebrity, match_percentage, personality, result_id)
        
        return jsonify({
            "success": True,
            "message": "Result saved successfully",
            "result_id": result_id,
            "image_saved": image_filename is not None,
            "telegram_sent": telegram_sent,
            "data": {
                "celebrity": celebrity,
                "match": match_percentage,
                "personality": personality,
                "timestamp": result_data["date"]
            }
        })
        
    except Exception as e:
        print(f"❌ Error in save_result: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

def send_to_telegram_bot(user_id, username, celebrity, match_percentage, personality, result_id):
    """إرسال النتيجة للبوت التليجرام"""
    try:
        # تحضير الرسالة
        message = f"""
🎊 *New FaceMatch Pro Result!*

👤 *User:* {username}
🌟 *Celebrity:* {celebrity}
📊 *Match:* {match_percentage}%
😊 *Personality:* {personality}
🆔 *Result ID:* {result_id}

📅 *Date:* {datetime.now().strftime("%Y-%m-%d %H:%M")}
🔗 *Website:* {WEBSITE_URL}?tgid={user_id}

✅ Result saved successfully!
"""
        
        # إرسال الرسالة
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": user_id,
            "text": message,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }
        
        response = requests.post(url, json=payload, timeout=10)
        result = response.json()
        
        if result.get("ok"):
            print(f"✅ Telegram message sent to {user_id}")
            return True
        else:
            print(f"⚠️ Telegram error: {result.get('description')}")
            return False
            
    except Exception as e:
        print(f"❌ Telegram sending error: {e}")
        return False

@app.route('/api/get-user-results/<user_id>', methods=['GET'])
def get_user_results(user_id):
    """الحصول على نتائج مستخدم معين"""
    try:
        db = load_db()
        
        user_results = [
            r for r in db["results"] 
            if r["user_id"] == str(user_id)
        ]
        
        # ترتيب من الأحدث للأقدم
        user_results.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return jsonify({
            "success": True,
            "user_id": user_id,
            "username": db["users"].get(user_id, {}).get("username", "Unknown"),
            "total_results": len(user_results),
            "results": user_results[:20]  # آخر 20 نتيجة فقط
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """لوحة المتصدرين"""
    try:
        db = load_db()
        
        # حساب النقاط لكل مستخدم
        user_stats = {}
        for result in db["results"]:
            user_id = result["user_id"]
            if user_id not in user_stats:
                user_stats[user_id] = {
                    "username": db["users"].get(user_id, {}).get("username", "Unknown"),
                    "total_matches": 0,
                    "total_points": 0,
                    "best_match": 0
                }
            
            user_stats[user_id]["total_matches"] += 1
            user_stats[user_id]["total_points"] += 10
            
            match_score = result.get("match", 0)
            if match_score > user_stats[user_id]["best_match"]:
                user_stats[user_id]["best_match"] = match_score
        
        # تحويل للقائمة وترتيب حسب النقاط
        leaderboard = [
            {
                "user_id": uid,
                "username": stats["username"],
                "total_matches": stats["total_matches"],
                "total_points": stats["total_points"],
                "best_match": stats["best_match"]
            }
            for uid, stats in user_stats.items()
        ]
        
        leaderboard.sort(key=lambda x: x["total_points"], reverse=True)
        
        return jsonify({
            "success": True,
            "total_users": len(user_stats),
            "total_results": len(db["results"]),
            "leaderboard": leaderboard[:50],
            "updated": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/uploads/<filename>', methods=['GET'])
def get_uploaded_file(filename):
    """خدمة الصور المحفوظة"""
    try:
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(filepath):
            return send_file(filepath, mimetype='image/jpeg')
        else:
            return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """إحصائيات عامة"""
    db = load_db()
    
    return jsonify({
        "success": True,
        "stats": {
            "total_users": len(db["users"]),
            "total_results": len(db["results"]),
            "latest_result": db["results"][-1] if db["results"] else None,
            "server_time": datetime.now().isoformat()
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 FaceMatch Pro API Server starting on port {port}")
    print(f"🌐 Website: {WEBSITE_URL}")
    print(f"🤖 Bot Token: {BOT_TOKEN[:10]}...")
    app.run(host='0.0.0.0', port=port, debug=False)
