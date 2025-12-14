import tkinter as tk
from tkinter import ttk, messagebox
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float, func
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.exc import IntegrityError
import os

# ---------------------------------------------------------
# بخش ۱: تنظیمات دیتابیس و مدل‌ها (SQLAlchemy Code-First)
# ---------------------------------------------------------

DB_FILE = 'chamran_uni.db'
Base = declarative_base()

# --- تعریف مدل‌ها ---

class Master(Base):
    __tablename__ = 'Master'
    MasterId = Column(Integer, primary_key=True, autoincrement=True)
    Name = Column(String(100), nullable=False) 
    Graduation = Column(String(50))
    Mobile = Column(String(20), nullable=False)
    Email = Column(String(100), nullable=True)
    presentations = relationship("Presentation", back_populates="master")
    COLUMNS = {"ID": "MasterId", "نام استاد": "Name", "مدرک": "Graduation", "موبایل": "Mobile", "ایمیل": "Email"}

class Lesson(Base):
    __tablename__ = 'Lesson'
    LessonId = Column(Integer, primary_key=True, autoincrement=True)
    Name = Column(String(100), nullable=False)
    Unit = Column(Integer, nullable=False)     
    Major = Column(String(50), nullable=False) 
    presentations = relationship("Presentation", back_populates="lesson") 
    COLUMNS = {"ID": "LessonId", "نام درس": "Name", "تعداد واحد": "Unit", "رشته": "Major"}

class Presentation(Base):
    __tablename__ = 'Presentation'
    PresentationId = Column(Integer, primary_key=True, autoincrement=True)
    MasterId = Column(Integer, ForeignKey('Master.MasterId'), nullable=False)
    LessonId = Column(Integer, ForeignKey('Lesson.LessonId'), nullable=False)
    DayHold = Column(String(50))
    StartTime = Column(Integer)
    FinishTime = Column(Integer)
    master = relationship("Master", back_populates="presentations")
    lesson = relationship("Lesson", back_populates="presentations") 
    selections = relationship("Selection", back_populates="presentation")
    COLUMNS = {"ID": "PresentationId", "نام استاد": "MasterId", "نام درس": "LessonId", "روز": "DayHold", "شروع": "StartTime", "پایان": "FinishTime"}

class Student(Base):
    __tablename__ = 'Student'
    IdStudent = Column(Integer, primary_key=True, autoincrement=True)
    Name = Column(String(100), nullable=False)
    EntranceTerm = Column(String(10)) 
    Graduation = Column(String(50))
    Mobile = Column(String(20), nullable=False)
    Email = Column(String(100), nullable=True)
    Major = Column(String(50), nullable=False) 
    selections = relationship("Selection", back_populates="student")
    COLUMNS = {"ID": "IdStudent", "نام دانشجو": "Name", "ترم ورود": "EntranceTerm", "مقطع": "Graduation", "موبایل": "Mobile", "ایمیل": "Email", "رشته": "Major"}

class Selection(Base):
    __tablename__ = 'Selection'
    IdSelection = Column(Integer, primary_key=True, autoincrement=True)
    IdStudent = Column(Integer, ForeignKey('Student.IdStudent'), nullable=False)
    IdPresentation = Column(Integer, ForeignKey('Presentation.PresentationId'), nullable=False)
    Score = Column(Float, nullable=True) 
    YearEducation = Column(Integer)
    student = relationship("Student", back_populates="selections")
    presentation = relationship("Presentation", back_populates="selections")
    COLUMNS = {"ID": "IdSelection", "نام دانشجو": "IdStudent", "درس ارائه شده": "IdPresentation", "نمره": "Score", "سال": "YearEducation"}


