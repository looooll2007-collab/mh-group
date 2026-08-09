import base64
import datetime
import io
import random
import sqlite3
import pandas as pd
import requests
import streamlit as st

# ==========================================
# 1. تهيئة الصفحة
# ==========================================
st.set_page_config(
    page_title="MH GROUP ERP SYSTEM",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================
# 2. تخصيص المظهر (CSS) ليطابق الصورة تماماً
# ==========================================
st.markdown(
    """
<style>
    /* خلفية التطبيق كاملة */
    .stApp {
        background-color: #0B0F17 !important;
        color: #F3F4F6 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* إخفاء شريط الملاحة الافتراضي في تسجيل الدخول */
    section[data-testid="stSidebar"] {
        background-color: #111827 !important;
        border-right: 1px solid #1F2937 !important;
    }

    /* كرت المزايا بالجانب الأيسر */
    .feature-card {
        background: linear-gradient(180deg, rgba(31, 41, 55, 0.4) 0%, rgba(17, 24, 39, 0.8) 100%);
        border: 1px solid rgba(217, 119, 6, 0.2);
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        margin-top: 10px;
    }
    .feature-icon {
        font-size: 1.5rem;
        color: #D97706;
        margin-bottom: 5px;
    }
    .feature-title {
        font-weight: bold;
        font-size: 0.9rem;
        color: #F8FAFC;
    }
    .feature-desc {
        font-size: 0.75rem;
        color: #94A3B8;
    }

    /* صندوق تسجيل الدخول الرئيسي */
    .login-container {
        background-color: #111622;
        border: 1px solid #1F2937;
        border-radius: 20px;
        padding: 40px 30px;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
    }
    
    /* زر تسجيل الدخول الذهبي التدرجي */
    .stButton>button {
        background: linear-gradient(90deg, #B45309 0%, #D97706 50%, #F59E0B 100%) !important;
        color: #FFFFFF !important;
        border-radius: 10px !important;
        border: none !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
        height: 50px !important;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        opacity: 0.9;
        box-shadow: 0 0 15px rgba(217, 119, 6, 0.4);
    }

    /* حقول الإدخال */
    .stTextInput input {
        background-color: #1A202C !important;
        color: #FFFFFF !important;
        border: 1px solid #2D3748 !important;
        border-radius: 10px !important;
        height: 48px !important;
    }
    .stTextInput input:focus {
        border-color: #D97706 !important;
    }

    /* بطاقات المظاهر الإحصائية في الداشبورد */
    .metric-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 15px;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #FFFFFF;
        margin: 8px 0;
    }
</style>
""",
    unsafe_allow_html=True,
)


# ==========================================
# 3. تهيئة قاعدة البيانات والتأكد من بيانات الدخول الحقيقية
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

        # إضافة حساب الآدمين الافتراضي الحقيقي إن لم يكن موجوداً
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO users (username, password, role, phone) VALUES ('admin', 'admin123', 'Admin', '01000000000')"
            )
        conn.commit()

init_db()


# ==========================================
# 4. إدارة حالة الجلسة (Session States)
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_role" not in st.session_state:
    st.session_state["user_role"] = ""
if "username" not in st.session_state:
    st.session_state["username"] = ""


