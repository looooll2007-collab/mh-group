
import streamlit as st
import hashlib
import secrets
from datetime import date, datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Date, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

# ============================================================
# MH GROUP ERP - FINAL SINGLE FILE
# Arabic RTL / Dark Gold / Real Login / PostgreSQL Ready
# ============================================================

st.set_page_config(
    page_title="MH Group ERP",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- DATABASE ----------------

DATABASE_URL = st.secrets.get("DATABASE_URL", "") if hasattr(st, "secrets") else ""
if not DATABASE_URL:
    import os
    DATABASE_URL = os.getenv("DATABASE_URL", "")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

if not DATABASE_URL:
    DATABASE_URL = "sqlite:///mh_group_erp.db"

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    full_name = Column(String(150), default="المدير العام")
    role = Column(String(50), default="admin")
    active = Column(Boolean, default=True)

class Property(Base):
    __tablename__ = "properties"
    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True)
    name = Column(String(150))
    property_type = Column(String(80))
    purchase = Column(Float, default=0)
    expenses = Column(Float, default=0)
    sale = Column(Float, default=0)
    status = Column(String(50), default="متاح")
    created_at = Column(DateTime, default=datetime.utcnow)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    kind = Column(String(30))
    title = Column(String(150))
    amount = Column(Float, default=0)
    tx_date = Column(Date, default=date.today)
    note = Column(String(500), default="")

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True)
    name = Column(String(150))
    job = Column(String(100))
    hours = Column(Float, default=0)
    rate = Column(Float, default=0)
    advances = Column(Float, default=0)

class Supplier(Base):
    __tablename__ = "suppliers"
    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True)
    name = Column(String(150))
    due = Column(Float, default=0)
    paid = Column(Float, default=0)

class Audit(Base):
    __tablename__ = "audit"
    id = Column(Integer, primary_key=True)
    username = Column(String(80))
    action = Column(String(300))
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(engine)

# ---------------- SECURITY ----------------

def hash_password(password):
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), 180000
    ).hex()
    return salt + "$" + digest

def verify_password(password, stored):
    try:
        salt, digest = stored.split("$", 1)
        check = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), salt.encode(), 180000
        ).hex()
        return secrets.compare_digest(check, digest)
    except Exception:
        return False

def seed_admin():
    db = Session()
    try:
        if not db.query(User).filter_by(username="admin").first():
            db.add(User(
                username="admin",
                password_hash=hash_password("ChangeMe123!"),
                full_name="المدير العام",
                role="admin",
                active=True
            ))
            db.commit()
    finally:
        db.close()

seed_admin()

def log_action(username, action):
    db = Session()
    db.add(Audit(username=username, action=action))
    db.commit()
    db.close()

def money(x):
    return f"{x:,.0f} ج.م"

# ---------------- GLOBAL CSS ----------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Cairo', sans-serif !important;
}

.stApp {
    background: #080d15;
    color: #fff;
}

.block-container {
    max-width: 1500px;
    padding-top: 25px;
}

section[data-testid="stSidebar"] {
    background: #0d1420;
    border-left: 1px solid rgba(212,170,76,.15);
}

h1,h2,h3,h4,p,label {
    font-family: 'Cairo', sans-serif !important;
}

.gold {
    color: #d7b35b !important;
}

.login-shell {
    min-height: 82vh;
    display: flex;
    align-items: center;
    justify-content: center;
}

