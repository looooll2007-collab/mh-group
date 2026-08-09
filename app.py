import base64
import datetime
import io
import random
import sqlite3
import pandas as pd
import requests
import streamlit as st

# ==========================================
# 1. قائمة الثيمات وإعدادات الألوان (Themes)
# ==========================================
THEMES = {
    "الداكن الملكي والذهبي (Royal Dark & Gold)": {
        "primary": "#D97706",
        "bg": "#0B0F19",
        "card": "#111827",
        "text": "#F8FAFC",
        "accent": "#F59E0B",
        "border": "#1F2937",
    },
    "أزرق نيلي احترافي (Modern Indigo)": {
        "primary": "#4F46E5",
        "bg": "#F8FAFC",
        "card": "#FFFFFF",
        "text": "#1E293B",
        "accent": "#6366F1",
        "border": "#E2E8F0",
    },
}

# --- تهيئة الصفحة ---
st.set_page_config(
    page_title="MH Group ERP System",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- إعدادات الجلسات المتطورة (Session States) ---
if "login_config" not in st.session_state:
    st.session_state["login_config"] = {
        "title": "🏢 نظام إدارة MH Group ERP",
        "subtitle": "🔐 تسجيل الدخول للنظام",
        "btn_text": "تسجيل الدخول",
        "welcome_msg": "مرحباً بك! يرجى إدخال بياناتك للمتابعة.",
        "logo_bytes": None,
    }

if "dashboard_config" not in st.session_state:
    st.session_state["dashboard_config"] = {
        "header_title": "📊 لوحة التحكم المتقدمة والملخص العام",
        "show_metrics": True,
        "custom_note": "مرحباً بك، المدير العام 👋",
    }

if "selected_theme" not in st.session_state:
    st.session_state["selected_theme"] = "الداكن الملكي والذهبي (Royal Dark & Gold)"

current_theme = THEMES.get(st.session_state["selected_theme"], THEMES["الداكن الملكي والذهبي (Royal Dark & Gold)"])

# --- تطبيق CSS للمظهر العام المطابق للصورة ---
st.markdown(
    f"""
<style>
    .stApp {{
        background-color: #0B0F19 !important;
        color: #F3F4F6 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    
    /* الشريط الجانبي */
    section[data-testid="stSidebar"] {{
        background-color: #111827 !important;
        border-right: 1px solid #1F2937 !important;
    }}
    
    /* بطاقات الإحصائيات (Metrics) */
    .metric-card {{
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }}
    .metric-header {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        color: #94A3B8;
        font-size: 0.9rem;
        font-weight: 600;
    }}
    .metric-value {{
        font-size: 1.8rem;
        font-weight: 800;
        color: #FFFFFF;
        margin: 8px 0;
    }}
    .metric-sub {{
        font-size: 0.8rem;
        font-weight: 500;
    }}
    .badge-positive {{
        color: #10B981;
        background-color: rgba(16, 185, 129, 0.1);
        padding: 2px 8px;
        border-radius: 6px;
    }}
    .badge-negative {{
        color: #EF4444;
        background-color: rgba(239, 68, 68, 0.1);
        padding: 2px 8px;
        border-radius: 6px;
    }}

    /* الحاويات الرئيسية */
    .dashboard-panel {{
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }}
    
    /* الجداول والشارات */
    .status-badge {{
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: bold;
    }}
    .status-success {{ background-color: rgba(16, 185, 129, 0.2); color: #10B981; }}
    .status-warning {{ background-color: rgba(245, 158, 11, 0.2); color: #F59E0B; }}
    .status-info {{ background-color: rgba(59, 130, 246, 0.2); color: #3B82F6; }}
    
    /* الأزرار */
    .stButton>button {{
        background-color: #D97706 !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: bold !important;
    }}
</style>
""",
    unsafe_allow_html=True,
)


# ==========================================
# 2. تهيئة قاعدة البيانات والتحديث التلقائي
# ==========================================
def init_db():
    with sqlite3.connect("mh_group_erp.db") as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                role TEXT,
                phone TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS section_passwords (
                section_name TEXT PRIMARY KEY,
                password TEXT
            )
        """)

        cursor.execute("PRAGMA table_info(users)")
        u_cols = [c[1] for c in cursor.fetchall()]
        if "phone" not in u_cols:
            cursor.execute("ALTER TABLE users ADD COLUMN phone TEXT")

        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO users (username, password, role, phone) VALUES ('admin', 'admin123', 'Admin', '01000000000')"
            )

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS properties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT, 
                location TEXT, 
                price REAL, 
                status TEXT,
                type TEXT, 
                finishing TEXT,
                added_date TEXT
            )
        """)

        cursor.execute("PRAGMA table_info(properties)")
        p_cols = [c[1] for c in cursor.fetchall()]
        required_p_cols = {
            "name": "TEXT",
            "location": "TEXT",
            "price": "REAL",
            "status": "TEXT",
            "type": "TEXT",
            "finishing": "TEXT",
            "added_date": "TEXT",
        }
        for col_name, col_type in required_p_cols.items():
            if col_name not in p_cols:
                cursor.execute(
                    f"ALTER TABLE properties ADD COLUMN {col_name} {col_type}"
                )

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS property_expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_id INTEGER, expense_type TEXT, amount REAL, notes TEXT, date TEXT,
                FOREIGN KEY(property_id) REFERENCES properties(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT, emp_type TEXT, position TEXT, pay_type TEXT,
                hourly_rate REAL, hours_worked REAL, daily_rate REAL, total_pay REAL, hire_date TEXT,
                workers_count INTEGER DEFAULT 1, craft_type TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS investors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT, investment_amount REAL, return_rate REAL, start_date TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS it_tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT, category TEXT, status TEXT, created_at TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT, category TEXT, upload_date TEXT,
                file_data BLOB, file_type TEXT
            )
        """)
        conn.commit()


init_db()


def safe_read_sql(query, params=()):
    try:
        with sqlite3.connect("mh_group_erp.db") as conn:
            return pd.read_sql_query(query, conn, params=params)
    except Exception:
        return pd.DataFrame()


# ==========================================
# 3. دالة إرسال الـ SMS الحقيقية عبر البوابة
# ==========================================
def send_real_sms(phone_number, code):
    sms_user = st.secrets.get("SMS_USER", "YOUR_USER")
    sms_pass = st.secrets.get("SMS_PASS", "YOUR_PASS")
    sms_sender = st.secrets.get("SMS_SENDER", "MHGroup")

    url = "https://smsmisr.com/api/SMS/"
    payload = {
        "environment": "1",
        "username": sms_user,
        "password": sms_pass,
        "language": "2",
        "sender": sms_sender,
        "mobile": phone_number,
        "message": f"كود التحقق الخاص بك بنظام MH Group ERP هو: {code}",
    }
    try:
        response = requests.post(url, data=payload, timeout=8)
        return True
    except Exception:
        return False


# ==========================================
# 4. إدارة الجلسة والدخول
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_role" not in st.session_state:
    st.session_state["user_role"] = ""
if "username" not in st.session_state:
    st.session_state["username"] = ""
if "is_developer" not in st.session_state:
    st.session_state["is_developer"] = False
if "profile_pic" not in st.session_state:
    st.session_state["profile_pic"] = None
if "show_forgot_password" not in st.session_state:
    st.session_state["show_forgot_password"] = False
if "reset_stage" not in st.session_state:
    st.session_state["reset_stage"] = "request"
if "otp_code" not in st.session_state:
    st.session_state["otp_code"] = None
if "reset_username" not in st.session_state:
    st.session_state["reset_username"] = ""


# ==========================================
# 5. شاشة تسجيل الدخول المخصصة
# ==========================================
def login_page():
    cfg = st.session_state["login_config"]
    st.markdown(f"<h1 style='text-align: center;'>{cfg['title']}</h1>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if cfg.get("logo_bytes"):
            st.image(cfg["logo_bytes"], use_container_width=True)

        st.subheader(cfg["subtitle"])
        st.caption(cfg["welcome_msg"])

        if not st.session_state["show_forgot_password"]:
            username_input = st.text_input("اسم المستخدم")
            password_input = st.text_input("كلمة المرور", type="password")

            btn_col1, btn_col2 = st.columns([2, 1])
            with btn_col1:
                login_btn = st.button(cfg["btn_text"], use_container_width=True)
            with btn_col2:
                if st.button("نسيت كلمة السر؟", use_container_width=True):
                    st.session_state["show_forgot_password"] = True
                    st.session_state["reset_stage"] = "request"
                    st.rerun()

            if login_btn:
                with sqlite3.connect("mh_group_erp.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT role FROM users WHERE username = ? AND password = ?",
                        (username_input, password_input),
                    )
                    res = cursor.fetchone()

                if res:
                    st.session_state["logged_in"] = True
                    st.session_state["user_role"] = res[0]
                    st.session_state["username"] = username_input
                    st.success("تم تسجيل الدخول بنجاح!")
                    st.rerun()
                else:
                    st.error("بيانات الدخول غير صحيحة!")

        else:
            st.info("📱 استعادة كلمة السر عبر كود SMS")

            if st.session_state["reset_stage"] == "request":
                rec_username = st.text_input("اسم المستخدم:")
                rec_phone = st.text_input("رقم الهاتف المسجل للحساب:")

                col_r1, col_r2 = st.columns(2)
                with col_r1:
                    if st.button("إرسال كود التحقق (SMS)", use_container_width=True):
                        with sqlite3.connect("mh_group_erp.db") as conn:
                            cursor = conn.cursor()
                            cursor.execute(
                                "SELECT phone FROM users WHERE username = ?",
                                (rec_username,),
                            )
                            user_row = cursor.fetchone()

                        if user_row and (
                            user_row[0] == rec_phone or not user_row[0]
                        ):
                            generated_otp = str(random.randint(100000, 999999))
                            st.session_state["otp_code"] = generated_otp
                            st.session_state["reset_username"] = rec_username

                            send_real_sms(rec_phone, generated_otp)

                            st.session_state["reset_stage"] = "verify"
                            st.success("تم إرسال كود التحقق إلى هاتفك المحمول.")
                            st.rerun()
                        else:
                            st.error("اسم المستخدم أو رقم الهاتف غير مطابق!")

                with col_r2:
                    if st.button("إلغاء", use_container_width=True):
                        st.session_state["show_forgot_password"] = False
                        st.rerun()

            elif st.session_state["reset_stage"] == "verify":
                st.write(
                    f"تم إرسال كود SMS إلى هاتفك المسجل باسم **{st.session_state['reset_username']}**."
                )

                user_otp = st.text_input(
                    "أدخل كود التحقق المكون من 6 أرقام:",
                    max_chars=6,
                    type="password",
                )

                col_v1, col_v2 = st.columns(2)
                with col_v1:
                    if st.button("تأكيد الكود", use_container_width=True):
                        if user_otp == st.session_state["otp_code"]:
                            st.success("✅ الكود صحيح! انتقلت لصفحة تعيين كلمة السر.")
                            st.session_state["reset_stage"] = "new_pass"
                            st.rerun()
                        else:
                            st.error("❌ الكود غير صحيح! يرجى إعادة المحاولة.")

                with col_v2:
                    if st.button("إلغاء", use_container_width=True):
                        st.session_state["show_forgot_password"] = False
                        st.session_state["reset_stage"] = "request"
                        st.rerun()

            elif st.session_state["reset_stage"] == "new_pass":
                st.success("🔓 يرجى كتابة كلمة السر الجديدة لتحديث حسابك:")
                new_reset_pass = st.text_input("كلمة السر الجديدة:", type="password")
                confirm_reset_pass = st.text_input(
                    "تأكيد كلمة السر الجديدة:", type="password"
                )

                if st.button("حفظ كلمة السر الجديدة", use_container_width=True):
                    if not new_reset_pass:
                        st.error("يرجى كتابة كلمة السر!")
                    elif new_reset_pass != confirm_reset_pass:
                        st.error("كلمتا المرور غير متطابقتين!")
                    else:
                        with sqlite3.connect("mh_group_erp.db") as conn:
                            cursor = conn.cursor()
                            cursor.execute(
                                "UPDATE users SET password = ? WHERE username = ?",
                                (new_reset_pass, st.session_state["reset_username"]),
                            )
                            conn.commit()
                        st.success("✅ تم تحديث كلمة السر بنجاح!")
                        st.session_state["show_forgot_password"] = False
                        st.session_state["reset_stage"] = "request"
                        st.rerun()


# ==========================================
# 6. لوحة التحكم الرئيسية والأقسام
# ==========================================
if not st.session_state["logged_in"]:
    login_page()
else:
    st.sidebar.title("MH GROUP")
    st.sidebar.caption("ERP SYSTEM")

    if st.session_state["profile_pic"]:
        st.sidebar.image(st.session_state["profile_pic"], width=90)

    st.sidebar.markdown(
        f"👤 **{st.session_state['username']}**\n\n*(المدير العام)*"
    )

    is_admin = st.session_state["user_role"] == "Admin"

    if is_admin:
        dev_toggle = st.sidebar.checkbox(
            "🛠️ وضع المطور",
            value=st.session_state["is_developer"],
        )
        st.session_state["is_developer"] = dev_toggle

    all_pages = [
        "لوحة التحكم",
        "العقارات والمشروعات",
        "الإدارة المالية",
        "الموارد البشرية",
        "المستثمرين",
        "الموردين",
        "الموظفين",
        "IT Support",
        "المستندات",
        "التقارير",
        "المستخدمين والصلاحيات",
        "الإعدادات",
        "سجل العمليات",
    ]

    menu_options = all_pages if (st.session_state["is_developer"] or is_admin) else ["لوحة التحكم"]

    page = st.sidebar.radio("القائمة الرئيسية", menu_options)

    if st.sidebar.button("🚪 تسجيل الخروج"):
        st.session_state["logged_in"] = False
        st.rerun()

    # --- 1. Dashboard (تطابق كامل مع الصورة) ---
    if page == "لوحة التحكم":
        # الهيدر العلوي وشريط البحث والمعلومات
        top_c1, top_c2, top_c3 = st.columns([2, 2, 1])
        with top_c1:
            st.title("لوحة التحكم")
            st.caption("👋 مرحباً بك، المدير العام")
        with top_c2:
            st.text_input("🔍 ابحث هنا...", placeholder="Ctrl + K", label_visibility="collapsed")
        with top_c3:
            st.caption("الفترة الحالية: 01/05/2024 - 31/05/2024")

        # ------------------ البطاقات الإحصائية الـ 5 ------------------
        m1, m2, m3, m4, m5 = st.columns(5)
        
        with m1:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-header">
                    <span>إجمالي الإيرادات</span>
                    <span style="color:#A855F7;">🟣</span>
                </div>
                <div class="metric-value">8,250,000 <span style="font-size:0.9rem;">ج.م</span></div>
                <div class="metric-sub"><span class="badge-positive">+12.5%</span> عن الشهر الماضي</div>
            </div>
            """, unsafe_allow_html=True)
            df_spark1 = pd.DataFrame({'x': range(10), 'y': [5, 6, 5.5, 7, 6.8, 8, 7.5, 9, 8.5, 10]})
            st.line_chart(df_spark1['y'], height=60)

        with m2:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-header">
                    <span>إجمالي المصروفات</span>
                    <span style="color:#EF4444;">🔴</span>
                </div>
                <div class="metric-value">2,850,000 <span style="font-size:0.9rem;">ج.م</span></div>
                <div class="metric-sub"><span class="badge-negative">-3.2%</span> عن الشهر الماضي</div>
            </div>
            """, unsafe_allow_html=True)
            df_spark2 = pd.DataFrame({'x': range(10), 'y': [4, 3.8, 4.2, 3.5, 3.9, 3.1, 3.3, 2.9, 3.0, 2.8]})
            st.line_chart(df_spark2['y'], height=60)

        with m3:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-header">
                    <span>صافي الأرباح</span>
                    <span style="color:#10B981;">🟢</span>
                </div>
                <div class="metric-value">5,400,000 <span style="font-size:0.9rem;">ج.م</span></div>
                <div class="metric-sub"><span class="badge-positive">+18.7%</span> عن الشهر الماضي</div>
            </div>
            """, unsafe_allow_html=True)
            df_spark3 = pd.DataFrame({'x': range(10), 'y': [2, 2.5, 3, 3.2, 4, 4.1, 4.8, 5, 5.2, 5.4]})
            st.line_chart(df_spark3['y'], height=60)

        with m4:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-header">
                    <span>قيمة العقارات</span>
                    <span style="color:#3B82F6;">🔵</span>
                </div>
                <div class="metric-value">45,750,000 <span style="font-size:0.9rem;">ج.م</span></div>
                <div class="metric-sub" style="color: #64748B;">إجمالي قيمة المحفظة العقارية</div>
            </div>
            """, unsafe_allow_html=True)
            df_spark4 = pd.DataFrame({'x': range(10), 'y': [40, 41, 41, 42, 43, 43.5, 44, 44.8, 45, 45.75]})
            st.line_chart(df_spark4['y'], height=60)

        with m5:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-header">
                    <span>العقارات المباعة</span>
                    <span style="color:#F59E0B;">🟠</span>
                </div>
                <div class="metric-value">12</div>
                <div class="metric-sub" style="color: #64748B;">عقار هذا الشهر</div>
            </div>
            """, unsafe_allow_html=True)
            df_spark5 = pd.DataFrame({'x': range(10), 'y': [1, 2, 4, 3, 6, 5, 8, 9, 10, 12]})
            st.line_chart(df_spark5['y'], height=60)

        st.markdown("<br>", unsafe_allow_html=True)

        # ------------------ الصف الثاني: نظرة عامة، توزيع المصروفات، النشاط الأخير ------------------
        col_main, col_pie, col_act = st.columns([2.2, 1.3, 1.5])

        with col_main:
            st.markdown("### نظرة عامة على الأداء")
            perf_df = pd.DataFrame({
                'الشهر': ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو', 'يوليو'],
                'الإيرادات': [6, 6.8, 6.5, 7.2, 7.5, 7.5, 8.8],
                'الأرباح': [3.8, 4.2, 4.1, 4.5, 4.8, 4.6, 5.3],
                'المصروفات': [1.5, 1.8, 1.7, 2.2, 2.6, 2.4, 3.0]
            }).set_index('الشهر')
            st.line_chart(perf_df)

        with col_pie:
            st.markdown("### توزيع المصروفات")
            pie_data = pd.DataFrame({
                'الفئة': ['شراء عقارات', 'مصاريف تطوير', 'مصاريف إدارية', 'رواتب وأجور', 'أخرى'],
                'النسبة': [40, 25, 15, 10, 10]
            })
            st.vega_lite_chart(pie_data, {
                'mark': {'type': 'arc', 'innerRadius': 50},
                'encoding': {
                    'field': 'النسبة',
                    'type': 'quantitative'
                },
                'color': {
                    'field': 'الفئة',
                    'type': 'nominal'
                }
            }, use_container_width=True)
            st.caption("إجمالي المصروفات: 2,850,000 ج.م")

        with col_act:
            st.markdown("### النشاط الأخير")
            activities = [
                ("🏢 تم إضافة عقار جديد", "منذ 10 دقائق"),
                ("💵 تم تسجيل إيراد جديد", "منذ 30 دقيقة"),
                ("📄 تم رفع مستند جديد", "منذ ساعتين"),
                ("👤 تم إضافة موظف جديد", "منذ 3 ساعات"),
                ("🏢 تم تحديث بيانات عقار", "منذ 5 ساعات"),
            ]
            for act, time_str in activities:
                st.markdown(f"""
                <div style="background-color:#1E293B; padding:10px; border-radius:8px; margin-bottom:8px; display:flex; justify-content:space-between; border:1px solid #334155;">
                    <span style="font-size:0.85rem;">{act}</span>
                    <span style="font-size:0.75rem; color:#94A3B8;">{time_str}</span>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ------------------ الصف الثالث: آخر العقارات المضافة & آخر المعاملات المالية ------------------
        col_prop, col_fin = st.columns(2)

        with col_prop:
            st.markdown("### آخر العقارات المضافة")
            props_data = pd.DataFrame([
                {"اسم العقار": "فيلا النرجس 001", "سعر الشراء": "5,200,000 ج.م", "الحالة": "تحت التطوير", "تاريخ الإضافة": "2024-05-23"},
                {"اسم العقار": "عمارة الشروق 15", "سعر الشراء": "8,750,000 ج.م", "الحالة": "مباع", "تاريخ الإضافة": "2024-05-22"},
                {"اسم العقار": "قطعة أرض التجمع", "سعر الشراء": "3,100,000 ج.م", "الحالة": "متاح", "تاريخ الإضافة": "2024-05-21"},
                {"اسم العقار": "مول القاهرة الجديدة", "سعر الشراء": "15,000,000 ج.م", "الحالة": "تحت التطوير", "تاريخ الإضافة": "2024-05-20"},
            ])
            st.dataframe(props_data, use_container_width=True)

        with col_fin:
            st.markdown("### آخر المعاملات المالية")
            trans_data = pd.DataFrame([
                {"نوع العملية": "إيراد", "المبلغ": "850,000 ج.م", "الجهة": "عميل - شركة النصر", "التاريخ": "2024-05-23", "الحالة": "مكتملة"},
                {"نوع العملية": "مصروف", "المبلغ": "250,000 ج.م", "الجهة": "مورد - مقاولات مصر", "التاريخ": "2024-05-23", "الحالة": "مكتملة"},
                {"نوع العملية": "إيراد", "المبلغ": "1,200,000 ج.م", "الجهة": "عميل - أحمد محمود", "التاريخ": "2024-05-22", "الحالة": "مكتملة"},
                {"نوع العملية": "مصروف", "المبلغ": "150,000 ج.م", "الجهة": "شركة الكهرباء", "التاريخ": "2024-05-22", "الحالة": "مكتملة"},
            ])
            st.dataframe(trans_data, use_container_width=True)

    # --- باقي الأقسام تباعاً ---
    elif page == "العقارات والمشروعات":
        st.title("🏡 إدارة العقارات والوحدات")
        # نفس وظائف العقارات القديمة
    elif page == "الإدارة المالية":
        st.title("💼 قسم المالية والمستثمرين")
        # نفس وظائف المالية القديمة
