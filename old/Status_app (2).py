import tkinter as tk
from tkinter import messagebox
import json
import matplotlib.pyplot as plt
import numpy as np

SKILLS_FILE = "skills.json"

# دالة لقراءة المهارات من الملف
def load_skills():
    try:
        with open(SKILLS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# دالة لحفظ المهارات إلى الملف
def save_skills(skills_dict):
    with open(SKILLS_FILE, "w", encoding="utf-8") as f:
        json.dump(skills_dict, f, ensure_ascii=False, indent=2)

# دالة لعرض الرادار
def show_radar(skills_dict):
    labels = list(skills_dict.keys())
    values = list(skills_dict.values())

    num_vars = len(labels)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    values += values[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.plot(angles, values, color='lime', linewidth=2)
    ax.fill(angles, values, color='lime', alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=12, fontweight='bold')
    ax.set_yticklabels([])
    ax.set_ylim(0, 100)
    ax.set_title("ملف المهارات الشخصي", size=16, weight='bold', y=1.08)

    plt.tight_layout()
    plt.show()

# واجهة البرنامج
skills = load_skills()
entries = {}

root = tk.Tk()
root.title("تعديل المهارات")
root.geometry("350x500")

frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="تعديل تقييم المهارات (0 - 100):", font=("Arial", 12, "bold")).pack()

# لكل مهارة نعمل Label + Entry
for skill, value in skills.items():
    row = tk.Frame(frame)
    row.pack(pady=5)
    tk.Label(row, text=skill, width=15, anchor='w').pack(side=tk.LEFT)
    entry = tk.Entry(row, width=5)
    entry.insert(0, str(value))
    entry.pack(side=tk.LEFT)
    entries[skill] = entry  # ← ← ← السطر المهم اللي كان ناقص

# زر الحفظ
def on_save():
    new_skills = {}
    try:
        for skill, entry in entries.items():
            val = int(entry.get())
            if not (0 <= val <= 100):
                raise ValueError
            new_skills[skill] = val
        save_skills(new_skills)
        messagebox.showinfo("تم", "تم حفظ التقييمات بنجاح!")
    except:
        messagebox.showerror("خطأ", "برجاء إدخال أرقام صحيحة بين 0 و 100.")

# زر عرض الرادار
def on_show():
    new_skills = {}
    try:
        for skill, entry in entries.items():
            val = int(entry.get())
            new_skills[skill] = val
        show_radar(new_skills)
    except:
        messagebox.showerror("خطأ", "تأكد من أن كل التقييمات أرقام صحيحة.")

tk.Button(root, text="💾 حفظ التعديلات", command=on_save, bg="lightblue").pack(pady=10)
tk.Button(root, text="📊 عرض المهارات كرادار", command=on_show, bg="lightgreen").pack(pady=5)

root.mainloop()
