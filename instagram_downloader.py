import instaloader
import os
import shutil

# نام کاربری اینستاگرام شما (باید با نام فایل سشن ذخیره شده تطابق داشته باشد)
INSTA_USERNAME = "aminsharbatiii"

# یک نمونه Instaloader ایجاد کنید
L = instaloader.Instaloader()

# *****************************************************************
# بارگذاری سشن برای حل مشکل "Login required"
try:
    # نام فایل سشن ذخیره شده (باید کنار این فایل قرار داشته باشد)
    session_file_name = f"session-{INSTA_USERNAME}" 
    
    # Instaloader سشن را در فایل پروژه جستجو می‌کند
    L.load_session(INSTA_USERNAME, session_file_name) 
    print(f"Instaloader session successfully loaded for {INSTA_USERNAME}.")
    
except FileNotFoundError:
    print("WARNING: Instaloader session file not found. Downloads may face 'Login required' errors.")
except Exception as e:
    print(f"An unexpected error occurred during session loading: {e}")
# *****************************************************************

def download_instagram_content(url, chat_id):
    """
    محتوای اینستاگرام را بر اساس URL دانلود می‌کند.
    :param url: لینک پست اینستاگرام.
    :param chat_id: آیدی چت برای ایجاد پوشه مجزا برای فایل‌های دانلود شده.
    :return: لیستی از مسیر فایل‌های دانلود شده.
    """
    
    # اطمینان حاصل کنید که URL یک لینک پست یا ریلز است.
    if "/p/" not in url and "/reel/" not in url and "/tv/" not in url:
        return ["لطفاً یک لینک پست، ریلز یا IGTV معتبر وارد کنید."]

    try:
        # 1. استخراج shortcode
        shortcode = url.split('/')[-2] if url.endswith('/') else url.split('/')[-1]
        
        # 2. تعریف مسیر ذخیره (برای جلوگیری از تداخل، از chat_id کاربر استفاده می‌کنیم)
        download_dir = f"downloads/{chat_id}"
        os.makedirs(download_dir, exist_ok=True)
        
        # 3. دانلود پست
        original_dirname_pattern = L.dirname_pattern
        
        # تنظیم مسیر دانلود به پوشه مشخص شده برای این کاربر
        L.dirname_pattern = download_dir + "/{shortcode}"
        
        # دانلود بر اساس shortcode
        L.download_post(instaloader.Post.from_shortcode(L.context, shortcode), shortcode)
        
        # بازیابی تنظیمات اصلی
        L.dirname_pattern = original_dirname_pattern
        
        # 4. جمع‌آوری مسیر فایل‌های دانلود شده
        post_dir = f"{download_dir}/{shortcode}"
        
        # Instaloader ممکن است فایل‌های اضافی (مانند .txt و .json) را هم دانلود کند
        downloaded_files = [os.path.join(post_dir, f) for f in os.listdir(post_dir) if os.path.isfile(os.path.join(post_dir, f))]
        
        # فیلتر کردن فایل‌های مدیا
        media_files = [f for f in downloaded_files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.mp4'))]
        
        if not media_files:
             return ["دانلود انجام شد، اما فایل مدیا (عکس یا ویدیو) در پوشه پیدا نشد. ممکن است پست خصوصی باشد یا مشکل دیگری در فایل سشن وجود داشته باشد."]
        
        return media_files

    except instaloader.exceptions.PostNotFoundError:
        return [f"متاسفانه پستی با این لینک پیدا نشد. (Post Not Found)"]
    except Exception as e:
        return [f"متاسفانه در دانلود محتوا خطایی رخ داد: {type(e).__name__}: {e}"]