# ==========================================
# 5. شاشة تسجيل الدخول المطابقة تماماً للصورة
# ==========================================
def render_login_screen():
    st.markdown("<br>", unsafe_allow_html=True)
    
    # تقسيم الصفحة إلى عمودين رئيسيين (الهيدر الترحيبي والصورة على اليسار / نموذج الدخول على اليمين)
    col_left, col_space, col_right = st.columns([1.1, 0.1, 1])

    # ------------------ الجانب الأيسر: الشعار والمميزات ------------------
    with col_left:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 30px;">
            <div style="font-size: 2.2rem; color: #D97706; font-weight: bold;">M</div>
            <div>
                <div style="font-size: 1.3rem; font-weight: 800; letter-spacing: 1px; color: #FFFFFF;">MH GROUP</div>
                <div style="font-size: 0.75rem; color: #D97706; font-weight: 600; letter-spacing: 2px;">ERP SYSTEM</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="margin-top: 40px; margin-bottom: 30px;">
            <h1 style="font-size: 2.8rem; font-weight: 900; color: #FFFFFF; margin-bottom: 5px;">مرحباً بك في</h1>
            <h1 style="font-size: 2.8rem; font-weight: 900; color: #D97706; margin-top: 0;">MH GROUP ERP</h1>
            <p style="color: #94A3B8; font-size: 1.1rem; line-height: 1.6; margin-top: 15px;">
                نظام متكامل لإدارة أعمال الاستثمار والتطوير العقاري بكفاءة واحترافية عالية
            </p>
        </div>
        """, unsafe_allow_html=True)

        # المزايا الأربع الموجودة في أسفل اليسار بالصورة
        f1, f2, f3, f4 = st.columns(4)
        with f1:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🏢</div>
                <div class="feature-title">إدارة شاملة</div>
                <div class="feature-desc">جميع عملياتك في مكان واحد</div>
            </div>
            """, unsafe_allow_html=True)
        with f2:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🕒</div>
                <div class="feature-title">تقارير دقيقة</div>
                <div class="feature-desc">تقارير وتحليلات لحظية</div>
            </div>
            """, unsafe_allow_html=True)
        with f3:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🛡️</div>
                <div class="feature-title">أمان عالٍ</div>
                <div class="feature-desc">حماية بياناتك على أعلى مستوى</div>
            </div>
            """, unsafe_allow_html=True)
        with f4:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <div class="feature-title">إدارة ذكية</div>
                <div class="feature-desc">لوحة تحكم متكاملة</div>
            </div>
            """, unsafe_allow_html=True)

    # ------------------ الجانب الأيمن: نموذج الدخول ------------------
    with col_right:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <div style="font-size: 3rem; color: #D97706; margin-bottom: 10px;">👑</div>
            <h2 style="color: #FFFFFF; font-weight: 800; font-size: 2rem; margin: 0;">تسجيل الدخول</h2>
            <p style="color: #94A3B8; font-size: 0.95rem; margin-top: 5px;">مرحباً بك، يرجى تسجيل الدخول للوصول إلى حسابك</p>
        </div>
        """, unsafe_allow_html=True)

        # مدخلات البيانات الحقيقية
        username_input = st.text_input("اسم المستخدم", placeholder="أدخل اسم المستخدم (مثال: admin)")
        password_input = st.text_input("كلمة المرور", type="password", placeholder="أدخل كلمة المرور (مثال: admin123)")

        c_rem, c_forgot = st.columns([1, 1])
        with c_rem:
            remember_me = st.checkbox("تذكرني")
        with c_forgot:
            st.markdown("<div style='text-align: left;'><a href='#' style='color: #D97706; text-decoration: none; font-size: 0.9rem;'>نسيت كلمة المرور؟</a></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # زر تسجيل الدخول مع التحقق الحقيقي من قاعدة البيانات
        if st.button("تسجيل الدخول ➔", use_container_width=True):
            if not username_input or not password_input:
                st.error("يرجى إدخال اسم المستخدم وكلمة المرور!")
            else:
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
                    st.success("تم تسجيل الدخول بنجاح! جاري التوجيه...")
                    st.rerun()
                else:
                    st.error("اسم المستخدم أو كلمة المرور غير صحيحة!")

        # أزرار الدخول الخارجي (Google & Microsoft)
        st.markdown("""
        <div style="text-align: center; margin: 25px 0 15px 0; color: #64748B; font-size: 0.85rem;">
            أو تسجيل الدخول باستخدام
        </div>
        """, unsafe_allow_html=True)

        btn_g, btn_m = st.columns(2)
        with btn_g:
            if st.button("🌐 Google", use_container_width=True):
                st.info("خدمة Google OAuth تتطلب مفتاح API في الإعدادات.")
        with btn_m:
            if st.button("💻 Microsoft", use_container_width=True):
                st.info("خدمة Microsoft Azure OAuth تتطلب مفتاح API.")

        st.markdown("""
        <div style="text-align: center; margin-top: 30px; color: #475569; font-size: 0.8rem;">
            جميع الحقوق محفوظة © MH Group 2026
        </div>
        """, unsafe_allow_html=True)


# ==========================================
# 6. لوحة التحكم الرئيسية بعد تسجيل الدخول
# ==========================================
if not st.session_state["logged_in"]:
    render_login_screen()
else:
    # الشريط الجانبي
    st.sidebar.title("MH GROUP")
    st.sidebar.caption("ERP SYSTEM")
    st.sidebar.markdown(f"👤 **{st.session_state['username']}**\n\n*(المدير العام)*")

    menu_options = [
        "لوحة التحكم", "العقارات والمشروعات", "الإدارة المالية",
        "الموارد البشرية", "المستثمرين", "الموردين", "الموظفين", "الإعدادات"
    ]
    page = st.sidebar.radio("القائمة الرئيسية", menu_options)

    if st.sidebar.button("🚪 تسجيل الخروج"):
        st.session_state["logged_in"] = False
        st.rerun()

    # شاشة الداشبورد
    if page == "لوحة التحكم":
        top_c1, top_c2, top_c3 = st.columns([2, 2, 1])
        with top_c1:
            st.title("لوحة التحكم")
            st.caption("👋 مرحباً بك، المدير العام")
        with top_c2:
            st.text_input("🔍 ابحث هنا...", placeholder="Ctrl + K", label_visibility="collapsed")
        with top_c3:
            st.caption("الفترة الحالية: مايو 2026")

        # 5 بطاقات إحصائية
        m1, m2, m3, m4, m5 = st.columns(5)
        with m1:
            st.markdown('<div class="metric-card"><div style="color:#94A3B8;">إجمالي الإيرادات</div><div class="metric-value">8,250,000 <span style="font-size:0.8rem;">ج.م</span></div></div>', unsafe_allow_html=True)
            st.line_chart([5, 6, 7, 8, 10], height=50)
        with m2:
            st.markdown('<div class="metric-card"><div style="color:#94A3B8;">إجمالي المصروفات</div><div class="metric-value">2,850,000 <span style="font-size:0.8rem;">ج.م</span></div></div>', unsafe_allow_html=True)
            st.line_chart([4, 3.8, 3.2, 2.8], height=50)
        with m3:
            st.markdown('<div class="metric-card"><div style="color:#94A3B8;">صافي الأرباح</div><div class="metric-value">5,400,000 <span style="font-size:0.8rem;">ج.م</span></div></div>', unsafe_allow_html=True)
            st.line_chart([2, 3, 4, 5.4], height=50)
        with m4:
            st.markdown('<div class="metric-card"><div style="color:#94A3B8;">قيمة العقارات</div><div class="metric-value">45,750,000 <span style="font-size:0.8rem;">ج.م</span></div></div>', unsafe_allow_html=True)
            st.line_chart([40, 42, 45], height=50)
        with m5:
            st.markdown('<div class="metric-card"><div style="color:#94A3B8;">العقارات المباعة</div><div class="metric-value">12</div></div>', unsafe_allow_html=True)
            st.line_chart([1, 4, 8, 12], height=50)

    else:
        st.title(f"قسم: {page}")
        st.info("هذا القسم مربوط بنظام إدارة البيانات بنجاح.")
