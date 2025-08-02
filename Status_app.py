import tkinter as tk
from tkinter import messagebox
import json
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime,timedelta
import os
import shutil
import traceback
from tkinter import simpledialog


SKILLS_FILE = "skills.json"
_last_snapshot_time = None  # متغير عام global تضعه في أول ملف GUI


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

    # ⬇⬇ إضافة أخذ نسخة snapshot تلقائيًا بعد الحفظ ⬇⬇
    try:
        # 🟨 حمّل آخر Snapshot موجود (لو فيه)
        snapshot_folder = "snapshots"
        os.makedirs(snapshot_folder, exist_ok=True)
        snapshots = sorted(os.listdir(snapshot_folder))
        if snapshots:
            last_snapshot_path = os.path.join(snapshot_folder, snapshots[-1])
            with open(last_snapshot_path, "r", encoding="utf-8") as f:
                last_snapshot = json.load(f)
        else:
            last_snapshot = []

        # ✅ قارن بين الحالة الحالية وآخر Snapshot
        if skills_list != last_snapshot:
            now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            shutil.copy(SKILLS_FILE, os.path.join(snapshot_folder, f"{now}.json"))
        # ❌ لو نفس الحالة، تجاهل snapshot

    except Exception as e:
        messagebox.showerror("خطأ في أخذ Snapshot", f"لم يتم حفظ نسخة احتياطية:\n{e}")


    

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
    global _last_snapshot_time
    now = datetime.now()

    if _last_snapshot_time and (now - _last_snapshot_time) < timedelta(seconds=5):
        print("⛔ تم تجاهل الحفظ لتكراره خلال 5 ثواني.")
        return

    _last_snapshot_time = now

    print(f"🔄 حفظ Snapshot عند: {now}")
    try:
        with open("skills.json", "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                raise ValueError("ملف المهارات فارغ!")
            data = json.loads(content)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        snapshot = {
            "timestamp": timestamp,
            "skills": data
        }

        history = []
        if os.path.exists("history.json"):
            with open("history.json", "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    history = json.loads(content)

        history.append(snapshot)

        with open("history.json", "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=4)

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



def show_history_window():
    history_win = tk.Toplevel(root)
    history_win.title("📅 الحالات السابقة")
    history_win.geometry("400x600")

    tk.Label(history_win, text="اختر تاريخ الحالة:").pack(pady=10)

    snapshot_folder = "snapshots"
    if not os.path.exists(snapshot_folder):
        tk.Label(history_win, text="لا توجد حالات محفوظة بعد.").pack(pady=20)
        return

    files = sorted(os.listdir(snapshot_folder), reverse=True)  # الأحدث أولًا
    for filename in files:
        if filename.endswith(".json"):
            date_str = filename.replace(".json", "")
            frame = tk.Frame(history_win)
            frame.pack(pady=5)

            tk.Label(frame, text=date_str).pack(side=tk.LEFT, padx=5)

            # زر فتح السناب شوت
            tk.Button(frame, text="👁️ عرض", command=lambda f=filename: show_snapshot_radar_from_file(f)).pack(side=tk.LEFT)

            # زر تعديل الاسم
            tk.Button(frame, text="✏️ تعديل الاسم", command=lambda f=filename: rename_snapshot_prompt(f, history_win)).pack(side=tk.LEFT, padx=5)

            # زر حذف السناب شوت (تم تعديله ليأخذ اسم الملف)
            tk.Button(frame, text="🗑️ حذف", command=lambda f=filename: delete_snapshot(f, history_win)).pack(side=tk.LEFT, padx=5)




def rename_snapshot_prompt(filename, parent_window):
    old_path = os.path.join("snapshots", filename)
    date_part = filename.replace(".json", "").split("__")[0]  # نأخذ الجزء الخاص بالتاريخ فقط

    # نافذة صغيرة لطلب الاسم الجديد
    rename_win = tk.Toplevel(parent_window)
    rename_win.title("✏️ إعادة التسمية")
    rename_win.geometry("300x150")

    tk.Label(rename_win, text=f"أدخل وصفًا للحالة:\n(سيُضاف بعد التاريخ)").pack(pady=10)
    entry = tk.Entry(rename_win, width=30)
    entry.pack(pady=5)

    def apply_rename():
        new_description = entry.get().strip().replace(" ", "_")
        if not new_description:
            messagebox.showwarning("⚠️ تنبيه", "يجب إدخال وصف جديد.")
            return

        new_filename = f"{date_part}__{new_description}.json"
        new_path = os.path.join("snapshots", new_filename)

        if os.path.exists(new_path):
            messagebox.showerror("❌ خطأ", "يوجد ملف بنفس الاسم بالفعل!")
        else:
            os.rename(old_path, new_path)
            messagebox.showinfo("✅ تم", "تم تعديل الاسم بنجاح.")
            rename_win.destroy()
            parent_window.destroy()
            show_history_window()  # إعادة فتح نافذة التاريخ لتحديثها

    tk.Button(rename_win, text="💾 حفظ", command=apply_rename).pack(pady=10)


def delete_snapshot(filename, parent_window):
    confirm = messagebox.askyesno("تأكيد الحذف", f"هل أنت متأكد من حذف اللقطة:\n{filename}؟")
    if not confirm:
        return

    path = os.path.join("snapshots", filename)
    try:
        os.remove(path)
        messagebox.showinfo("تم الحذف", f"تم حذف {filename} بنجاح.")
        parent_window.destroy()  # إغلاق النافذة الحالية
        show_history_window()    # فتحها من جديد لتحديث العرض
    except Exception as e:
        messagebox.showerror("خطأ", f"فشل حذف الملف:\n{e}")






def show_snapshot_radar_from_file(filename):
    snapshot_path = os.path.join("snapshots", filename)

    try:
        with open(snapshot_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            messagebox.showerror("خطأ", "ملف Snapshot غير صالح.")
            return

        labels = [item["name"] for item in data]
        values = [item["value"] for item in data]

        if not labels or not values:
            messagebox.showinfo("فارغ", "لا توجد مهارات في هذا الـ Snapshot.")
            return

        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        values += values[:1]
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax.plot(angles, values, 'o-', linewidth=2)
        ax.fill(angles, values, alpha=0.25)
        ax.set_thetagrids(np.degrees(angles[:-1]), labels)
        ax.set_title(f"رادار Snapshot - {filename}", fontsize=14)
        ax.grid(True)

        plt.show()

    except Exception:
        messagebox.showerror("خطأ", f"فشل في تحميل Snapshot:\n{traceback.format_exc()}")





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
btn_show_history = tk.Button(root, text="📜 عرض التاريخ", command=show_history_window)
btn_show_history.pack(pady=5)


root.mainloop()
