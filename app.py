import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
from openai import OpenAI

app = Flask(__name__)
app.secret_key = 'aeriya2001'

client = OpenAI(
  client = OpenAI(
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)
)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_db():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT DEFAULT '',
            avatar TEXT DEFAULT ''
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS addresses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            postal_code TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()


init_db()


# ─── محصولات با رنگ‌های بهتر (تم مشکی / سفید / صورتی) ───
ALL_PRODUCTS = [
    {  
        "id": 1,
        "name": "آیفون ۱۶ پرو مکس اپل مدل iPhone 16 Pro Max ZAA",
        "specs": "",
        "rating": 4.5,
        "rating_count": 120,
        "price": "345,000,000",
        "old_price": None,
        "discount": None,
        "category": "mobile",
        "images": [
            "/static/images/گوشی_موبایل_اپل_مدل_iPhone_16_Pro_Max_ZAA-removebg-preview.png",
            "/static/images/آیفون_۱۶_پرو_ل_iPhone_16_Pro_Max_ZAA-removebg-preview.png",
            "/static/images/آیفون_۱۶_پرو_مکس_اپل_مدل_iPhone_16_Pro_Max_ZAA_1_-removebg-preview.png",
            "/static/images/آیفون_۱۶_پرو_مکس_اپل_مدل_iPhone_16_Pro_Max_ZAA-removebg-preview.png"
        ],
        "colors": [
            {"name": "مشکی تیتانیوم", "hex": "#1c1c1e"},
            {"name": "سفید تیتانیوم", "hex": "#f5f5f7"},
            {"name": "صورتی طبیعی", "hex": "#e8b4b8"},
            {"name": "صحرایی", "hex": "#c4a77d"}
        ]
    },
    {
        "id": 2,
        "name": "ساعت هوشمند اپل مدل Ultra 3",
        "specs": "",
        "rating": 4.5,
        "rating_count": 120,
        "price": "38,000,000",
        "old_price": None,
        "discount": None,
        "category": "watch",
        "images": [
            "/static/images/ساعت_هوشمند_اپل_مدل_Ultra_3-removebg-preview.png",  # عکس اول
            "/static/images/ultra3 (1).png",  # عکس دوم
            "/static/images/ultra3 (3).png",  # عکس سوم
        ],
        "colors": [
            {"name": "مشکی", "hex": "#1a1a1a"},
            {"name": "نقره‌ای", "hex": "#c0c0c0"},
            {"name": "رزگلد", "hex": "#b76e79"}
        ]
    },
    {
        "id": 3,
        "name": "هدفون بلوتوثی اپل مدل AirPods 4",
        "specs": "",
        "rating": 4.5,
        "rating_count": 120,
        "price": "29,500,000",
        "old_price": None,
        "discount": None,
        "category": "audio",
        "images": [
            "/static/images/هدفون_بلوتوثی_اپل_مدل_AirPods_4_-removebg-preview.png",  # عکس اول
            "/static/images/air1.png",  # عکس دوم
            "/static/images/air2.png",  # عکس سوم
            "/static/air3.png"
        ],
        "colors": [
            {"name": "مشکی", "hex": "#1a1a1a"},
            {"name": "سفید", "hex": "#f5f5f5"}
        ]
    },
    {
        "id": 4,
        "name": "لپ تاپ مدل MacBook Pro 2025",
        "specs": "",
        "rating": 4.5,
        "rating_count": 120,
        "price": "481,000,000",
        "old_price": None,
        "discount": None,
        "category": "laptop",
        "images": [
            "/static/images/MacBook_Air_MDHK4_2026-removebg-preview.png",  # عکس اول
            "/static/images/mac1.png",  # عکس دوم
            "/static/images/mac2.png",
              "/static/images/mac3.png"  # عکس سوم
        ],
        "colors": [
            {"name": "نقره‌ای", "hex": "#c0c0c0"},
            {"name": "خاکستری فضایی", "hex": "#4b4b4b"}
        ]
    },
    {
        "id": 5,
        "name": "شارژر بی سیم مدل مگ سیف 7",
        "specs": "",
        "rating": 4.5,
        "rating_count": 120,
        "price": "12,000,000",
        "old_price": None,
        "discount": None,
        "category": "accessory",
        "images": [
            "/static/images/داک_شارژر_بی_سیم_مدل_مگ_سیف_A37-removebg-preview.png",  # عکس اول
            "/static/images/magsafe-7-2.png",  # عکس دوم
            "/static/images/magsafe-7-3.png",  # عکس سوم
        ],
        "colors": [
            {"name": "مشکی", "hex": "#1a1a1a"},
            {"name": "سفید", "hex": "#f5f5f5"}
        ]
    },
    {
        "id": 6,
        "name": "دوربین سونی A۷ IV",
        "specs": "",
        "rating": 4.5,
        "rating_count": 120,
        "price": "335,000,000",
        "old_price": None,
        "discount": None,
        "category": "camera",
        "images": [
            "/static/images/دوربین_سونی_A۷_IV-removebg-preview.png",  # عکس اول
            "/static/images/sony a 7.png",  # عکس دوم
            "/static/images/sony7a2.png",  # عکس سوم
        ],
        "colors": [{"name": "مشکی", "hex": "#1a1a1a"}]
    },
    {
        "id": 7,
        "name": "داک شارژر بی سیم مدل مگ سیف A60",
        "specs": "",
        "rating": 4.5,
        "rating_count": 120,
        "price": "12,800,000",
        "old_price": None,
        "discount": None,
        "category": "accessory",
        "images": [
            "/static/images/داک_شارژر_بی_سیم_مدل_مگ_سیف_A60-removebg-preview.png",  # عکس اول
            "/static/images/magsafe-a60-2.png",  # عکس دوم
            "/static/images/magsafe-a60-3.png",  # عکس سوم
        ],
        "colors": [
            {"name": "مشکی", "hex": "#1a1a1a"},
            {"name": "سفید", "hex": "#f5f5f5"}
        ]
    },
    {
        "id": 8,
        "name": "هدفون سونی WH-1000XM5",
        "specs": "",
        "rating": 4.5,
        "rating_count": 120,
        "price": "18,500,000",
        "old_price": None,
        "discount": None,
        "category": "audio",
        "images": [
            "/static/images/headphone.png",  # عکس اول
            "/static/images/headsony (1).png",  # عکس دوم
            "/static/images/headsony (2).png",  # عکس سوم
        ],
        "colors": [
            {"name": "مشکی", "hex": "#1a1a1a"},
            {"name": "نقره‌ای", "hex": "#c0c0c0"}
        ]
    },
    {
        "id": 9,
        "name": "گلکسی واچ ۷",
        "specs": "",
        "rating": 4.5,
        "rating_count": 120,
        "price": "22,000,000",
        "old_price": None,
        "discount": None,
        "category": "watch",
        "images": [
            "/static/images/watch.png",  # عکس اول
            "/static/images/ultra3 (2).png",  # عکس دوم
             # عکس سوم
        ],
        "colors": [
            {"name": "مشکی", "hex": "#1a1a1a"},
            {"name": "صورتی", "hex": "#e8a5c4"}
        ]
    },
    {
        "id": 10,
        "name": "گوشی موبایل سامسونگ مدل Galaxy S25 FE",
        "specs": "",
        "rating": 4.5,
        "rating_count": 120,
        "price": "125,000,000",
        "old_price": None,
        "discount": None,
        "category": "mobile",
        "images": [
            "/static/images/galaxys25-removebg-preview.png",  # عکس اول
            "/static/images/s25 (3).png",  # عکس دوم
            "/static/images/s25fe1-removebg-preview.png",  # عکس سوم
        ],
        "colors": [
            {"name": "مشکی", "hex": "#1c1c1e"},
            {"name": "سفید", "hex": "#f5f5f7"},
            {"name": "صورتی", "hex": "#f2c4d0"}
        ]
    },
    {
        "id": 11,
        "name": "گوشی موبایل سامسونگ مدل Galaxy A26",
        "specs": "",
        "rating": 4.5,
        "rating_count": 120,
        "price": "44,000,000",
        "old_price": None,
        "discount": None,
        "category": "mobile",
        "images": [
            "/static/images/گوشی_موبایل_سامسونگ_مدل_Galaxy_A26-removebg-preview.png",  # عکس اول
            "/static/images/26a1 (1).png",  # عکس دوم
            "/static/images/26a6.png",  # عکس سوم
        ],
        "colors": [
            {"name": "مشکی", "hex": "#1a1a1a"},
            {"name": "سفید", "hex": "#f5f5f5"},
            {"name": "صورتی", "hex": "#e8a5c4"}
        ]
    },
    {
        "id": 12,
        "name": "آیفون ۱۶ گوشی موبایل اپل مدل iPhone 16 CH",
        "specs": "",
        "rating": 4.5,
        "rating_count": 120,
        "price": "222,000,000",
        "old_price": None,
        "discount": None,
        "category": "mobile",
        "images": [
            "/static/images/گوشی_موبایل_اپل_مدل_iPhone_16_CH-removebg-preview.png",  # عکس اول
            "/static/images/16i1.png",  # عکس دوم
            "/static/images/16i3.png",  # عکس سوم
        ],
        "colors": [
            {"name": "مشکی", "hex": "#1c1c1e"},
            {"name": "سفید", "hex": "#f5f5f7"},
            {"name": "صورتی", "hex": "#f2c4d0"},
            {"name": "آبی روشن", "hex": "#a8c5da"}
        ]
    },
    {
        "id": 13,
        "name": "ساعت هوشمند شیائومی مدل Redmi Watch 5 Lite",
        "specs": "",
        "rating": 4.5,
        "rating_count": 120,
        "price": "3,800,000",
        "old_price": None,
        "discount": None,
        "category": "watch",
        "images": [
            "/static/images/ئومی_Redmi_Watch_5_Lite_-.png",  # عکس اول
            "/static/images/redmi5 (2).png",  # عکس دوم
            "/static/images/redmi5 (1).png",  # عکس سوم
        ],
        "colors": [
            {"name": "مشکی", "hex": "#1a1a1a"},
            {"name": "نقره‌ای", "hex": "#c0c0c0"},
            {"name": "رزگلد", "hex": "#b76e79"}
        ]
    },
    {
        "id": 14,
        "name": "ساعت هوشمند هایلو مدل Solar Lite",
        "specs": "",
        "rating": 4.5,
        "rating_count": 120,
        "price": "1,600,000",
        "old_price": None,
        "discount": None,
        "category": "watch",
        "images": [
            "/static/images/__Solar_Lite--.png",  # عکس اول
            "/static/images/هایلو (1).pngg",  # عکس دوم
            "/static/images/هایلو (2).png",  # عکس سوم
        ],
        "colors": [
            {"name": "مشکی", "hex": "#1a1a1a"},
            {"name": "صورتی", "hex": "#e8a5c4"}
        ]
    },
    {
        "id": 15,
        "name": "ساعت هوشمند مدل C39 Pro MAX",
        "specs": "",
        "rating": 4.5,
        "rating_count": 120,
        "price": "1,950,000",
        "old_price": None,
        "discount": None,
        "category": "watch",
        "images": [
            "/static/images/C39_Pro_MAX-removebg-preview.png",  # عکس اول
            "/static/images/c39 (1).png",  # عکس دوم
            "/static/images/c39 (2).png",  # عکس سوم
        ],
        "colors": [
            {"name": "مشکی", "hex": "#1a1a1a"},
            {"name": "نقره‌ای", "hex": "#c0c0c0"},
            {"name": "رزگلد", "hex": "#b76e79"}
        ]
    },
    {
        "id": 16,
        "name": "ساعت هوشمند 47 میلی متری فنیرسی مدل S370i",
        "specs": "",
        "rating": 4.5,
        "rating_count": 120,
        "price": "1,450,000",
        "old_price": None,
        "discount": None,
        "category": "watch",
        "images": [
            "/static/images/s370فنیرسی-removebg-preview.png",  # عکس اول
            "/static/images/s37 (1).png",  # عکس دوم
            
        ],
        "colors": [
            {"name": "مشکی", "hex": "#1a1a1a"},
            {"name": "صورتی", "hex": "#e8a5c4"}
        ]
    },
    {
        "id": 17,
        "name": "ساعت هوشمند 46 میلی متری مدل WS40 MAX",
        "specs": "",
        "rating": 4.5,
        "rating_count": 120,
        "price": "1,250,000",
        "old_price": None,
        "discount": None,
        "category": "watch",
        "images": [
            "/static/images/WS40_MAX-removebg-preview.png",  # عکس اول
            "/static/images/ws40-max-2.png",  # عکس دوم
            "/static/images/ws40-max-3.png",  # عکس سوم
        ],
        "colors": [
            {"name": "مشکی", "hex": "#1a1a1a"},
            {"name": "نقره‌ای", "hex": "#c0c0c0"},
            {"name": "رزگلد", "hex": "#b76e79"}
        ]
    },
    {
        "id": 18,
        "name": "گوشی موبایل اپل مدل iPhone 17 Pro Max ZAA",
        "specs": "",
        "rating": 4.5,
        "rating_count": 120,
        "price": "290,000,000",
        "old_price": None,
        "discount": None,
        "category": "mobile",
        "images": [
            "/static/images/iPhone_17_Pro_Max_ZAA-removebg-preview.png",  # عکس اول
            "/static/images/17oro3.png",  # عکس دوم
            "/static/images/17pro4.pngg",  # عکس سوم
        ],
        "colors": [
            {"name": "مشکی تیتانیوم", "hex": "#1c1c1e"},
            {"name": "سفید", "hex": "#f5f5f7"},
            {"name": "صورتی", "hex": "#f2c4d0"}
        ]
    },
    {
        "id": 19,
        "name": "گوشی موبایل سامسونگ مدل Galaxy S26 Ultra",
        "specs": "",
        "rating": 4.5,
        "rating_count": 120,
        "price": "319,999,000",
        "old_price": None,
        "discount": None,
        "category": "mobile",
        "images": [
            "/static/images/Galaxy_S26_Ultra_-removebg-preview.png",  # عکس اول
            "/static/images/26s3.png",  # عکس دوم
            "/static/images/26s4.png",  # عکس سوم
        ],
        "colors": [
            {"name": "مشکی", "hex": "#1c1c1e"},
            {"name": "سفید", "hex": "#f5f5f7"},
            {"name": "صورتی", "hex": "#e8a5c4"}
        ]
    },
    {
        "id": 20,
        "name": "گوشی موبایل موتورولا مدل Edge 60 Fusion",
        "specs": "",
        "rating": 4.5,
        "rating_count": 120,
        "price": "37,700,000",
        "old_price": None,
        "discount": None,
        "category": "mobile",
        "images": [
            "/static/images/Edge_60_Fusion-removebg-preview.png",  # عکس اول
            "/static/images/motor2.png",  # عکس دوم
            "/static/images/motor.png",
              "/static/images/motor1.png"  # عکس سوم
        ],
        "colors": [
            {"name": "مشکی", "hex": "#1a1a1a"},
            {"name": "سفید", "hex": "#f5f5f5"},
            {"name": "صورتی", "hex": "#e8a5c4"}
        ]
    },
    {
        "id": 22,
        "name": "گوشی موبایل سامسونگ مدل Galaxy A57",
        "specs": "",
        "rating": 4.5,
        "rating_count": 120,
        "price": "42,000,000",
        "old_price": None,
        "discount": None,
        "category": "mobile",
        "images": [
            "/static/images/Galaxy_A57-removebg-preview.png",  # عکس اول
            "/static/images/57a2.png",  # عکس دوم
            "/static/images/57a1.png",  # عکس سوم
        ],
        "colors": [
            {"name": "مشکی", "hex": "#1a1a1a"},
            {"name": "سفید", "hex": "#f5f5f5"},
            {"name": "صورتی", "hex": "#f2c4d0"}
        ]
    },
    {
        "id": 23,
        "name": "گوشی موبایل اپل مدل iPhone 14 CH",
        "specs": "",
        "rating": 4.5,
        "rating_count": 120,
        "price": "48,000,000",
        "old_price": None,
        "discount": None,
        "category": "mobile",
        "images": [
            "/static/images/iPhone_14_CH_-removebg-preview.png",  # عکس اول
            "/static/images/14m.png",  # عکس دوم
            "/static/images/14mn.png",  # عکس سوم
        ],
        "colors": [
            {"name": "مشکی", "hex": "#1c1c1e"},
            {"name": "سفید", "hex": "#f5f5f7"},
            {"name": "صورتی", "hex": "#e8a5c4"}
        ]
    },
    {
        "id": 24,
        "name": "گوشی موبایل سامسونگ مدل Galaxy A16 4G",
        "specs": "",
        "rating": 4.5,
        "rating_count": 120,
        "price": "14,500,000",
        "old_price": None,
        "discount": None,
        "category": "mobile",
        "images": [
            "/static/images/16a2.png",  # عکس اول
            "/static/images/a16-removebg-preview.png",  # عکس دوم
            "/static/images/16a1.png",  # عکس سوم
        ],
        "colors": [
            {"name": "مشکی", "hex": "#1a1a1a"},
            {"name": "سفید", "hex": "#f5f5f5"},
            {"name": "صورتی", "hex": "#e8a5c4"}
        ]
    },
    {
        "id": 25,
        "name": "هدفون بی سیم بلوتوث مدل P47-5.0+EDR",
        "specs": "",
        "rating": 4.5,
        "rating_count": 120,
        "price": "1,850,000",
        "old_price": None,
        "discount": None,
        "category": "audio",
        "images": [
            "/static/images/هدفون_بلوتوثی_مدل_P47_EDR_-removebg-preview.png",  # عکس اول
            "/static/images/P47-5.0+EDR-removebg-preview.png",  # عکس دوم
            "/static/images/1P47-5.0+EDR-removebg-preview.png",  # عکس سوم
        ],
        "colors": [
            {"name": "مشکی", "hex": "#1a1a1a"},
            {"name": "سفید", "hex": "#f5f5f5"}
        ]
    },
    {
        "id": 26,
        "name": "هدست بلوتوثی مدل P9",
        "specs": "",
        "rating": 4.5,
        "rating_count": 120,
        "price": "1,650,000",
        "old_price": None,
        "discount": None,
        "category": "audio",
        "images": [
            "/static/images/هدست_بلوتوثی_مدل_p9-removebg-preview.png",  # عکس اول
            "/static/images/p93-removebg-preview.png",  # عکس دوم
            "/static/images/p9-removebg-preview.png",  # عکس سوم
        ],
        "colors": [
            {"name": "مشکی", "hex": "#1a1a1a"},
            {"name": "صورتی", "hex": "#e8a5c4"}
        ]
    },
    {
        "id": 27,
        "name": "هدفون بی سیم بی اچ جی بی ال مدل VJ083",
        "specs": "",
        "rating": 4.5,
        "rating_count": 120,
        "price": "1,450,000",
        "old_price": None,
        "discount": None,
        "category": "audio",
        "images": [
            "/static/images/هدفون_بی_سیم_بی_اچ_جی_بی_ال_مدل_VJ083-removebg-preview.png",  # عکس اول
            "/static/images/هدفون_VJ083-removebg-preview.png",  # عکس دوم
            "/static/images/بی_اچ_جی_بی_ال_مدل_VJ083-removebg-preview.png",  # عکس سوم
        ],
        "colors": [
            {"name": "مشکی", "hex": "#1a1a1a"},
            {"name": "سفید", "hex": "#f5f5f5"}
        ]
    },
    {
        "id": 28,
        "name": "هدفون بلوتوثی مدل J-30",
        "specs": "",
        "rating": 4.5,
        "rating_count": 120,
        "price": "1,195,000",
        "old_price": None,
        "discount": None,
        "category": "audio",
        "images": [
            "/static/images/هدفون_بلوتوثی_مدل_J-30-removebg-preview.png",  # عکس اول
            "/static/images/هدفون_بلوتوثی_مدل_J-30-removebg-preview.png",  # عکس دوم
            "/static/images/هدفون_بلوتوثی_مدل_J-301-removebg-preview.png",  # عکس سوم
        ],
        "colors": [
            {"name": "مشکی", "hex": "#1a1a1a"},
            {"name": "صورتی", "hex": "#e8a5c4"}
        ]
    },
    {
        "id": 29,
        "name": "تبلت 11.2 اینچ شیائومی مدل Pad 7 Wi-Fi",
        "specs": "",
        "rating": 4.5,
        "rating_count": 120,
        "price": "19,500,000",
        "old_price": None,
        "discount": None,
        "category": "tablet",
        "images": [
            "/static/images/Pad_7_Wi-Fi-removebg-preview.png",  # عکس اول
            "/static/images/pad7.png",  # عکس دوم
           
        ],
        "colors": [
            {"name": "نقره‌ای", "hex": "#c0c0c0"},
            {"name": "خاکستری فضایی", "hex": "#4b4b4b"}
        ]
    },
    {
        "id": 30,
        "name": "تبلت 12.1 اینچ شیائومی مدل Poco Pad M1 Wi-Fi",
        "specs": "",
        "rating": 4.5,
        "rating_count": 120,
        "price": "16,800,000",
        "old_price": None,
        "discount": None,
        "category": "tablet",
        "images": [
            "/static/images/Poco_Pad_M1_Wi-Fi_-removebg-preview.png",  # عکس اول
            "/static/images/تبلت_12.1_اینچ_شیائومی_مدل_Poco_Pad_M1_Wi-Fi-removebg-preview.png",  # عکس دوم
            "/static/images/تبلت_12.1_اینچ_شیائومی_مدل1_Poco_Pad_M1_Wi-Fi-removebg-preview.png",  # عکس سوم
        ],
        "colors": [
            {"name": "نقره‌ای", "hex": "#c0c0c0"},
            {"name": "خاکستری فضایی", "hex": "#4b4b4b"}
        ]
    },
    {
        "id": 31,
        "name": "تبلت ۱۱ اینچ اپل مدل iPad Pro 2025 M5 Wi-Fi",
        "specs": "",
        "rating": 4.5,
        "rating_count": 120,
        "price": "85,000,000",
        "old_price": None,
        "discount": None,
        "category": "tablet",
        "images": [
            "/static/images/IPad_Pro_2025_M5_Wi-Fi-removebg-preview.png",  # عکس اول
            "/static/images/6be5a1a1f33770e602bceeb23e929e69-removebg-preview.png",  # عکس دوم
            "/static/images/eefda953199a5a1be08a6fb06edce406-removebg-preview.png",  # عکس سوم
        ],
        "colors": [
            {"name": "نقره‌ای", "hex": "#c0c0c0"},
            {"name": "خاکستری فضایی", "hex": "#4b4b4b"}
        ]
    },
    {
        "id": 32,
        "name": "تبلت 8.3 اینچی اپل مدل iPad Mini 7th Generation",
        "specs": "",
        "rating": 4.5,
        "rating_count": 120,
        "price": "38,000,000",
        "old_price": None,
        "discount": None,
        "category": "tablet",
        "images": [
            "/static/images/iPad_Mini_7th_Generation_2024_Wi-Fi_-removebg-preview.png",  # عکس اول
            "/static/images/f5d5af3d0f72411ed0e54f0f353159a9-removebg-preview.png",  # عکس دوم
            "/static/images/mini.png",  # عکس سوم
        ],
        "colors": [
            {"name": "نقره‌ای", "hex": "#c0c0c0"},
            {"name": "خاکستری فضایی", "hex": "#4b4b4b"},
            {"name": "صورتی", "hex": "#e8a5c4"}
        ]
    },
    {
        "id": 33,
        "name": "لپ تاپ لنوو مدل IdeaPad 1 15IJL7 با پردازنده Celeron N4500",
        "specs": "",
        "rating": 4.5,
        "rating_count": 120,
        "price": "39,500,000",
        "old_price": None,
        "discount": None,
        "category": "laptop",
        "images": [
            "/static/images/IdeaPad_Slim_3_15IRU8-removebg-preview.png",  # عکس اول
            "/static/images/لپ_تاپ_لنوو_مدل_IdeaPad_1_15IJL7_با_پردازنده_Celeron_N4500-removebg-preview.png",  # عکس دوم
            "/static/images/لپدل_IdeaPad_1_15IJL7_با_پردازنده_Celeron_N4500-removebg-preview.png",  # عکس سوم
        ],
        "colors": [
            {"name": "نقره‌ای", "hex": "#c0c0c0"},
            {"name": "خاکستری فضایی", "hex": "#4b4b4b"}
        ]
    },
    {
        "id": 34,
        "name": "لپ تاپ 16 اینچی ایسوس مدل TUF Gaming F16 FX608JMR-F16I75060-i7",
        "specs": "",
        "rating": 4.5,
        "rating_count": 120,
        "price": "313,000,000",
        "old_price": None,
        "discount": None,
        "category": "laptop",
        "images": [
            "/static/images/لپ_تاپ_16_اینچی_ایسوس_مدل-removebg-preview.png",  # عکس اول
            "/static/images/لپ_تاپ_1دل_TUF_Gaming_F16_FX608JMR-F16I75060-i7-removebg-preview.png",  # عکس دوم
            "/static/images/لپ_تاپ_16_اینچی_ایسوس_مدل_TUF_Gaming_F16_FX608JMR-F16I75060-i7-removebg-preview.png",  # عکس سوم
        ],
        "colors": [
            {"name": "نقره‌ای", "hex": "#c0c0c0"},
            {"name": "خاکستری فضایی", "hex": "#4b4b4b"}
        ]
    },
    {
        "id": 35,
        "name": "لپ‌تاپ 15.6 اینچی لنوو مدل LOQ Essential 15IRX11-i5 13450HX-RTX5050",
        "specs": "",
        "rating": 4.5,
        "rating_count": 120,
        "price": "95,000,000",
        "old_price": None,
        "discount": None,
        "category": "laptop",
        "images": [
            "/static/images/lenovo loq 16 inch.png",  # عکس اول
            "/static/images/لپ_تاپ_15.6_اینچی_لنوو_مدل_LOQ_Essential_15IRX11-i5_13450HX-RTX5050-removebg-preview.png",  # عکس دوم
            "/static/images/لنوو_LOQ_Essential_15IRX11-i5_13450HX-RTX50505-removebg-preview.png",  # عکس سوم
        ],
        "colors": [
            {"name": "نقره‌ای", "hex": "#c0c0c0"},
            {"name": "خاکستری فضایی", "hex": "#4b4b4b"}
        ]
    },
    {
        "id": 36,
        "name": "دوربین عکاسی DSLR کانن مدل EOS 2000D",
        "specs": "",
        "rating": 4.5,
        "rating_count": 120,
        "price": "28,000,000",
        "old_price": None,
        "discount": None,
        "category": "camera",
        "images": [
            "/static/images/وربین_عکاسی_DSLR_کانن_مدل_EOS_2000D-removebg-preview.png",  # عکس اول
            "/static/images/عکاسی_DSLR_کانن_مدل_EOS_2000D-removebg-preview.png",  # عکس دوم
            "/static/images/دوربین_عکاسی_DSLR_کانن_مدل_EOS_2000D-removebg-preview.png",  # عکس سوم
        ],
        "colors": [{"name": "مشکی", "hex": "#1a1a1a"}]
    },
    {
        "id": 37,
        "name": "دوربین عکاسی DSLR کانن EOS 250D",
        "specs": "",
        "rating": 4.5,
        "rating_count": 120,
        "price": "119,000,000",
        "old_price": None,
        "discount": None,
        "category": "camera",
        "images": [
            "/static/images/دوربین_عکاسی_DSLR_کانن_EOS_250D-removebg-preview.png",  # عکس اول
            "/static/images/250d__1_-removebg-preview.png",  # عکس دوم
            "/static/images/دوربین_عکاسی_DSLR_کانن_EOS_250D-removebg-preview.png",  # عکس سوم
        ],
        "colors": [{"name": "مشکی", "hex": "#1a1a1a"}]
    },
    {
        "id": 38,
        "name": "دوربین دیجیتال کامپکت سامسونگ مدل ST69",
        "specs": "",
        "rating": 4.5,
        "rating_count": 120,
        "price": "54,500,000",
        "old_price": None,
        "discount": None,
        "category": "camera",
        "images": [
            "/static/images/وربین_دیجیتال_کامپکت_سامسونگ_مدل_ST69-removebg-preview.png",  # عکس اول
            "/static/images/دوربین_دیجیتال_کامپکت_سامسونگ_مدل_ST691_-removebg-preview.png",  # عکس دوم
            "/static/images/دوربین_دیجیتال_کامپکت_سامسونگ_مدل_ST69-removebg-preview.png",  # عکس سوم
        ],
        "colors": [{"name": "مشکی", "hex": "#1a1a1a"}]
    },
]


