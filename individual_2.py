#个人任务2
#提供一个文本框
#用于在任务即使期间记笔记


import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from dataclasses import dataclass
from typing import List
import csv

# 任务数据类
@dataclass
class Task:
    name: str
    minutes: int
    notes: str = ""  # 新增笔记字段

# 任务列表管理类
class TaskList:
    def __init__(self):
        self._tasks: List[Task] = []

    def add(self, task: Task):
        self._tasks.append(task)

    def get_all(self) -> List[Task]:
        return self._tasks.copy()

    def delete(self, index: int):
        if 0 <= index < len(self._tasks):
            self._tasks.pop(index)

    def clear(self):
        self._tasks.clear()

    def update(self, index: int, updated_task: Task):
        if 0 <= index < len(self._tasks):
            self._tasks[index] = updated_task

    def get_total_time(self) -> int:
        return sum(task.minutes for task in self._tasks)

    def get_task_count(self) -> int:
        return len(self._tasks)

    def export_to_list(self) -> List[dict]:
        return [{"任务名称": task.name, "时长(分钟)": task.minutes, "笔记": task.notes} for task in self._tasks]

    def import_from_list(self, data: List[dict]):
        self._tasks = [Task(
            name=item["任务名称"],
            minutes=item["时长(分钟)"],
            notes=item.get("笔记", "")  # 导入时兼容无笔记的CSV
        ) for item in data]

