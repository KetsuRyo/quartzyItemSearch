import tkinter as tk
from tkinter import filedialog, ttk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import messagebox
import csv



class DetailPopup(tk.Toplevel):
    def __init__(self, master=None, **kw):
        super().__init__(master=master, **kw)
        self.title("Details")
        self.geometry("400x600")  # 可以根据需要调整大小
        self.content_frame = tk.Frame(self)
        self.content_frame.pack(expand=True, fill=tk.BOTH)

    def update_content(self, details):
        # 清除当前内容
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # 填充新的详细信息
        for detail in details:
            tk.Label(self.content_frame, text=detail, wraplength=380).pack(anchor='w', padx=10, pady=5)

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Loader and Analyzer")
        self.detail_popup = None

        self.notebook = ttk.Notebook(self.root)
        
        self.upload_tab = tk.Frame(self.notebook)
        self.qty_search_tab = tk.Frame(self.notebook)
        self.money_search_tab = tk.Frame(self.notebook)
        
        self.notebook.add(self.upload_tab, text="Upload")
        self.notebook.add(self.qty_search_tab, text="SearchForQty")
        self.notebook.add(self.money_search_tab, text="SearchForMoney")
        
        self.notebook.pack(expand=1, fill="both")
        self.detail_search_tab = tk.Frame(self.notebook)
        self.notebook.add(self.detail_search_tab, text="SearchForDetail")
        self.setup_detail_search_tab(self.detail_search_tab)

        self.setup_upload_tab()
        self.setup_search_tab(self.qty_search_tab, 'Qty')
        self.setup_search_tab(self.money_search_tab, 'Total Money', is_money=True)

        self.data = None
        self.aggregated_data = None
    def setup_detail_search_tab(self, parent):
        search_var = tk.StringVar()
        search_entry = tk.Entry(parent, textvariable=search_var)
        search_entry.pack()

        search_button = tk.Button(parent, text="Search", command=lambda: self.perform_detail_search(search_var.get().lower(), parent))
        search_button.pack()

        self.detail_results_frame = tk.Frame(parent)
        self.detail_results_frame.pack()
    def perform_detail_search(self, search_term, parent):
        filtered_data = self.data[self.data['Item Name'].str.lower().str.contains(search_term)]
        
        # 假设 self.detail_results_frame 是在 setup_detail_search_tab 中创建的用于显示搜索结果的 Frame
        for widget in self.detail_results_frame.winfo_children():
            widget.destroy()  # 清除旧的搜索结果

        # 找到所有匹配的 Item Names 并去重
        unique_items = filtered_data['Item Name'].drop_duplicates()

        for item_name in unique_items:
            tk.Button(self.detail_results_frame, text=item_name, command=lambda item=item_name: self.show_item_monthly_details(item)).pack()

    def on_detail_popup_close(self):
        self.detail_popup.destroy()  # 显式销毁窗口
        self.detail_popup = None  # 重置 self.detail_popup 变量

    def clean_column_names(self, df):
        df.columns = df.columns.str.replace('="', '', regex=False)
        df.columns = df.columns.str.replace('"', '', regex=False)
        return df

    def show_item_monthly_details(self, item_name):
        # 基于选定的 Item Name, 找到所有相关的订单并按月份聚合
        item_data = self.data[self.data['Item Name'] == item_name]
        monthly_counts = item_data.groupby('Month').size().reset_index(name='Counts')

        if not self.detail_popup or not self.detail_popup.winfo_exists():
            self.detail_popup = tk.Toplevel()
            self.detail_popup.title(f"Details for {item_name}")
            
            # 当窗口关闭时，重置 self.detail_popup 为 None
            self.detail_popup.protocol("WM_DELETE_WINDOW", self.on_detail_popup_close)
        else:
            self.detail_popup.title(f"Monthly Details for {item_name}")
            for widget in self.detail_popup.winfo_children():
                widget.destroy()
            self.detail_popup.title(f"Monthly Details for {item_name}")
        
        for _, row in monthly_counts.iterrows():
            month = row['Month']
            counts = row['Counts']
            btn_text = f"{month} {counts}次"
            tk.Button(self.detail_popup, text=btn_text, command=lambda m=month: self.show_date_details(item_name, m)).pack()
    def show_months(self, item_name):
        filtered_data = self.data[self.data['Item Name'] == item_name]
        count_by_month = filtered_data.groupby('Month').size().reset_index(name='Counts')
        
        top = tk.Toplevel()
        top.title(f"Order counts for {item_name}")

        for _, row in count_by_month.iterrows():
            month = row['Month']
            counts = row['Counts']
            btn_text = f"{month} {counts}次"
            tk.Button(top, text=btn_text, command=lambda m=row['Month']: self.show_month_details(item_name, m)).pack()

    def setup_upload_tab(self):
        self.load_button = tk.Button(self.upload_tab, text="Load CSV", command=self.load_csv)
        self.load_button.pack()
    
    def clean_value(self, value):
        """移除字段值中的特殊格式"""
        if isinstance(value, str):
            return value.strip('="').rstrip('"')
        return value

    def load_csv(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            # 使用 on_bad_lines='skip' 跳过不良行
            self.data = pd.read_csv(file_path, on_bad_lines='skip')
            
            # 清理列名
            self.data.columns = [self.clean_value(col) for col in self.data.columns]

            # 清理数据
            for col in self.data.columns:
                self.data[col] = self.data[col].apply(self.clean_value)

            self.process_data()  # 调用处理数据的方法
            messagebox.showinfo("读取完成", "CSV 文件读取并处理完成。")
            self.switch_to_search_for_qty_tab()  # 切换到 SearchForQty 选项卡


    def switch_to_search_for_qty_tab(self):
        # 找到 "SearchForQty" 页面的索引
        search_tab_index = None
        for i, tab in enumerate(self.notebook.tabs()):
            if "SearchForQty" in self.notebook.tab(tab, "text"):
                search_tab_index = i
                break
        
        # 如果找到了 "SearchForQty" 页面，则自动切换到该页面
        if search_tab_index is not None:
            self.notebook.select(search_tab_index)

            
    def process_data(self):
        self.data['Date Ordered'] = pd.to_datetime(self.data['Date Ordered'])
        self.data['Month'] = self.data['Date Ordered'].dt.to_period('M').astype(str)  # 将日期转换为月份字符串
        # 累加 "Total Price"
        self.aggregated_data = self.data.groupby(['Item Name', 'Month']).agg({'Qty': 'sum', 'Total Price': 'sum'}).reset_index()

    def setup_search_tab(self, parent, measure, is_money=False):
        search_var = tk.StringVar()
        search_entry = tk.Entry(parent, textvariable=search_var)
        search_entry.pack()

        search_button = tk.Button(parent, text="Search", command=lambda: self.perform_search(search_var.get().lower(), parent, measure, is_money))
        search_button.pack()

        search_results_frame = tk.Frame(parent)
        search_results_frame.pack()
        
        setattr(self, f"{parent}_results_frame", search_results_frame)
    def show_date_details(self, item_name, month):
        if self.detail_popup:
            self.detail_popup.destroy()  # 如果已有弹出窗口，则销毁
        self.detail_popup = tk.Toplevel()  # 创建新的弹出窗口
        self.detail_popup.title(f"Details for {item_name} in {month}")

        # 筛选指定月份的订单
        month_data = self.data[(self.data['Item Name'] == item_name) & (self.data['Month'].str.startswith(month))]
        unique_dates = month_data['Date Ordered'].dt.strftime('%Y-%m-%d').unique()

        for date in unique_dates:
            btn_text = f"Order on {date}"
            tk.Button(self.detail_popup, text=btn_text, command=lambda d=date: self.show_order_details(item_name, month, d)).pack()

    def show_order_details(self, item_name, month, date):
        if self.detail_popup:
            for widget in self.detail_popup.winfo_children():
                widget.destroy()  # 清空当前弹出窗口中的内容，而不是创建新窗口

        # 根据日期筛选订单
        specific_order_data = self.data[(self.data['Item Name'] == item_name) & (self.data['Date Ordered'].dt.strftime('%Y-%m-%d') == date)]

        # 显示选定订单的详细信息
        for index, row in specific_order_data.iterrows():
            for col in self.data.columns:
                tk.Label(self.detail_popup, text=f"{col}: {row[col]}").pack()

    def perform_search(self, search_term, parent, measure, is_money):
        filtered_data = self.aggregated_data[self.aggregated_data['Item Name'].str.lower().str.contains(search_term)]
        unique_items = filtered_data['Item Name'].unique()
        
        search_results_frame = getattr(self, f"{parent}_results_frame")
        for widget in search_results_frame.winfo_children():
            widget.destroy()

        for item_name in unique_items:
            tk.Button(search_results_frame, text=item_name, command=lambda item=item_name: self.show_item_details(item, measure, is_money)).pack()

    def show_item_details(self, item_name, measure, is_money):
        # 确保使用 "Total Price" 字段
        measure_column = 'Total Price' if is_money else 'Qty'
        item_data = self.aggregated_data[self.aggregated_data['Item Name'] == item_name]
        
        full_range = pd.period_range(start=self.data['Date Ordered'].min(), end=self.data['Date Ordered'].max(), freq='M')
        full_df = pd.DataFrame(full_range, columns=['Month']).astype(str)  # 保证 Month 列为字符串类型

        # 合并数据，并填充未购买月份的数据为0
        merged_data = pd.merge(full_df, item_data, on='Month', how='left').fillna(0)
        merged_data[measure_column] = pd.to_numeric(merged_data[measure_column], errors='coerce').fillna(0)
        
        # 绘制图表
        top = tk.Toplevel()
        top.title(f"{item_name} - {measure_column}")
        fig, ax = plt.subplots()
        merged_data.plot(x='Month', y=measure_column, kind='bar', ax=ax, legend=False)
        ax.set_ylabel('Total Price' if is_money else 'Quantity')
        ax.set_title(f'{item_name} - {"Total Price" if is_money else "Quantity"} by Month')
        chart = FigureCanvasTkAgg(fig, top)
        chart.draw()
        chart.get_tk_widget().pack()






if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()


