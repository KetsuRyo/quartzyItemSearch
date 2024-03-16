import tkinter as tk
from tkinter import filedialog, ttk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import messagebox
from datetime import datetime
from pandas.tseries.offsets import DateOffset



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
        self.setup_search_tab(self.qty_search_tab, 'Qty', 'qty_search')
        self.setup_search_tab(self.money_search_tab, 'Total Price', 'money_search')


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
            if counts == 1:
                btn_text = f"{month} once"
            elif counts == 2:
                btn_text = f"{month} twice"
            else:
                btn_text = f"{month} {counts} times"
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
            messagebox.showinfo("Loading Complete.", "CSV  processed sucessfully.")
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




    def generate_avg_purchase_info(self, tab_id, measure):
        selected_items = getattr(self, f"{tab_id}_selected_items")
        if not selected_items:
            messagebox.showwarning("Warning", "Please choose at least one option!")
            return

        # 筛选并处理数据
        filtered_data = self.data[self.data['Item Name'].isin(selected_items)]
        # 确保 'Total Price' 或 'Qty' 列为数值类型
        filtered_data[measure] = pd.to_numeric(filtered_data[measure], errors='coerce').fillna(0)

        if filtered_data.empty:
            messagebox.showinfo("Info", "No purchase records for selected items.")
            return

        # 计算起止时间
        start_date = filtered_data['Date Ordered'].min()
        end_date = pd.Timestamp.now()  # 获取今天的日期
        total_months = (end_date.year - start_date.year) * 12 + end_date.month - start_date.month + 1

        # 计算总次数和总量或总金额
        total_purchases = len(filtered_data)
        total_measure = filtered_data[measure].sum()
        avg_purchases_per_month = total_purchases / total_months  # 平均每月购买次数

        # 根据measure调整显示的信息
        if measure == 'Qty':
            avg_measure_per_month = total_measure / total_months
            info_text = f'All selected items from {start_date.strftime("%Y-%m")} to now, average {avg_measure_per_month:.2f} items per month, purchased {avg_purchases_per_month:.2f} times per month.'
        elif measure == 'Total Price':
            avg_measure_per_month = total_measure / total_months
            info_text = f'All selected items from {start_date.strftime("%Y-%m")} to now, spent an average of ${avg_measure_per_month:.2f} per month, purchased {avg_purchases_per_month:.2f} times per month.'

        # 显示图表和信息
        top = tk.Toplevel()
        top.title("Average Purchase Info")
        tk.Label(top, text=info_text).pack(pady=10)  # 显示信息






    def setup_search_tab(self, parent, measure, tab_id):
        search_var = tk.StringVar()
        search_entry = tk.Entry(parent, textvariable=search_var)
        search_entry.pack(pady=5)  # Add some padding for visual separation

        button_frame = tk.Frame(parent)
        button_frame.pack(pady=5)  # Adjust padding as needed

        search_button = tk.Button(button_frame, text="Search", command=lambda: self.perform_search(search_var.get().lower(), parent, measure, tab_id))
        search_button.pack(side=tk.LEFT, padx=5)  # Adjust padding as needed

        merge_button = tk.Button(button_frame, text="Graph Generate", command=lambda: self.merge_and_show_chart(parent, measure, tab_id))
        merge_button.pack(side=tk.LEFT, padx=5)  # Adjust padding as needed
        Avg_button = tk.Button(parent, text="Generate Avg Purchase Info", command=lambda: self.generate_avg_purchase_info(tab_id,measure))
        Avg_button.pack(pady=5)
        clear_selection_button = tk.Button(button_frame, text="Clear Selection", command=lambda: self.clear_selection(tab_id))
        clear_selection_button.pack(side=tk.LEFT, padx=5)  # Adjust padding as needed

        # Creating scrollable area for search results
        canvas = tk.Canvas(parent)
        scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill="y")
        canvas.pack(fill="both", expand=True)  # Fill and expand to ensure it uses all available space

        search_results_frame = tk.Frame(canvas)
        canvas_frame = canvas.create_window((0,0), window=search_results_frame, anchor="center")  # Try to center the window

        # This binds the search_results_frame to resize with the canvas
        search_results_frame.bind("<Configure>", lambda e, canvas=canvas, canvas_frame=canvas_frame: on_frame_configure(e, canvas, canvas_frame))

        # Update scrollregion in a separate function to avoid lambda complexity
        def on_frame_configure(event, canvas, canvas_frame):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Center the canvas_frame horizontally
            canvas.itemconfig(canvas_frame, anchor="center")
            canvas.coords(canvas_frame, (canvas.winfo_width() / 2, 0))

        # 存储重要的属性
        setattr(self, f"{tab_id}_canvas", canvas)
        setattr(self, f"{tab_id}_results_frame", search_results_frame)
        setattr(self, f"{tab_id}_selected_items", [])


    def clear_selection(self, tab_id):
        selected_items = getattr(self, f"{tab_id}_selected_items")
        selected_items.clear()  # Clear the list of selected items

        # Optionally: Update UI to reflect the cleared selection
        search_results_frame = getattr(self, f"{tab_id}_results_frame")
        for widget in search_results_frame.winfo_children():
            if isinstance(widget, tk.Checkbutton):
                widget.deselect()  # Deselect all Checkbuttons


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

    def perform_search(self, search_term, parent, measure, tab_id):
        # Ensure self.data is not None
        if self.data is None:
            messagebox.showinfo("Error", "No data loaded. Please load a CSV file first.")
            return
        
        # Proceed with filtering the data
        valid_data = self.data[self.data['Status'] != 'CANCELLED']

        # 根据搜索词进一步筛选数据
        filtered_data = valid_data[valid_data['Item Name'].str.lower().str.contains(search_term)]
        unique_items = filtered_data['Item Name'].unique()

        # 获取搜索结果框架
        search_results_frame = getattr(self, f"{tab_id}_results_frame")
        
        for widget in search_results_frame.winfo_children():
            widget.destroy()
        selected_items = getattr(self, f"{tab_id}_selected_items")
        selected_items.clear()
        for item_name in unique_items:
            var = tk.BooleanVar()
            chk = tk.Checkbutton(search_results_frame, text=item_name, variable=var,
                                command=lambda item=item_name, v=var: self.on_item_select(item, v, tab_id))
            chk.pack()



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



        setattr(self, f"{parent}_results_frame", search_results_frame)
        setattr(self, f"{parent}_selected_items", [])  # 用于存储选中的项目

    def on_item_select(self, item_name, var, tab_id):
        selected_items = getattr(self, f"{tab_id}_selected_items")
        if var.get():
            # 如果复选框被选中且项目名不在列表中，添加项目名到列表
            if item_name not in selected_items:
                selected_items.append(item_name)
        else:
            # 如果复选框未被选中且项目名在列表中，从列表中移除项目名
            if item_name in selected_items:
                selected_items.remove(item_name)



    def merge_and_show_chart(self, parent, measure, tab_id):
        # Correctly access selected_items using tab_id
        selected_items = getattr(self, f"{tab_id}_selected_items")
        if not selected_items:
            messagebox.showwarning("Warning", "Please Choose at least one option!")
            return

        # The rest of your method's implementation...
        today = pd.Timestamp.now()
        current_month_next = (today + DateOffset(months=1)).strftime('%Y-%m')


        # 筛选并合并选定项目的数据
        filtered_data = self.aggregated_data[self.aggregated_data['Item Name'].isin(selected_items)]
        aggregated_data = filtered_data.groupby('Month').agg({measure: 'sum'}).reset_index()

        # 确保 'Month' 列为字符串类型
        aggregated_data['Month'] = aggregated_data['Month'].astype(str)

        # 确保 'Total Price' 或 'Qty' 列为数值类型
        aggregated_data[measure] = pd.to_numeric(aggregated_data[measure], errors='coerce').fillna(0)
        all_months = pd.date_range(start=self.data['Date Ordered'].min(),
                               end=current_month_next,
                               freq='M').strftime('%Y-%m').tolist()
        all_months_df = pd.DataFrame(all_months, columns=['Month'])

        # 合并以确保所有月份都包含在内，对缺失月份填充为0
        final_data = pd.merge(all_months_df, aggregated_data, on='Month', how='left').fillna(0)
        first_item_name = selected_items[0][:4] if len(selected_items[0]) >= 4 else selected_items[0]


        # 显示图表
        top = tk.Toplevel()
        top.title("Merge Graph")
        
        # 调整figsize以提供更多空间给X轴标签
        fig, ax = plt.subplots(figsize=(10, 6))  # 根据需要调整figsize
        
        final_data.plot(x='Month', y=measure, kind='bar', ax=ax, legend=False)
        ax.set_ylabel(measure)
        ax.set_title(f"QueryData of {first_item_name} - {measure} by Month")
        
        # 旋转X轴标签以防重叠，调整间隔
        plt.xticks(rotation=45, ha="right")  # ha="right" 使标签稍微倾斜，以获得更好的布局
        
        # 使用tight_layout自动调整子图参数，填充整个图表区域并减少重叠
        plt.tight_layout()
        
        chart = FigureCanvasTkAgg(fig, top)  # 创建图表
        chart.draw()
        chart.get_tk_widget().pack(fill=tk.BOTH, expand=True)  # 确保图表填充整个顶级窗口并可以展开





if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()


