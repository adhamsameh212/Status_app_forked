import matplotlib.pyplot as plt
import numpy as np
import json

# قراءة البيانات من ملف JSON
with open("skills.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# ترتيب البيانات
labels = list(data.keys())
values = list(data.values())

# إعدادات الرسم
num_vars = len(labels)
angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
values += values[:1]
angles += angles[:1]

# رسم الرادار
fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
ax.plot(angles, values, color='lime', linewidth=2)
ax.fill(angles, values, color='lime', alpha=0.25)

# التسميات
ax.set_xticks(angles[:-1])
ax.set_xticklabels(labels, fontsize=12, fontweight='bold')

# تخصيص الشكل
ax.set_yticklabels([])
ax.set_ylim(0, 100)
ax.set_title("ملف المهارات الشخصي", size=16, weight='bold', y=1.08)

plt.tight_layout()
plt.show()
