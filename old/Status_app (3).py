import tkinter as tk
from tkinter import messagebox
import json
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime 
import os

SKILLS_FILE = "skills.json"

# دالة لقراءة المهارات من الملف
def load_skills():
    try:
        with open(SKILLS_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as e:
        print("❌ خطأ في قراءة JSON:", e)
        return []

# دالة لحفظ المهارات إلى الملف
def save_skills(skills_list):
    with open(SKILLS_FILE, "w", encoding="utf-8") as f:
        json.dump(skills_list, f, ensure_ascii=False, indent=2)

# دالة لعرض الرادار
def show_radar(skills_dict):
    if not skills_dict:
        messagebox.showwarning("تحذير", "لا توجد مهارات لعرضها!")
        return

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

# تحديث الواجهة بالكامل بعد إضافة/حذف
def refresh_ui():
    for widget in frame.winfo_children():
        widget.destroy()
    entries.clear()
    build_ui()

# دالة لحذف مهارة
def delete_skill(skill_name):
    global skills
    skills = [s for s in skills if s["name"] != skill_name]
    save_skills(skills)
    refresh_ui()

# إضافة أو تعديل مهارة جديدة
def add_or_update_skill():
    name = add_name_entry.get().strip()
    try:
        val = int(add_value_entry.get())
        if not name or not (0 <= val <= 100):
            raise ValueError

        found = False
        for skill_obj in skills:
            if skill_obj["name"] == name:
                skill_obj["value"] = val
                found = True
                break

        if not found:
            skills.append({"name": name, "value": val})

        save_skills(skills)
        refresh_ui()
    except:
        messagebox.showerror("خطأ", "تأكد من إدخال اسم وقيمة صحيحة بين 0 و 100.")


def save_snapshot():
    try:
        with open("skills.json", "r") as f:
            data = json.load(f)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        snapshot = {
            "timestamp": timestamp,
            "skills": data
        }

        # تحميل الملف القديم أو إنشاء قائمة جديدة
        if os.path.exists("history.json"):
            with open("history.json", "r") as f:
                history = json.load(f)
        else:
            history = []

        history.append(snapshot)

        with open("history.json", "w") as f:
            json.dump(history, f, indent=4)

        messagebox.showinfo("تم الحفظ", f"تم حفظ لقطة بتاريخ {timestamp}")
    except Exception as e:
        messagebox.showerror("خطأ", f"حدث خطأ أثناء الحفظ: {e}")


# بناء عناصر المهارات في الواجهة
def build_ui():
    global add_name_entry, add_value_entry,skills
    skills = load_skills()

    tk.Label(frame, text="تقييم المهارات (0 - 100):", font=("Arial", 12, "bold")).pack()
    for skill_obj in skills:
        print("Skill object:", skill_obj, type(skill_obj))
        skill = skill_obj["name"]
        value = skill_obj["value"]
        row = tk.Frame(frame)
        row.pack(pady=5, fill="x")
        tk.Label(row, text=skill, width=15, anchor='w').pack(side=tk.LEFT)
        entry = tk.Entry(row, width=5)
        entry.insert(0, str(value))
        entry.pack(side=tk.LEFT)
        entries[skill] = entry

        del_btn = tk.Button(row, text="🗑", command=lambda s=skill: delete_skill(s), bg="red", fg="white")
        del_btn.pack(side=tk.RIGHT)

    # مساحة للإضافة
    tk.Label(frame, text="\n➕ إضافة / تعديل مهارة:", font=("Arial", 11, "bold")).pack()

    add_row = tk.Frame(frame)
    add_row.pack(pady=5)
    tk.Label(add_row, text="الاسم:", width=7).pack(side=tk.LEFT)
    add_name_entry = tk.Entry(add_row, width=10)
    add_name_entry.pack(side=tk.LEFT)
    tk.Label(add_row, text="القيمة:", width=7).pack(side=tk.LEFT)
    add_value_entry = tk.Entry(add_row, width=5)
    add_value_entry.pack(side=tk.LEFT)

    tk.Button(frame, text="➕ إضافة / تعديل", command=add_or_update_skill, bg="lightyellow").pack(pady=5)



# تنفيذ الحفظ
def on_save():
    try:
        for skill_obj in skills:
            name = skill_obj["name"]
            if name in entries:
                val = int(entries[name].get())
                skill_obj["value"] = val
            if not (0 <= val <= 100):
                raise ValueError
        save_skills(skills)
        messagebox.showinfo("تم", "تم حفظ التعديلات.")
    except:
        messagebox.showerror("خطأ", "برجاء إدخال أرقام صحيحة بين 0 و 100.")


# عرض الرادار
def on_show():
    try:
        temp_skills = {}
        for skill_obj in skills:
            name = skill_obj["name"]
            val = int(entries[name].get())
            temp_skills[name] = val
        show_radar(temp_skills)
    except:
        messagebox.showerror("خطأ", "تأكد من أن كل التقييمات أرقام صحيحة.")


# نافذة البرنامج
skills = load_skills()
entries = {}

root = tk.Tk()
root.title("إدارة المهارات")
root.geometry("400x600")

frame = tk.Frame(root)
frame.pack(pady=10)

# بناء واجهة البداية
build_ui()

# أزرار الحفظ والعرض
tk.Button(root, text="💾 حفظ التعديلات", command=on_save, bg="lightblue").pack(pady=10)
tk.Button(root, text="📊 عرض الرادار", command=on_show, bg="lightgreen").pack(pady=5)
tk.Button(root, text="📸 حفظ لقطة Snapshot", command=save_snapshot, bg="lightgray").pack(pady=10)


root.mainloop()