@app.route('/')
def index():
    return render_template('index.html', products=ALL_PRODUCTS)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form.get('fullname', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        password2 = request.form.get('password2', '')

        if not fullname or not phone or not password:
            return render_template('register.html', error='لطفاً همه فیلدها را پر کنید')

        if password != password2:
            return render_template('register.html', error='رمز عبور و تکرار آن یکسان نیستند')

        if len(password) < 6:
            return render_template('register.html', error='رمز عبور باید حداقل ۶ کاراکتر باشد')

        hashed_password = generate_password_hash(password)

        conn = get_db()
        try:
            # نکته: ستون «email» در دیتابیس همان شناسه یکتای کاربر است؛
            # چون کل سایت با شماره موبایل کار می‌کند، همان مقدار داخل این ستون ذخیره می‌شود.
            conn.execute(
                'INSERT INTO users (email, password, name) VALUES (?, ?, ?)',
                (phone, hashed_password, fullname)
            )
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            conn.close()
            return render_template('register.html', error='این شماره موبایل قبلاً ثبت شده است')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')

        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (phone,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_email'] = user['email']
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='شماره موبایل یا رمز عبور اشتباه است')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/account')
def account():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    user_row = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    addresses_rows = conn.execute('SELECT * FROM addresses WHERE user_id = ?', (session['user_id'],)).fetchall()
    conn.close()

    user = {
        'email': user_row['email'],
        'name': user_row['name'],
        'avatar': user_row['avatar'],
        'addresses': [dict(a) for a in addresses_rows]
    }

    message = session.pop('message', None)
    return render_template('account.html', user=user, message=message)


@app.route('/account/update-name', methods=['POST'])
def update_name():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    name = request.form.get('name', '')
    conn = get_db()
    conn.execute('UPDATE users SET name = ? WHERE id = ?', (name, session['user_id']))
    conn.commit()
    conn.close()

    session['message'] = 'نام با موفقیت به‌روزرسانی شد'
    return redirect(url_for('account'))


@app.route('/account/update-avatar', methods=['POST'])
def update_avatar():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    file = request.files.get('avatar')

    if not file or file.filename == '':
        session['message'] = 'فایلی انتخاب نشده است'
        return redirect(url_for('account'))

    if not allowed_file(file.filename):
        session['message'] = 'فرمت فایل مجاز نیست. فقط عکس (png, jpg, jpeg, webp, gif)'
        return redirect(url_for('account'))

    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = secure_filename(f"user_{session['user_id']}_{uuid.uuid4().hex}.{ext}")

    file.save(os.path.join(UPLOAD_FOLDER, filename))

    conn = get_db()

    old_row = conn.execute('SELECT avatar FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    if old_row and old_row['avatar']:
        old_path = os.path.join(UPLOAD_FOLDER, old_row['avatar'])
        if os.path.exists(old_path):
            os.remove(old_path)

    conn.execute('UPDATE users SET avatar = ? WHERE id = ?', (filename, session['user_id']))
    conn.commit()
    conn.close()

    session['message'] = 'عکس پروفایل با موفقیت آپدیت شد'
    return redirect(url_for('account'))


@app.route('/account/addresses/add', methods=['POST'])
def add_address():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    title = request.form.get('title')
    phone = request.form.get('phone')
    address = request.form.get('address')
    postal_code = request.form.get('postal_code')

    conn = get_db()
    conn.execute(
        'INSERT INTO addresses (user_id, title, phone, address, postal_code) VALUES (?, ?, ?, ?, ?)',
        (session['user_id'], title, phone, address, postal_code)
    )
    conn.commit()
    conn.close()

    session['message'] = 'آدرس با موفقیت ثبت شد'
    return redirect(url_for('account'))


@app.route('/account/addresses/delete/<int:addr_id>', methods=['POST'])
def delete_address(addr_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    conn.execute('DELETE FROM addresses WHERE id = ? AND user_id = ?', (addr_id, session['user_id']))
    conn.commit()
    conn.close()

    session['message'] = 'آدرس حذف شد'
    return redirect(url_for('account'))


@app.route('/cart')
def cart():
    return render_template('cart.html')


@app.route('/payment-redirect')
def payment_redirect():
    return render_template('payment-redirect.html')


@app.route('/payment-result')
def payment_result():
    return render_template('payment-result.html')


@app.route('/category/mobile')
def category_mobile():
    mobile_products = [p for p in ALL_PRODUCTS if p['category'] == 'mobile']
    return render_template('category_mobile.html', products=mobile_products)


@app.route('/api/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')

    products_summary = "\n".join([
        f"- {p['name']} | دسته: {p['category']} | قیمت: {p['price']} تومان (id: {p['id']})"
        for p in ALL_PRODUCTS
    ])

    prompt = f"""تو دستیار فروش فروشگاه Smart Store هستی. فقط از بین محصولات زیر پیشنهاد بده، هیچ محصول دیگه‌ای رو معرفی نکن:

{products_summary}

با توجه به بودجه و نیاز کاربر، بهترین محصول (یا محصولات) رو با نام دقیق و قیمت پیشنهاد بده. کوتاه و مفید جواب بده.

پیام کاربر: {user_message}"""

    response = client.chat.completions.create(
        model="google/gemini-2.5-flash",
        max_tokens=800,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return {
        "reply": response.choices[0].message.content
    }


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = next((p for p in ALL_PRODUCTS if p['id'] == product_id), None)

    if not product:
        return "محصول پیدا نشد", 404

    return render_template('product.html', product=product)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)