.login-box {
    width: 100%;
    max-width: 530px;
    background: linear-gradient(145deg,#141d29,#0c121b);
    border: 1px solid rgba(215,179,91,.25);
    border-radius: 22px;
    padding: 42px;
    box-shadow: 0 30px 90px rgba(0,0,0,.5);
    text-align: right;
}

.logo {
    width: 78px;
    height: 78px;
    margin: 0 auto 15px;
    border-radius: 19px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(145deg,#f3d478,#a87820);
    color: #111;
    font-size: 48px;
    font-weight: 900;
    box-shadow: 0 12px 35px rgba(215,179,91,.18);
}

.login-title {
    text-align: center;
    color: #e0b85d;
    font-size: 34px;
    font-weight: 800;
}

.login-sub {
    text-align: center;
    color: #8993a3;
    margin-bottom: 28px;
}

.stTextInput > div > div {
    background: #171f2b !important;
    border: 1px solid rgba(255,255,255,.10) !important;
    border-radius: 10px !important;
}

.stTextInput input {
    color: white !important;
    text-align: right !important;
    direction: rtl !important;
}

.stButton > button {
    background: linear-gradient(145deg,#e1bd5c,#a97821) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    min-height: 50px !important;
    font-family: 'Cairo', sans-serif !important;
    font-weight: 800 !important;
}

.kpi {
    background: linear-gradient(145deg,#152130,#0e1722);
    border: 1px solid rgba(255,255,255,.07);
    border-radius: 16px;
    padding: 20px;
    min-height: 130px;
}

.kpi-label {
    color: #8994a5;
    font-size: 13px;
}

.kpi-value {
    color: white;
    font-size: 25px;
    font-weight: 800;
    margin-top: 8px;
}

.card {
    background: #111a26;
    border: 1px solid rgba(255,255,255,.07);
    border-radius: 16px;
    padding: 20px;
}

.footer {
    text-align: center;
    color: #657184;
    margin-top: 40px;
    padding: 20px;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# LOGIN
# ============================================================

if "user" not in st.session_state:

    st.markdown("""
    <div class="login-shell">
        <div class="login-box">
            <div class="logo">M</div>
            <div class="login-title">MH GROUP</div>
            <div class="login-sub">نظام الإدارة المتكامل ERP</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Put the real Streamlit inputs immediately below the visual card.
    # This avoids the problem shown in the user's screenshot where HTML
    # was displayed as plain text.

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("### 🔐 تسجيل الدخول")
        username = st.text_input("اسم المستخدم", placeholder="أدخل اسم المستخدم")
        password = st.text_input("كلمة المرور", type="password", placeholder="أدخل كلمة المرور")

        remember = st.checkbox("تذكرني")

        if st.button("تسجيل الدخول  →", use_container_width=True):
            db = Session()
            user = db.query(User).filter_by(
                username=username,
                active=True
            ).first()

            valid = user and verify_password(password, user.password_hash)

            if valid:
                st.session_state.user = {
                    "username": user.username,
                    "name": user.full_name,
                    "role": user.role
                }
                log_action(user.username, "تسجيل الدخول")
                st.rerun()
            else:
                st.error("اسم المستخدم أو كلمة المرور غير صحيحة.")

        st.markdown("""
        <div style="
            text-align:center;
            color:#687386;
            margin-top:25px;
            font-size:12px;">
            MH GROUP © 2026
        </div>
        """, unsafe_allow_html=True)

    st.stop()

# ============================================================
# MAIN ERP
# ============================================================

user = st.session_state.user

with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:10px 0 25px;">
        <div class="logo" style="margin:auto;width:58px;height:58px;font-size:35px;">M</div>
        <h3 style="color:white;margin-bottom:0;">MH GROUP</h3>
        <small style="color:#d7b35b;">ERP SYSTEM</small>
    </div>
    """, unsafe_allow_html=True)

    pages = {
        "🏠 لوحة التحكم": "dashboard",
        "🏢 العقارات": "properties",
        "💰 المالية": "finance",
        "👥 الموظفين": "employees",
        "🤝 الموردين": "suppliers",
        "📊 التقارير": "reports",
        "🧾 سجل العمليات": "audit",
        "⚙️ الإعدادات": "settings",
    }

    selected = st.radio("القائمة", list(pages.keys()))
    page = pages[selected]

    st.markdown("---")
    st.write(f"👤 **{user['name']}**")
    st.caption(f"الصلاحية: {user['role']}")

    if st.button("🚪 تسجيل الخروج", use_container_width=True):
        log_action(user["username"], "تسجيل الخروج")
        del st.session_state["user"]
        st.rerun()

# ---------------- DASHBOARD ----------------

if page == "dashboard":

    st.markdown("# لوحة التحكم")
    st.caption("نظرة عامة مباشرة على بيانات MH Group")

    db = Session()

    transactions = db.query(Transaction).all()
    properties = db.query(Property).all()
    employees = db.query(Employee).all()
    suppliers = db.query(Supplier).all()

    revenue = sum(x.amount for x in transactions if x.kind == "إيراد")
    expenses = sum(x.amount for x in transactions if x.kind == "مصروف")
    profit = revenue - expenses
    portfolio = sum(x.purchase + x.expenses for x in properties)

    a,b,c,d = st.columns(4)

    with a:
        st.markdown(f"""
        <div class="kpi">
            <div class="kpi-label">إجمالي الإيرادات</div>
            <div class="kpi-value">{money(revenue)}</div>
        </div>
        """, unsafe_allow_html=True)

    with b:
        st.markdown(f"""
        <div class="kpi">
            <div class="kpi-label">إجمالي المصروفات</div>
            <div class="kpi-value">{money(expenses)}</div>
        </div>
        """, unsafe_allow_html=True)

    with c:
        st.markdown(f"""
        <div class="kpi">
            <div class="kpi-label">صافي الأرباح</div>
            <div class="kpi-value">{money(profit)}</div>
        </div>
        """, unsafe_allow_html=True)

    with d:
        st.markdown(f"""
        <div class="kpi">
            <div class="kpi-label">قيمة العقارات</div>
            <div class="kpi-value">{money(portfolio)}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 🏢 آخر العقارات")

    if properties:
        import pandas as pd
        df = pd.DataFrame([
            {
                "الكود": p.code,
                "العقار": p.name,
                "النوع": p.property_type,
                "التكلفة": p.purchase + p.expenses,
                "سعر البيع": p.sale,
                "الربح المتوقع": p.sale - p.purchase - p.expenses,
                "الحالة": p.status
            }
            for p in properties[-10:]
        ])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("لا توجد عقارات حتى الآن.")

    db.close()

# ---------------- PROPERTIES ----------------

elif page == "properties":

    st.markdown("# 🏢 إدارة العقارات")

    db = Session()

    with st.form("property_form"):
        st.markdown("### إضافة عقار")

        a,b,c = st.columns(3)

        code = a.text_input("كود العقار")
        name = b.text_input("اسم العقار")
        typ = c.selectbox(
            "نوع العقار",
            ["شقة","فيلا","عمارة","أرض","مول","مكتب","محل"]
        )

        purchase = a.number_input("سعر الشراء", min_value=0.0, step=1000.0)
        expenses = b.number_input("المصروفات", min_value=0.0, step=1000.0)
        sale = c.number_input("سعر البيع المتوقع", min_value=0.0, step=1000.0)

        status = st.selectbox(
            "الحالة",
            ["متاح","تحت التطوير","مباع"]
        )

        st.info(
            f"التكلفة النهائية: {money(purchase + expenses)}  |  "
            f"الربح المتوقع: {money(sale - purchase - expenses)}"
        )

        if st.form_submit_button("💾 حفظ العقار"):
            if not code or not name:
                st.error("اكتب كود واسم العقار.")
            elif db.query(Property).filter_by(code=code).first():
                st.error("كود العقار موجود بالفعل.")
            else:
                db.add(Property(
                    code=code,
                    name=name,
                    property_type=typ,
                    purchase=purchase,
                    expenses=expenses,
                    sale=sale,
                    status=status
                ))
                db.commit()
                log_action(user["username"], f"إضافة عقار {code}")
                st.success("تم حفظ العقار.")
                st.rerun()

    properties = db.query(Property).order_by(Property.id.desc()).all()

    import pandas as pd
    df = pd.DataFrame([
        {
            "الكود": p.code,
            "العقار": p.name,
            "النوع": p.property_type,
            "الشراء": p.purchase,
            "المصروفات": p.expenses,
            "التكلفة": p.purchase + p.expenses,
            "البيع": p.sale,
            "الربح": p.sale - p.purchase - p.expenses,
            "الحالة": p.status
        }
        for p in properties
    ])

    st.dataframe(df, use_container_width=True, hide_index=True)
    db.close()

# ---------------- FINANCE ----------------

elif page == "finance":

    st.markdown("# 💰 الإدارة المالية")

    db = Session()

    with st.form("transaction_form"):

        a,b,c = st.columns(3)

        kind = a.selectbox("نوع العملية", ["إيراد","مصروف"])
        title = b.text_input("البيان")
        amount = c.number_input("المبلغ", min_value=0.0, step=1000.0)

        txdate = a.date_input("التاريخ", date.today())
        note = b.text_input("ملاحظات")

        if st.form_submit_button("💾 حفظ العملية"):

            db.add(Transaction(
                kind=kind,
                title=title,
                amount=amount,
                tx_date=txdate,
                note=note
            ))

            db.commit()
            log_action(user["username"], f"إضافة {kind}: {amount}")
            st.success("تم حفظ العملية.")
            st.rerun()

    transactions = db.query(Transaction).order_by(Transaction.id.desc()).all()

    import pandas as pd

    df = pd.DataFrame([
        {
            "النوع": x.kind,
            "البيان": x.title,
            "المبلغ": x.amount,
            "التاريخ": x.tx_date,
            "الملاحظات": x.note
        }
        for x in transactions
    ])

    st.dataframe(df, use_container_width=True, hide_index=True)
    db.close()

# ---------------- EMPLOYEES ----------------

elif page == "employees":

    st.markdown("# 👥 الموارد البشرية")

    db = Session()

    with st.form("employee_form"):

        a,b,c = st.columns(3)

        code = a.text_input("كود الموظف")
        name = b.text_input("اسم الموظف")
        job = c.text_input("الوظيفة")

        hours = a.number_input("عدد الساعات", min_value=0.0)
        rate = b.number_input("سعر الساعة", min_value=0.0)
        advances = c.number_input("السلف", min_value=0.0)

        if st.form_submit_button("💾 حفظ الموظف"):

            db.add(Employee(
                code=code,
                name=name,
                job=job,
                hours=hours,
                rate=rate,
                advances=advances
            ))

            db.commit()
            log_action(user["username"], f"إضافة موظف {code}")
            st.success("تم حفظ الموظف.")
            st.rerun()

    employees = db.query(Employee).order_by(Employee.id.desc()).all()

    import pandas as pd

    df = pd.DataFrame([
        {
            "الكود": e.code,
            "الموظف": e.name,
            "الوظيفة": e.job,
            "الساعات": e.hours,
            "سعر الساعة": e.rate,
            "الإجمالي": e.hours * e.rate,
            "السلف": e.advances,
            "المتبقي": e.hours * e.rate - e.advances
        }
        for e in employees
    ])

    st.dataframe(df, use_container_width=True, hide_index=True)
    db.close()

# ---------------- SUPPLIERS ----------------

elif page == "suppliers":

    st.markdown("# 🤝 الموردين")

    db = Session()

    with st.form("supplier_form"):

        a,b,c = st.columns(3)

        code = a.text_input("كود المورد")
        name = b.text_input("اسم المورد")
        due = c.number_input("إجمالي المستحق", min_value=0.0)
        paid = a.number_input("المدفوع", min_value=0.0)

        if st.form_submit_button("💾 حفظ المورد"):

            db.add(Supplier(
                code=code,
                name=name,
                due=due,
                paid=paid
            ))

            db.commit()
            log_action(user["username"], f"إضافة مورد {code}")
            st.success("تم حفظ المورد.")
            st.rerun()

    suppliers = db.query(Supplier).order_by(Supplier.id.desc()).all()

    import pandas as pd

    df = pd.DataFrame([
        {
            "الكود": s.code,
            "المورد": s.name,
            "المستحق": s.due,
            "المدفوع": s.paid,
            "المتبقي": s.due - s.paid
        }
        for s in suppliers
    ])

    st.dataframe(df, use_container_width=True, hide_index=True)
    db.close()

# ---------------- REPORTS ----------------

elif page == "reports":

    st.markdown("# 📊 التقارير")

    db = Session()

    properties = db.query(Property).all()
    transactions = db.query(Transaction).all()
    employees = db.query(Employee).all()

    import pandas as pd

    report = st.selectbox(
        "نوع التقرير",
        ["العقارات","المالية","الموظفين"]
    )

    if report == "العقارات":
        df = pd.DataFrame([
            {
                "الكود":p.code,
                "العقار":p.name,
                "التكلفة":p.purchase+p.expenses,
                "البيع":p.sale,
                "الربح":p.sale-p.purchase-p.expenses,
                "الحالة":p.status
            }
            for p in properties
        ])

    elif report == "المالية":
        df = pd.DataFrame([
            {
                "النوع":x.kind,
                "البيان":x.title,
                "المبلغ":x.amount,
                "التاريخ":x.tx_date
            }
            for x in transactions
        ])

    else:
        df = pd.DataFrame([
            {
                "الكود":e.code,
                "الموظف":e.name,
                "الوظيفة":e.job,
                "المستحق":e.hours*e.rate,
                "السلف":e.advances,
                "المتبقي":e.hours*e.rate-e.advances
            }
            for e in employees
        ])

    st.dataframe(df, use_container_width=True, hide_index=True)

    st.download_button(
        "⬇️ تحميل التقرير CSV",
        df.to_csv(index=False).encode("utf-8-sig"),
        "mh_group_report.csv",
        "text/csv"
    )

    db.close()

# ---------------- AUDIT ----------------

elif page == "audit":

    st.markdown("# 🧾 سجل العمليات")

    db = Session()
    logs = db.query(Audit).order_by(Audit.id.desc()).limit(500).all()

    import pandas as pd

    df = pd.DataFrame([
        {
            "المستخدم":x.username,
            "العملية":x.action,
            "التاريخ":x.created_at
        }
        for x in logs
    ])

    st.dataframe(df, use_container_width=True, hide_index=True)

    db.close()

# ---------------- SETTINGS ----------------

elif page == "settings":

    st.markdown("# ⚙️ الإعدادات")

    if user["role"] != "admin":
        st.warning("هذه الصفحة متاحة للمدير فقط.")
        st.stop()

    st.markdown("### تغيير كلمة المرور")

    with st.form("password_form"):

        old = st.text_input("كلمة المرور الحالية", type="password")
        new = st.text_input("كلمة المرور الجديدة", type="password")
        confirm = st.text_input("تأكيد كلمة المرور", type="password")

        if st.form_submit_button("🔐 تغيير كلمة المرور"):

            db = Session()
            current = db.query(User).filter_by(
                username=user["username"]
            ).first()

            if not verify_password(old, current.password_hash):
                st.error("كلمة المرور الحالية غير صحيحة.")

            elif len(new) < 10:
                st.error("استخدم كلمة مرور لا تقل عن 10 أحرف.")

            elif new != confirm:
                st.error("كلمتا المرور غير متطابقتين.")

            else:
                current.password_hash = hash_password(new)
                db.commit()
                log_action(user["username"], "تغيير كلمة المرور")
                st.success("تم تغيير كلمة المرور بنجاح.")

            db.close()

st.markdown(
    '<div class="footer">MH GROUP ERP • © 2026 جميع الحقوق محفوظة</div>',
    unsafe_allow_html=True
)