# 添加任务对话框（含笔记输入）
class AddTaskDialog(tk.Toplevel):
    def __init__(self, parent, on_ok):
        super().__init__(parent)
        self.title("添加任务")
        self.resizable(False, False)
        self.on_ok = on_ok

        self.transient(parent)
        self.grab_set()

        # 居中显示
        self.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))

        # 创建变量
        self.name_var = tk.StringVar()
        self.min_var = tk.IntVar(value=15)
        self.notes_var = tk.StringVar()  # 笔记变量

        # 任务名称
        ttk.Label(self, text="任务名称:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.entry = ttk.Entry(self, textvariable=self.name_var, width=30)
        self.entry.grid(row=0, column=1, padx=10)
        self.entry.focus()

        # 时长
        ttk.Label(self, text="时长(分钟):").grid(row=1, column=0, padx=10, sticky="e")
        ttk.Spinbox(self, from_=1, to=180, textvariable=self.min_var, width=10).grid(row=1, column=1, padx=10)

        # 笔记（新增）
        ttk.Label(self, text="任务笔记:").grid(row=2, column=0, padx=10, pady=10, sticky="ne")
        self.notes_text = tk.Text(self, width=30, height=5)  # 多行文本框
        self.notes_text.grid(row=2, column=1, padx=10, pady=10)

        # 按钮框架
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=15)
        ttk.Button(btn_frame, text="确定", command=self._ok).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="取消", command=self.destroy).pack(side="left")

        # 绑定回车键
        self.bind('<Return>', lambda e: self._ok())

    def _ok(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("警告", "任务名称不能为空！")
            self.entry.focus()
            return

        try:
            minutes = self.min_var.get()
            if minutes <= 0:
                messagebox.showwarning("警告", "时长必须大于0分钟！")
                return
        except tk.TclError:
            messagebox.showwarning("警告", "请输入有效的时长！")
            return

        # 获取笔记内容
        notes = self.notes_text.get("1.0", tk.END).strip()  # 从第一行第一列到末尾
        task = Task(name=name, minutes=minutes, notes=notes)
        self.on_ok(task)
        self.destroy()

# 主程序
class MainApp:
    def __init__(self, root_window: tk.Tk):
        self.root = root_window
        root_window.title("任务管理器（含笔记功能）")
        root_window.geometry("600x500")
        self.task_list = TaskList()

        # 顶部标题
        title_label = ttk.Label(root_window, text="任务管理器（支持笔记记录）", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # 按钮框架
        btn_frame = ttk.Frame(root_window)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="+ 添加任务", command=self._open_add_dialog).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🗑️ 删除选中", command=self._delete_selected).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🗑️ 清空所有", command=self._clear_all).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="📊 统计信息", command=self._show_stats).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="📥 导入CSV", command=self._import_csv).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="📤 导出CSV", command=self._export_csv).pack(side="left", padx=5)

        # 统计信息
        self.stats_frame = ttk.LabelFrame(root_window, text="统计信息", padding=10)
        self.stats_frame.pack(fill="x", padx=20, pady=5)
        self.total_tasks_label = ttk.Label(self.stats_frame, text="总任务数: 0")
        self.total_tasks_label.pack(side="left", padx=20)
        self.total_time_label = ttk.Label(self.stats_frame, text="总时长: 0 分钟")
        self.total_time_label.pack(side="left", padx=20)

        # 任务列表Treeview（新增笔记列）
        tree_frame = ttk.Frame(root_window)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)
        columns = ("#1", "#2", "#3", "#4")  # 新增第4列用于显示笔记摘要
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)
        self.tree.heading("#1", text="序号")
        self.tree.heading("#2", text="任务名称")
        self.tree.heading("#3", text="时长(分钟)")
        self.tree.heading("#4", text="笔记摘要")  # 新增列标题

        # 设置列宽
        self.tree.column("#1", width=60, anchor="center")
        self.tree.column("#2", width=150)
        self.tree.column("#3", width=100, anchor="center")
        self.tree.column("#4", width=200)  # 笔记摘要列宽度

        # 滚动条
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 绑定双击事件（编辑任务，含笔记）
        self.tree.bind("<Double-1>", self._edit_task)

        # 初始化显示
        self._refresh_treeview()
        self._update_stats()

    def _open_add_dialog(self):
        dialog = AddTaskDialog(self.root, on_ok=self._on_task_added)
        self.root.wait_window(dialog)

    def _on_task_added(self, task):
        self.task_list.add(task)
        self._refresh_treeview()
        self._update_stats()

    def _refresh_treeview(self):
        self.tree.delete(*self.tree.get_children())
        tasks = self.task_list.get_all()
        for i, task in enumerate(tasks, 1):
            # 笔记摘要（截取前20个字符，超出显示...）
            note_summary = task.notes[:20] + "..." if len(task.notes) > 20 else task.notes
            self.tree.insert("", "end", values=(i, task.name, task.minutes, note_summary))

    def _update_stats(self):
        total_tasks = self.task_list.get_task_count()
        total_time = self.task_list.get_total_time()
        self.total_tasks_label.config(text=f"总任务数: {total_tasks}")
        self.total_time_label.config(text=f"总时长: {total_time} 分钟")

    def _delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要删除的任务！")
            return
        if messagebox.askyesno("确认删除", "确定要删除选中的任务吗？"):
            for item in reversed(selected):
                index = self.tree.index(item)
                self.task_list.delete(index)
            self._refresh_treeview()
            self._update_stats()

    def _clear_all(self):
        if not self.task_list.get_all():
            messagebox.showinfo("提示", "任务列表已经是空的！")
            return
        if messagebox.askyesno("确认清空", "确定要清空所有任务吗？"):
            self.task_list.clear()
            self._refresh_treeview()
            self._update_stats()

    def _show_stats(self):
        tasks = self.task_list.get_all()
        total_tasks = len(tasks)
        total_time = sum(task.minutes for task in tasks)
        if total_tasks == 0:
            messagebox.showinfo("统计信息", "当前没有任务")
            return
        avg_time = total_time / total_tasks if total_tasks > 0 else 0
        task_details = "\n".join([
            f"{i + 1}. {task.name} ({task.minutes}分钟)\n   笔记: {task.notes if task.notes else '无'}"
            for i, task in enumerate(tasks)
        ])
        messagebox.showinfo("详细统计",
                            f"总任务数: {total_tasks}\n"
                            f"总时长: {total_time} 分钟\n"
                            f"平均时长: {avg_time:.1f} 分钟\n\n"
                            f"任务详情:\n{task_details}")

    def _edit_task(self, event=None):
        selected = self.tree.selection()
        if selected:
            item = selected[0]
            index = self.tree.index(item)
            tasks = self.task_list.get_all()
            if 0 <= index < len(tasks):
                self._open_edit_dialog(index, tasks[index])

    def _open_edit_dialog(self, index, task):
        dialog = tk.Toplevel(self.root)
        dialog.title("编辑任务")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 100, self.root.winfo_rooty() + 100))

        # 任务名称
        ttk.Label(dialog, text="任务名称:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        name_var = tk.StringVar(value=task.name)
        name_entry = ttk.Entry(dialog, textvariable=name_var, width=30)
        name_entry.grid(row=0, column=1, padx=10)
        name_entry.focus()

        # 时长
        ttk.Label(dialog, text="时长(分钟):").grid(row=1, column=0, padx=10, sticky="e")
        min_var = tk.IntVar(value=task.minutes)
        ttk.Spinbox(dialog, from_=1, to=180, textvariable=min_var, width=10).grid(row=1, column=1, padx=10)

        # 笔记（编辑模式，保留原有内容）
        ttk.Label(dialog, text="任务笔记:").grid(row=2, column=0, padx=10, pady=10, sticky="ne")
        notes_text = tk.Text(dialog, width=30, height=5)
        notes_text.grid(row=2, column=1, padx=10, pady=10)
        notes_text.insert("1.0", task.notes)  # 填充原有笔记

        def save_changes():
            new_name = name_var.get().strip()
            if not new_name:
                messagebox.showwarning("警告", "任务名称不能为空！")
                return
            new_minutes = min_var.get()
            new_notes = notes_text.get("1.0", tk.END).strip()
            updated_task = Task(name=new_name, minutes=new_minutes, notes=new_notes)
            self.task_list.update(index, updated_task)
            self._refresh_treeview()
            self._update_stats()
            dialog.destroy()

        # 按钮
        btn_frame = ttk.Frame(dialog)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=15)
        ttk.Button(btn_frame, text="保存", command=save_changes).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side="left")

    def _import_csv(self):
        file_path = filedialog.askopenfilename(
            title="选择CSV文件",
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")],
            defaultextension=".csv"
        )
        if not file_path:
            return
        try:
            with open(file_path, mode='r', encoding='utf-8-sig', newline='') as file:
                reader = csv.DictReader(file)
                required_columns = ['任务名称', '时长(分钟)']
                if not all(col in reader.fieldnames for col in required_columns):
                    messagebox.showerror("格式错误", f"缺少必要列：{', '.join(required_columns)}")
                    return
                imported_tasks = []
                line_num = 2
                for row in reader:
                    name = row['任务名称'].strip()
                    dur_str = row['时长(分钟)'].strip()
                    notes = row.get('笔记', '').strip()  # 兼容无笔记列的CSV
                    if not name:
                        messagebox.showwarning("警告", f"第{line_num}行：任务名称为空，已跳过")
                        line_num += 1
                        continue
                    try:
                        dur = int(dur_str)
                        if dur <= 0:
                            raise ValueError
                    except ValueError:
                        messagebox.showwarning("警告", f"第{line_num}行：时长无效，已跳过")
                        line_num += 1
                        continue
                    imported_tasks.append(Task(name, dur, notes))
                    line_num += 1
                if not imported_tasks:
                    messagebox.showinfo("提示", "无有效任务可导入")
                    return
                if self.task_list.get_all() and messagebox.askyesno("确认", "是否清空现有任务？"):
                    self.task_list.clear()
                for task in imported_tasks:
                    self.task_list.add(task)
                self._refresh_treeview()
                self._update_stats()
                messagebox.showinfo("成功", f"导入{len(imported_tasks)}个任务")
        except Exception as e:
            messagebox.showerror("错误", f"导入失败：{str(e)}")

    def _export_csv(self):
        tasks = self.task_list.get_all()
        if not tasks:
            messagebox.showwarning("提示", "无任务可导出")
            return
        file_path = filedialog.asksaveasfilename(
            title="保存CSV文件",
            filetypes=[("CSV文件", "*.csv")],
            defaultextension=".csv",
            initialfile="任务导出.csv"
        )
        if not file_path:
            return
        try:
            with open(file_path, mode='w', encoding='utf-8-sig', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=['任务名称', '时长(分钟)', '笔记'])
                writer.writeheader()
                for task in tasks:
                    writer.writerow({
                        '任务名称': task.name,
                        '时长(分钟)': task.minutes,
                        '笔记': task.notes
                    })
            messagebox.showinfo("成功", f"导出到：{file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败：{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()