# پیکربندی اتصال
engine = create_engine(f'sqlite:///{DB_FILE}', echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# ---------------------------------------------------------
# بخش ۲: رابط کاربری (GUI با Tkinter)
# ---------------------------------------------------------

class ChamranApp:
    def __init__(self, root):
        self.root = root
        self.root.title("سیستم مدیریت آموزشی دانشگاه چمران")
        self.root.geometry("1000x750") 
        
        try:
            self.main_font = ('B Nazanin', 12)
            self.header_font = ('B Nazanin', 14, 'bold')
        except:
            self.main_font = ('Arial', 12)
            self.header_font = ('Arial', 14, 'bold')
            
        self.session = Session()
        self.setup_styles()

        self.majors_list = ['کامپیوتر', 'برق', 'عمران', 'مکانیک', 'معماری', 'سایر']
        self.week_days = ['شنبه', 'یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه']
        self.id_to_name_map = {} 
        self.combo_fk_cache = {} 

        self.tabs_info = {
            'Student': {'text': 'دانشجو', 'model': Student, 'id_field': 'IdStudent', 
                        'fields': [("نام دانشجو", "Name"), 
                                   ("ترم ورود", "EntranceTerm", "str_term_3_digit"), 
                                   ("مقطع", "Graduation"), 
                                   ("موبایل", "Mobile"), ("ایمیل", "Email", "str_optional"),
                                   ("رشته تحصیلی", "Major", "combo", self.majors_list)]},
            'Master': {'text': 'استاد', 'model': Master, 'id_field': 'MasterId', 
                       'fields': [("نام استاد", "Name"), ("مدرک", "Graduation"), 
                                  ("موبایل", "Mobile"), ("ایمیل", "Email", "str_optional")]},
            'Lesson': {'text': 'درس', 'model': Lesson, 'id_field': 'LessonId', 
                       'fields': [("نام درس", "Name"), ("تعداد واحد", "Unit", "int"),
                                  ("رشته تحصیلی", "Major", "combo", self.majors_list)]},
            'Presentation': {'text': 'ارائه', 'model': Presentation, 'id_field': 'PresentationId', 
                             'fields': [
                                 ("استاد", "MasterId", "combo_fk", Master, 'MasterId', 'Name'), 
                                 ("درس", "LessonId", "combo_fk", Lesson, 'LessonId', 'Name'),   
                                 ("روز برگزاری", "DayHold", "combo", self.week_days),
                                 ("ساعت شروع", "StartTime", "int_optional"), 
                                 ("ساعت پایان", "FinishTime", "int_optional")]},
            'Selection': {'text': 'وضعیت دروس دانشجو', 'model': Selection, 'id_field': 'IdSelection', 
                          'fields': [
                              ("رشته تحصیلی", "MajorFilter", "combo_major_filter", self.majors_list), 
                              ("دانشجو", "IdStudent", "combo_fk_filtered", Student, 'IdStudent', 'Name'), 
                              ("درس (ارائه)", "IdPresentation", "combo_fk_filtered", Presentation, 'PresentationId', 'Display'), 
                              ("سال تحصیلی", "YearEducation", "int_optional"), 
                              ("نمره", "Score", "float_optional")]},
        }

        self.tab_control = ttk.Notebook(root)
        
        for key, info in self.tabs_info.items():
            frame = ttk.Frame(self.tab_control)
            self.tab_control.add(frame, text=info['text'])
            info['frame'] = frame
            self.create_generic_tab(info)
            self.load_foreign_key_comboboxes(key) 

        self.tab_report = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_report, text='گزارش (میانگین نمرات)')
        self.create_report_tab()

        self.tab_control.pack(expand=1, fill="both")
        self.tab_control.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam') 
        style.configure(".", font=self.main_font)
        style.configure("TLabel", font=self.main_font, padding=6)
        style.configure("TButton", font=self.main_font, padding=8, background="#3498db", foreground="black")
        style.configure("TEntry", font=self.main_font, padding=4)
        style.configure("Treeview.Heading", font=self.header_font, background="#e7e7e7")
        style.configure("Treeview", font=self.main_font)

    # ------------------ توابع کمکی برای UI داینامیک ------------------

    def load_foreign_key_comboboxes(self, tab_key):
        """منوهای کشویی کلید خارجی در یک تب مشخص را مجدداً بارگذاری می‌کند."""
        info = self.tabs_info[tab_key]
        
        for label, db_field, *type_info in info['fields']:
            field_type = type_info[0] if type_info else 'str'
            
            if field_type == 'combo_fk':
                fk_model = type_info[1]
                fk_id_field = type_info[2]
                fk_name_field = type_info[3]
                
                combo_widget = self.combo_fk_cache.get((tab_key, db_field))
                if combo_widget:
                    options = self.fetch_combo_options(fk_model, fk_id_field, fk_name_field)
                    current_value = combo_widget.get()
                    combo_widget['values'] = options
                    if current_value in options:
                        combo_widget.set(current_value)
                    else:
                        combo_widget.set('')
        
    def fetch_combo_options(self, fk_model, fk_id_field, fk_name_field, major_filter=None):
        """داده‌ها را از دیتابیس واکشی کرده و map ID به Name را می‌سازد (همراه با فیلتر رشته)."""
        query = self.session.query(fk_model)
        
        if major_filter and major_filter != "سایر":
            if fk_model == Student:
                query = query.filter(Student.Major == major_filter)
            elif fk_model == Lesson:
                query = query.filter(Lesson.Major == major_filter)
        
        options = []
        id_to_name = {}
        
        for record in query.all():
            record_id = getattr(record, fk_id_field)
            
            if fk_model == Presentation:
                master_name = record.master.Name if record.master else 'نامشخص'
                lesson_name = record.lesson.Name if record.lesson else 'نامشخص'
                display_name = f"{lesson_name} ({master_name}, {record.DayHold})"
            else:
                display_name = getattr(record, fk_name_field)
            
            id_to_name[display_name] = record_id
            options.append(display_name)
        
        self.id_to_name_map[(fk_model.__name__, major_filter)] = id_to_name
        return sorted(options)
    
    def update_filtered_combos(self, major):
        """Comboboxهای دانشجو و ارائه را بر اساس رشته تحصیلی انتخاب شده فیلتر می‌کند."""
        info = self.tabs_info['Selection']
        
        student_combo = info['entries']['IdStudent']
        student_options = self.fetch_combo_options(Student, 'IdStudent', 'Name', major_filter=major)
        student_combo['values'] = student_options
        student_combo.set('') 

        presentation_combo = info['entries']['IdPresentation']
        presentation_options = self.fetch_combo_options(Presentation, 'PresentationId', 'Display', major_filter=major)
        presentation_combo['values'] = presentation_options
        presentation_combo.set('') 

    # ------------------ توابع عمومی CRUD و UI ------------------
    
    def create_generic_tab(self, info):
        frame = info['frame']
        model = info['model']
        fields = info['fields']
        tab_key = next(key for key, val in self.tabs_info.items() if val == info)
        
        input_frame = ttk.LabelFrame(frame, text=f"مدیریت {info['text']} (درج / بروزرسانی)", padding="15")
        input_frame.pack(padx=20, pady=10, fill="x")
        
        info['entries'] = {}
        
        for i, (label_text, db_field, *type_info) in enumerate(fields):
            row, col = divmod(i, 3) 
            
            ttk.Label(input_frame, text=f"{label_text}:").grid(row=row, column=col*2, padx=10, pady=5, sticky='w')
            
            field_type = type_info[0] if type_info else 'str'

            if field_type.startswith('combo'):
                
                widget = ttk.Combobox(input_frame, width=18, font=self.main_font, state='readonly') 
                widget.grid(row=row, column=col*2 + 1, padx=10, pady=5, sticky='ew')
                info['entries'][db_field] = widget
                
                if field_type == 'combo': 
                    widget['values'] = type_info[1]
                
                elif field_type == 'combo_fk': 
                    self.combo_fk_cache[(tab_key, db_field)] = widget
                    widget['values'] = [] 
                    
                elif field_type == 'combo_major_filter': 
                    widget['values'] = type_info[1]
                    widget.bind('<<ComboboxSelected>>', lambda event, combo=widget: self.update_filtered_combos(combo.get()))
                
                elif field_type == 'combo_fk_filtered': 
                    widget['values'] = []
                
            else: 
                entry = ttk.Entry(input_frame, width=20)
                entry.grid(row=row, column=col*2 + 1, padx=10, pady=5, sticky='ew')
                info['entries'][db_field] = entry

        btn_frame = ttk.Frame(input_frame)
        btn_frame.grid(row=len(fields)//3 + 1, column=0, columnspan=6, pady=15, sticky='n')

        ttk.Button(btn_frame, text="✅ درج رکورد جدید", command=lambda: self.add_record(model, info)).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="🔄 بروزرسانی (Update)", command=lambda: self.update_record(model, info)).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="❌ حذف رکورد", command=lambda: self.delete_record(model, info)).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="🔃 بازخوانی لیست", command=lambda: self.load_data_and_combos(tab_key)).pack(side=tk.LEFT, padx=10)

        cols_headings = list(model.COLUMNS.keys())
        tree = ttk.Treeview(frame, columns=cols_headings, show="headings")
        
        for col in cols_headings:
            tree.heading(col, text=col)
            tree.column(col, anchor=tk.CENTER, width=150)
            
        tree.pack(fill="both", expand=True, padx=20, pady=10)
        info['treeview'] = tree
        
        tree.bind("<<TreeviewSelect>>", lambda event, i=info: self.load_selected_to_entries(i))
        
        self.load_data(model)

    def load_data_and_combos(self, tab_key):
        """بازخوانی داده‌های جدول فعلی و به‌روزرسانی ComboBoxهای وابسته در دیگر تب‌ها."""
        model = self.tabs_info[tab_key]['model']
        self.load_data(model) 
        
        dependencies = {
            'Master': ['Presentation'],
            'Lesson': ['Presentation'],
            'Student': ['Selection'],
            'Presentation': ['Selection']
        }
        
        if tab_key in dependencies:
            for dependent_tab in dependencies[tab_key]:
                self.load_foreign_key_comboboxes(dependent_tab)
        
        if tab_key in ['Master', 'Lesson']:
             self.load_foreign_key_comboboxes('Presentation')
        
        messagebox.showinfo("عملیات موفق", "داده‌های جدول فعلی و منوهای کشویی وابسته به‌روزرسانی شدند.")
        
    def load_selected_to_entries(self, info):
        selected_item = info['treeview'].focus()
        if not selected_item:
            return
        
        values = info['treeview'].item(selected_item, 'values')
        model = info['model']
        
        pk_val = values[0] 
        
        self.clear_entries(info['entries'].values())
        
        record = self.session.query(model).get(pk_val)
        
        if record:
            for label, db_field, *type_info in info['fields']:
                value = getattr(record, db_field)
                entry = info['entries'][db_field]
                
                field_type = type_info[0] if type_info else 'str'

                if field_type.startswith('combo'):
                    if value is not None:
                        display_value = str(value)
                        
                        if field_type.startswith('combo_fk'):
                            fk_model = type_info[1]
                            
                            if fk_model == Presentation:
                                present = self.session.query(Presentation).get(value)
                                m_name = present.master.Name if present.master else 'نامشخص'
                                l_name = present.lesson.Name if present.lesson else 'نامشخص'
                                display_value = f"{l_name} ({m_name}, {present.DayHold})"
                            else:
                                fk_record = self.session.query(fk_model).get(value)
                                display_value = getattr(fk_record, type_info[3]) if fk_record else str(value)
                        
                        if db_field == 'MajorFilter':
                            if model == Selection and record.student and record.student.Major:
                                entry.set(record.student.Major)
                                self.update_filtered_combos(record.student.Major)
                                continue
                        
                        entry.set(display_value)
                        
                else: 
                    entry.insert(0, str(value) if value is not None else "")
        
    def validate_and_parse_data(self, fields, entries):
        data = {}
        for label, db_field, *type_info in fields:
            if db_field == "MajorFilter": 
                continue 

            value = entries[db_field].get()
            field_type = type_info[0] if type_info else 'str'

            if field_type.startswith('combo'):
                if not value and db_field != 'MajorFilter':
                    raise ValueError(f"لطفاً '{label}' را انتخاب کنید.")
                
                if field_type.startswith('combo_fk'):
                    fk_model = type_info[1]
                    
                    major_filter = entries.get('MajorFilter').get() if entries.get('MajorFilter') else None
                    map_key = (fk_model.__name__, major_filter)

                    id_to_name_map = self.id_to_name_map.get(map_key)
                    if not id_to_name_map or value not in id_to_name_map:
                        raise ValueError(f"مقدار انتخابی برای '{label}' نامعتبر است یا هنوز بارگذاری نشده است.")

                    data[db_field] = id_to_name_map[value]
                
                else: 
                    data[db_field] = value
                
                continue 

            if 'optional' not in field_type and not value:
                raise ValueError(f"فیلد '{label}' نمی‌تواند خالی باشد.")
            
            if not value and 'optional' in field_type:
                data[db_field] = None
                continue

            try:
                if field_type == 'str_term_3_digit':
                    term_str = value
                    if len(term_str) != 3 or not term_str.isdigit():
                         raise ValueError(f"فیلد '{label}' باید یک کد ترم دقیقاً سه‌رقمی و عددی باشد (مانند ۰۱۲).")
                    data[db_field] = term_str
                
                elif 'int' in field_type:
                    data[db_field] = int(value)
                elif 'float' in field_type:
                    data[db_field] = float(value)
                else: 
                    data[db_field] = value
            except ValueError as ve:
                if 'سه‌رقمی' in str(ve):
                    raise ve
                else:
                    raise ValueError(f"فیلد '{label}' باید از نوع {field_type.split('_')[0]} باشد.")
        return data

    # ------------------ توابع عملیات CRUD ------------------
    def add_record(self, model, info):
        try:
            data = self.validate_and_parse_data(info['fields'], info['entries'])
            
            new_record = model(**data)
            self.session.add(new_record)
            self.session.commit()
            
            messagebox.showinfo("موفقیت", f"{info['text']} با موفقیت افزوده شد.")
            self.clear_entries(info['entries'].values())
            
            tab_key = next(key for key, val in self.tabs_info.items() if val['model'] == model)
            self.load_data_and_combos(tab_key) 

            
        except ValueError as e:
            messagebox.showerror("خطای ورودی", str(e))
        except IntegrityError:
             self.session.rollback()
             messagebox.showerror("خطای دیتابیس", "خطا: شناسه خارجی نامعتبر یا فیلد اجباری خالی است.")
        except Exception as e:
            self.session.rollback()
            messagebox.showerror("خطای ناشناخته", str(e))
            
    def update_record(self, model, info):
        selected_item = info['treeview'].focus()
        if not selected_item:
            messagebox.showwarning("هشدار", "لطفاً برای بروزرسانی، یک رکورد را از لیست انتخاب کنید.")
            return

        try:
            pk_val = info['treeview'].item(selected_item, 'values')[0]
            data = self.validate_and_parse_data(info['fields'], info['entries'])
            
            record = self.session.query(model).get(pk_val)
            if not record:
                messagebox.showerror("خطا", "رکورد انتخاب شده در دیتابیس یافت نشد.")
                return

            for key, value in data.items():
                setattr(record, key, value)
            
            self.session.commit()
            messagebox.showinfo("موفقیت", f"{info['text']} با موفقیت بروزرسانی شد.")
            self.clear_entries(info['entries'].values())
            
            tab_key = next(key for key, val in self.tabs_info.items() if val['model'] == model)
            self.load_data_and_combos(tab_key) 

        except ValueError as e:
            messagebox.showerror("خطای ورودی", str(e))
        except IntegrityError:
             self.session.rollback()
             messagebox.showerror("خطای دیتابیس", "خطا: بروزرسانی نامعتبر است (شناسه خارجی اشتباه).")
        except Exception as e:
            self.session.rollback()
            messagebox.showerror("خطای ناشناخته", str(e))

    def delete_record(self, model, info):
        selected_item = info['treeview'].focus()
        if not selected_item:
            messagebox.showwarning("هشدار", "لطفاً برای حذف، یک رکورد را از لیست انتخاب کنید.")
            return

        if not messagebox.askyesno("تأیید حذف", "آیا مطمئن هستید که می‌خواهید این رکورد را حذف کنید؟ این عمل غیرقابل بازگشت است."):
            return

        try:
            pk_val = info['treeview'].item(selected_item, 'values')[0]
            
            record = self.session.query(model).get(pk_val)
            if record:
                self.session.delete(record)
                self.session.commit()
                messagebox.showinfo("موفقیت", f"{info['text']} با موفقیت حذف شد.")
                self.clear_entries(info['entries'].values())
                
                tab_key = next(key for key, val in self.tabs_info.items() if val['model'] == model)
                self.load_data_and_combos(tab_key) 
            else:
                messagebox.showerror("خطا", "رکورد انتخاب شده در دیتابیس یافت نشد.")

        except IntegrityError:
            self.session.rollback()
            messagebox.showerror("خطای وابستگی", "این رکورد به رکوردهای دیگری وابسته است و قابل حذف نیست. ابتدا رکوردهای وابسته را حذف کنید.")
        except Exception as e:
            self.session.rollback()
            messagebox.showerror("خطای ناشناخته", str(e))

    def load_data(self, model):
        for key, info in self.tabs_info.items():
            if info['model'] == model:
                tree = info['treeview']
                
                for i in tree.get_children():
                    tree.delete(i)
                
                data = self.session.query(model).all()
                col_keys = list(model.COLUMNS.values())
                
                for record in data:
                    row = []
                    for attr in col_keys:
                        value = getattr(record, attr)
                        
                        if model == Presentation and attr == 'MasterId':
                            row.append(record.master.Name if record.master else 'نامشخص')
                        elif model == Presentation and attr == 'LessonId':
                            row.append(record.lesson.Name if record.lesson else 'نامشخص')
                        
                        elif model == Selection and attr == 'IdStudent':
                            row.append(record.student.Name if record.student else 'نامشخص')
                        elif model == Selection and attr == 'IdPresentation':
                            if record.presentation:
                                l_name = record.presentation.lesson.Name if record.presentation.lesson else 'نامشخص'
                                m_name = record.presentation.master.Name if record.presentation.master else 'نامشخص'
                                row.append(f"{l_name} ({m_name})")
                            else:
                                row.append('نامشخص')
                        # ------------------------------------
                        
                        else:
                            row.append(value)
                            
                    tree.insert("", "end", values=row)
                break
            
    def clear_entries(self, entries):
        for entry in entries:
            if isinstance(entry, ttk.Combobox):
                 entry.set('')
            else:
                entry.delete(0, tk.END)

    def on_tab_change(self, event):
        selected_tab_index = self.tab_control.index(self.tab_control.select())
        
        if selected_tab_index < len(self.tabs_info):
            tab_key = list(self.tabs_info.keys())[selected_tab_index]
            model = self.tabs_info[tab_key]['model']
            
            self.load_data(model)
            self.load_foreign_key_comboboxes(tab_key)

            if tab_key == 'Selection':
                info = self.tabs_info['Selection']
                info['entries']['MajorFilter'].set('')
                info['entries']['IdStudent'].set('')
                info['entries']['IdPresentation']['values'] = []


    # ------------------ تب محاسبه میانگین (گزارش) ------------------
    def create_report_tab(self):
        frame = ttk.LabelFrame(self.tab_report, text="محاسبه میانگین نمرات دانشجو", padding="20")
        frame.pack(padx=50, pady=50, fill="none", expand=True) 
        
        ttk.Label(frame, text="شناسه دانشجو را وارد کنید:", font=self.main_font).pack(pady=10)
        self.rep_sid = ttk.Entry(frame, width=15, font=self.main_font)
        self.rep_sid.pack(pady=10)

        ttk.Button(frame, text="محاسبه میانگین (GPA)", command=self.calculate_average).pack(pady=20)

        self.lbl_result = ttk.Label(frame, text="---", font=('B Nazanin', 18, 'bold'), foreground="#27ae60")
        self.lbl_result.pack(pady=10)
        
        self.lbl_rank = ttk.Label(frame, text="---", font=('B Nazanin', 14, 'bold'))
        self.lbl_rank.pack(pady=10)
        

    def calculate_average(self):
        st_id_str = self.rep_sid.get()
        
        self.lbl_rank.config(text="---", foreground='black')

        if not st_id_str:
            messagebox.showwarning("هشدار", "لطفاً شناسه دانشجو را وارد کنید")
            return
        
        try:
            st_id = int(st_id_str)
            
            student = self.session.query(Student).filter(Student.IdStudent == st_id).first()
            
            if not student:
                messagebox.showerror("خطا", "دانشجویی با این شناسه یافت نشد.")
                return

            result = self.session.query(
                func.sum(Selection.Score * Lesson.Unit) / func.sum(Lesson.Unit)
            ).select_from(Selection) \
             .join(Presentation) \
             .join(Lesson) \
             .filter(Selection.IdStudent == st_id) \
             .filter(Selection.Score != None) \
             .scalar()
            
            st_name = student.Name

            if result is not None:
                gpa = result
                self.lbl_result.config(text=f"میانگین وزنی نمرات {st_name}: {gpa:.2f}", foreground="#000000")
                
                rank_text = ""
                rank_color = "black"

                if 0 <= gpa < 9:
                    rank_text = "رتبه: ضعیف"
                    rank_color = "red" 
                elif 9 <= gpa < 15:
                    rank_text = "رتبه: متوسط"
                    rank_color = "#f39c12" 
                elif 15 <= gpa <= 20:
                    rank_text = "رتبه: عالی"
                    rank_color = "green" 
                
                self.lbl_rank.config(text=rank_text, foreground=rank_color)

            else:
                self.lbl_result.config(text=f"دانشجو {st_name} هیچ نمره ثبت شده‌ای با واحد درسی ندارد.")
                self.lbl_rank.config(text="---", foreground='black')
                
        except ValueError:
            messagebox.showerror("خطا", "شناسه دانشجو باید یک عدد باشد.")
        except Exception as e:
            self.lbl_result.config(text="خطای دیتابیس رخ داد")
            self.lbl_rank.config(text="---", foreground='black')
            messagebox.showerror("خطای پایگاه داده", f"خطا: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg="#f0f0f0") 
    app = ChamranApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: [app.session.close(), root.destroy()])
    root.mainloop()