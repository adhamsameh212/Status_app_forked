import json
import os

print("📁 الملف موجود؟", os.path.exists("skills.json"))
with open("skills.json", "r", encoding="utf-8") as f:
    content = f.read()
    print("📄 محتوى الملف:\n", content)
    data = json.loads(content)
    print("✅ تم التحميل بنجاح:", data)
