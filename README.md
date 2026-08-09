# MH Group ERP - Streamlit

واجهة ERP عربية RTL لشركة MH Group، مصممة بأسلوب Dark + Gold.

## التشغيل محليًا

```bash
pip install -r requirements.txt
streamlit run app.py
```

## النشر على Streamlit Community Cloud

1. ارفع `app.py` و `requirements.txt` إلى GitHub.
2. افتح Streamlit Community Cloud.
3. اختر المستودع.
4. اختر ملف `app.py`.
5. Deploy.

> هذه النسخة تستخدم بيانات داخل Session State لأغراض الواجهة والتجربة.
> للاستخدام الفعلي يجب ربطها بقاعدة بيانات مثل PostgreSQL أو SQLite مع نظام تسجيل دخول وصلاحيات حقيقي.
