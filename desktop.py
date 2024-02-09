# Dependencies: PYYaml customtkinter
import asyncio
import datetime
import yaml
import sys
import customtkinter
import libs.database as database

class BootGUI(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Boot Info")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.info = customtkinter.CTkLabel(self, text='Starting application', font=customtkinter.CTkFont(size=20, weight="bold"))
        self.info.grid(row=0, column=0, padx=20, pady=20)
        self.subinfo = customtkinter.CTkLabel(self, text='Starting...')
        self.subinfo.grid(row=1, column=0, padx=20, pady=20)

    def updateinfo(self, arg="None"):
        self.info.configure(text=arg)

    def updatesubinfo(self, arg="None"):
        self.subinfo.configure(text=arg)

    def close_gui(self):
        self.destroy()



class ErrorGUI(customtkinter.CTk):
    def __init__(self, msg=str, err=str, time_wait=0):
        super().__init__()

        self.title("ERROR!")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        arg_full = f"{msg}\nError:[{err}]\nThe program will still launch in {time_wait} seconds"
        self.title = customtkinter.CTkLabel(self, text=str(arg_full))
        self.title.grid(row=0, column=0, columnspan=1, padx=20, pady=(20, 20))
        self.buttonframe = customtkinter.CTkFrame(self)
        self.buttonframe.grid(row=1, column=0)
        self.button = customtkinter.CTkButton(self.buttonframe, text="Exit", command=sys.exit)
        self.button.grid(row=0, column=0, padx=20, pady=(20, 20), sticky="e")
        self.button = customtkinter.CTkButton(self.buttonframe, text="Resume", command=self.skip_wait)
        self.button.grid(row=0, column=1, padx=20, pady=(20, 20), sticky="e")

    def skip_wait(self):
        self.destroy()
        open_second_gui()

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.entries_main = {}
        self.mysql_conn = False

        self.current_date = datetime.datetime.now().date()

        with open(r'configs/config.yml') as config:
            self.cfg = yaml.load(config, Loader=yaml.FullLoader)
            # checks if config entries are valid

        self.sqdb = database.sqlite()
        self.sqdb.connect("configs/database.db")
        self.currentdb = self.sqdb

        self.title(f"{self.cfg['group_name']} Barkaart")
        self.geometry(f"{1920}x{1080}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(9, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text=self.cfg['group_name'], font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.sidebar_toggle_admin = customtkinter.CTkButton(self.sidebar_frame, text="Admin", command=self.admin_password)
        self.sidebar_toggle_admin.grid(row=1, column=0, padx=20, pady=(10,20))
        self.sidebar_user_label = customtkinter.CTkLabel(self.sidebar_frame, text=self.cfg['lang']['select_user'], anchor="w")
        self.sidebar_user_label.grid(row=2, column=0, padx=20, pady=(20,10))
        self.sidebar_user = customtkinter.CTkOptionMenu(self.sidebar_frame, values=['Marije', 'Vamting'], command=self.update_order_list)
        self.sidebar_user.grid(row=3, column=0, padx=20, pady=10)
        self.sidebar_current_credits = customtkinter.CTkLabel(self.sidebar_frame, text=self.cfg['lang']['current_credits_money'].replace('%s', self.cfg['lang']['none']))
        self.sidebar_current_credits.grid(row=4, column=0, padx=20, pady=(10,20))
        self.sidebar_add_credits = customtkinter.CTkButton(self.sidebar_frame, text=self.cfg['lang']['add_credits'], command=self.add_credits)
        self.sidebar_add_credits.grid(row=5, column=0, padx=20, pady=20)
        self.sidebar_sort_user = customtkinter.CTkCheckBox(self.sidebar_frame, text=self.cfg['lang']['sort_user'], command=self.update_order_list)
        self.sidebar_sort_user.grid(row=6, column=0, padx=20, pady=(20,10))
        self.sidebar_sort_item_label = customtkinter.CTkLabel(self.sidebar_frame, text=self.cfg['lang']['sort_item'])
        self.sidebar_sort_item_label.grid(row=7, column=0, padx=20, pady=10)
        self.sidebar_sort_item = customtkinter.CTkOptionMenu(self.sidebar_frame, values=['Bier', 'Wijn', 'Meow'], command=self.update_order_list)
        self.sidebar_sort_item.grid(row=8, column=0, padx=20, pady=(10,20))



        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=25, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionmenu = customtkinter.CTkOptionMenu(self.sidebar_frame,
                                                                       values=["System", "Light", "Dark",],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionmenu.grid(row=26, column=0, padx=20, pady=(10, 10))
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=27, column=0, padx=20, pady=(10, 0))
        self.scaling_optionmenu = customtkinter.CTkOptionMenu(self.sidebar_frame,
                                                               values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        customtkinter.set_widget_scaling(float(self.cfg['user_preferences']['default_ui_scale']) / 100)
        self.scaling_optionmenu.grid(row=28, column=0, padx=20, pady=(10, 20))
        self.scaling_optionmenu.set(f"{self.cfg['user_preferences']['default_ui_scale']}%")

        # create scrollable frame and variables
        self.grid_rowconfigure(0, weight=1)
        self.tabview = customtkinter.CTkTabview(self)
        self.tabview.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.tabview.grid_rowconfigure(0, weight=0)
        self.tabview.grid_columnconfigure(0, weight=1)
        self.tabview.add(self.cfg['lang']['stats_label'])
        self.tabview.tab(self.cfg['lang']['stats_label']).grid_rowconfigure(0, weight=1)
        self.tabview.tab(self.cfg['lang']['stats_label']).grid_columnconfigure(0, weight=1)
        self.frame = customtkinter.CTkFrame(self.tabview.tab(self.cfg['lang']['stats_label']))
        self.frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.user_header = customtkinter.CTkLabel(self.frame, text=self.cfg['lang']['none'], font=('calibri', 40))
        self.user_header.grid(row=0, column=0, columnspan=15, padx=(40,20), pady=20, sticky='nw')

        self.most_recent_order = customtkinter.CTkLabel(self.frame, text=self.cfg['lang']['recent_order'].replace('%s', self.cfg['lang']['none']), font=('calibri', 40))
        self.most_recent_order.grid(row=1, column=0, padx=(40,20), pady=20, sticky='w')

        self.frame_left = customtkinter.CTkFrame(self.frame)
        self.frame_left.grid(row=2, column=0, padx=(40, 20), pady=20, sticky='nw')
        self.frame_left_header = customtkinter.CTkLabel(self.frame_left, text=self.cfg['lang']['left_header'],
                                                        font=('calibri', 30))
        self.frame_left_header.grid(row=0, column=0, padx=20, pady=20, sticky='nw')

        self.credits_left = customtkinter.CTkLabel(self.frame_left,
                                                   text=self.cfg['lang']['credits_money_left'].replace('%s', self.cfg['lang']['none']),
                                                   font=('calibri', 20))
        self.credits_left.grid(row=1, column=0, padx=20, pady=20, sticky='nw')
        if self.cfg['user_preferences']['show_totals']:
            self.frame_spent = customtkinter.CTkFrame(self.frame)
            self.frame_spent.grid(row=3, column=0, padx=(40,20), pady=20, sticky='nw')
            self.frame_spent_header = customtkinter.CTkLabel(self.frame_spent, text=self.cfg['lang']['spent_header'], font=('calibri', 30))
            self.frame_spent_header.grid(row=0, column=0, padx=20, pady=20, sticky='nw')

            self.total_orders = customtkinter.CTkLabel(self.frame_spent, text=self.cfg['lang']['total_orders'].replace('%s', self.cfg['lang']['none']), font=('calibri', 20))
            self.total_orders.grid(row=1, column=0, padx=20, pady=10, sticky='nw')
            if cfg['user_preferences']['use_credits']:
                self.total_credits = customtkinter.CTkLabel(self.frame_spent, text=self.cfg['lang']['total_credits_spent'].replace('%s', self.cfg['lang']['none']), font=('calibri', 20))
                self.total_credits.grid(row=2, column=0, padx=20, pady=10, sticky='nw')

            self.total_money_spent = customtkinter.CTkLabel(self.frame_spent, text=self.cfg['lang']['total_money_spent'].replace('%s', self.cfg['lang']['none']), font=('calibri', 20))
            self.total_money_spent.grid(row=3, column=0, padx=20, pady=10, sticky='nw')


        self.tabview.add(self.cfg['lang']['history_label'])
        self.tabview.tab(self.cfg['lang']['history_label']).grid_rowconfigure(0, weight=1)
        self.tabview.tab(self.cfg['lang']['history_label']).grid_columnconfigure(0, weight=1)
        self.scrollable_frame = customtkinter.CTkScrollableFrame(self.tabview.tab(self.cfg['lang']['history_label']), label_text=self.cfg['lang']['history_sublabel'])
        self.scrollable_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.order_list_1 = customtkinter.CTkFrame(self.scrollable_frame)
        self.order_list_1.grid(row=0, column=0, sticky='nsw', padx=5)
        self.order_list_1.rowconfigure(100, weight=0)
        self.order_list_legend_1 = customtkinter.CTkButton(self.order_list_1, text=self.cfg['lang']['order_date'], text_color_disabled="white", state="disabled")
        self.order_list_legend_1.grid(row=0, column=0, sticky='ew')

        self.order_list_2 = customtkinter.CTkFrame(self.scrollable_frame)
        self.order_list_2.grid(row=0, column=1, sticky='nsw', padx=5)
        self.order_list_2.rowconfigure(100, weight=0)
        self.order_list_legend_2 = customtkinter.CTkButton(self.order_list_2, text=self.cfg['lang']['item'],
                                                           text_color_disabled="white", state="disabled")
        self.order_list_legend_2.grid(row=0, column=0, sticky='ew')

        self.order_list_3 = customtkinter.CTkFrame(self.scrollable_frame)
        self.order_list_3.grid(row=0, column=2, sticky='nsw', padx=5)
        self.order_list_3.rowconfigure(100, weight=0)
        self.order_list_legend_3 = customtkinter.CTkButton(self.order_list_3, text=self.cfg['lang']['user'],
                                                           text_color_disabled="white", state="disabled")
        self.order_list_legend_3.grid(row=0, column=0, sticky='ew')

        self.order_data_1 = {}
        self.order_data_2 = {}
        self.order_data_3 = {}

        #Frame with order Buttons
        self.lower_frame = customtkinter.CTkFrame(self)
        self.lower_frame.grid(row=1, column=1, padx=(20, 0), pady=(20, 0), sticky='sew')
        self.lower_frame.rowconfigure(2, weight=1)
        self.lower_frame.columnconfigure(11, weight=1)
        self.lower_frame_label = customtkinter.CTkLabel(self.lower_frame, text=self.cfg['lang']['order_here'], font=("calibri", 25))
        self.lower_frame_label.grid(row=0, column=0, columnspan=20, padx=20, pady=(20,10))
        self.spacer_frame = customtkinter.CTkFrame(self.lower_frame, height=20)
        self.spacer_frame.grid(row=50, column=0, columnspan=20, padx=0, pady=(20,0), sticky='sew')
        self.spacer_footer = customtkinter.CTkLabel(self.spacer_frame, text="Copyright: © Vamting IT 2024", font=('calibri', 12))
        self.spacer_footer.grid(row=0, column=0, padx=10, pady=10, sticky='ew')

        user_exists = self.currentdb.fetchone(table='members')
        if not user_exists:
            self.create_first_user()
        item_exists = self.currentdb.fetchone(table='items')
        if not item_exists:
            self.add_item(name='Sample item', price=1, skip_admin=True)

        self.update_user_list(True)
        self.update_item_list(True)
        self.update_order_list()

        #Maximize window if wanted by user
        self.wm_attributes('-fullscreen', self.cfg['user_preferences']['fullscreen_borderless'])

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def create_first_user(self):
        dialog = customtkinter.CTkInputDialog(text='Welcome, Please create your first user!\nName:',
                                              title="First user Create")
        self.add_user(user_name=dialog.get_input(), skip_admin=True)

    # Fully Functional
    def handle_order(self, item_id:int):
        item_data = self.currentdb.fetchone(table='items', filters=f"id={item_id}")
        if item_data[5] >= 1:
            user_name = self.sidebar_user.get()
            user_data = self.currentdb.fetchone(table='members', filters=f"name='{user_name}'")
            if user_data[4] >= item_data[4]:
                id = 1
                max_item = self.currentdb.fetchall(table='orders')
                for item in max_item:
                    if id <= item[1]:
                        id = int(item[1]) + 1
                id_exists = self.currentdb.rowcount(table='orders', filters=f"id = {id}")
                if id_exists == -1:
                    self.currentdb.updatemultiple(table='members',
                                                  updates=f"last_updated={datetime.datetime.now().timestamp()},tickets_used={user_data[3] + item_data[4]},tickets_unused={user_data[4] - item_data[4]}",
                                                  filters=f"id={user_data[1]}")
                    self.currentdb.updatemultiple(table='items',
                                                  updates=f"last_updated={datetime.datetime.now().timestamp()},anmount_avalible={item_data[5] - 1},anmount_sold={item_data[6] + 1}", filters=f"id={item_data[1]}")
                    self.currentdb.insert(table='orders', collumns='order_placed,id,user_id,item_id',
                                          values=f"{datetime.datetime.now().timestamp()},{id},{user_data[1]},{item_data[1]}")
                    self.update_order_list()
                else:
                    self.error_message(msg="Something went wrong with adding the order!",
                                       err="Orderid Found in database")
            else:
                self.error_message(msg=self.cfg['lang']['out_of_credits'], err="out of credits")
        else:
            self.error_message(msg=self.cfg['lang']['out_of_stock'].replace("%s", item_data[2]), err="stock empty")

    # Probably works. Untested unused. Exists if ever needed
    def delete_order(self, id=int):
        self.currentdb.delete(table='orders', filters=f"id = {id}")
        self.update_order_list()

    # Fully Functional
    def update_order_list(self, data=None):
        skip_orders = False
        sorting_user = self.sidebar_user.get()
        user_data = self.currentdb.fetchone(table='members', filters=f"name='{sorting_user}'")
        user_orders = self.currentdb.fetchall(table='orders', filters=f"user_id={user_data[1]}")
        user_sort = self.sidebar_sort_user.get()
        item_sort = self.sidebar_sort_item.get()
        unfiltered = True
        if user_sort:
            orders = user_orders
            unfiltered = False
        if item_sort != 'All':
            item_id = self.currentdb.fetchone(table='items', filters=f"name='{item_sort}'")
            orders = self.currentdb.fetchall(table='orders', filters=f"item_id={item_id[1]}")
            unfiltered = False
        if unfiltered:
            orders = self.currentdb.fetchall(table='orders')
        if not orders:
            skip_orders = True
        row = 1
        max_rows = 25
        if not skip_orders:
            sorted_orders = sorted(orders, key=lambda x: x[0], reverse=True)
            for order in sorted_orders:
                if row > max_rows:
                    break
                if row % 2 == 0:
                    colour = "gray"
                else:
                    colour = "black"
                time = datetime.datetime.fromtimestamp(order[0])
                if not row in self.order_data_1:
                    order_entry_1 = customtkinter.CTkButton(self.order_list_1, text=time.strftime('%H:%M %d-%m-%Y'),
                                                            fg_color=colour, text_color_disabled="white",
                                                            state="disabled")
                    order_entry_1.grid(row=row, column=0, sticky='ew')
                    self.order_data_1[row] = order_entry_1
                else:
                    self.order_data_1[row].configure(text=time.strftime('%H:%M %d-%m-%Y'))

                order_name = self.currentdb.fetchone(table='items', filters=f"id={order[3]}")
                if not row in self.order_data_2:
                    order_entry_2 = customtkinter.CTkButton(self.order_list_2, text=order_name[2],
                                                            fg_color=colour, text_color_disabled="white",
                                                            state="disabled")
                    order_entry_2.grid(row=row, column=0, sticky='ew')
                    self.order_data_2[row] = order_entry_2
                else:
                    self.order_data_2[row].configure(text=order_name[2])

                user_name = self.currentdb.fetchone(table='members', filters=f"id={order[2]}")
                if not row in self.order_data_3:
                    order_entry_3 = customtkinter.CTkButton(self.order_list_3, text=user_name[2],
                                                            fg_color=colour, text_color_disabled="white",
                                                            state="disabled")
                    order_entry_3.grid(row=row, column=0, sticky='ew')
                    self.order_data_3[row] = order_entry_3
                else:
                    self.order_data_3[row].configure(text=user_name[2])
                row += 1
            while row <= max_rows:
                if row in self.order_data_1:
                    self.order_data_1[row].destroy()
                    self.order_data_1.pop(row)
                    self.order_data_2[row].destroy()
                    self.order_data_2.pop(row)
                    self.order_data_3[row].destroy()
                    self.order_data_3.pop(row)
                    row += 1
                else:
                    row = 2048

        if self.cfg['user_preferences']['use_credits']:
            creditdata = str(user_data[4])
        else:
            creditdata = str(float(user_data[4]) / 100)
        self.sidebar_current_credits.configure(text=self.cfg['lang']['current_credits_money'].replace('%s', creditdata))
        self.user_header.configure(text=user_data[2])
        if not skip_orders:
            item_info = self.currentdb.fetchone(table='items', filters=f"id={sorted_orders[0][3]}")
            self.most_recent_order.configure(text=self.cfg['lang']['recent_order'].replace('%s', item_info[2]))
        if self.cfg['user_preferences']['show_totals']:
            self.credits_left.configure(text=self.cfg['lang']['credits_money_left'].replace('%s', creditdata))

            order_anmount = self.currentdb.fetchall(table='orders', filters=f"user_id={user_data[1]}")
            self.total_orders.configure(text=self.cfg['lang']['total_orders'].replace('%s', str(len(order_anmount))))
            if self.cfg['user_preferences']['use_credits']:
                self.total_credits.configure(text=self.cfg['lang']['total_credits_spent'].replace('%s', str(user_data[3])))
            if self.cfg['user_preferences']['use_credits']:
                moneyspent = str(user_data[3] * (float(self.cfg['user_preferences']['credit_value_in_cents']) / 100))
            else:
                moneyspent = str(float(user_data[3]) / 100)
            self.total_money_spent.configure(text=self.cfg['lang']['total_money_spent'].replace('%s', moneyspent))

    def add_credits(self):
        user_name = self.sidebar_user.get()
        user_data = self.currentdb.fetchone(table='members', filters=f"name='{user_name}'")
        self.currentdb.update(table='members', collumn="tickets_unused", value=int(user_data[4]) + int(self.cfg['user_preferences']['credits_added_via_button']), filters=f"id={user_data[1]}")
        self.update_order_list()

    # Fully Functional
    def admin_password(self):
        password = customtkinter.CTkInputDialog(text="Admin Wachtwoord:", title="Admin Login")
        if str(password.get_input()) == self.cfg['admin_password']:
            self.open_admin_menu()
        else:
            self.error_message(msg="Incorrect Wachtwoord", err="Input does not match saved password")

    # Fully Functional
    def open_admin_menu(self):
        self.admin_menu = customtkinter.CTkToplevel(self)
        self.admin_menu.geometry("1200x500")
        self.admin_menu.title("Admin Settings")
        self.admin_menu.grid_columnconfigure(1, weight=1)
        self.admin_menu.grid_rowconfigure(1, weight=1)

        self.sidebar_frame_admin = customtkinter.CTkFrame(self.admin_menu, width=100, corner_radius=0)
        self.sidebar_frame_admin.grid(row=0, column=0, rowspan=4, sticky="nsw")
        self.sidebar_frame_admin.grid_rowconfigure(7, weight=1)

        self.add_member_name_label = customtkinter.CTkLabel(self.sidebar_frame_admin, text="Add User:")
        self.add_member_name_label.grid(row=0, column=0, padx=10, pady=10, sticky='nw')
        self.add_member_name = customtkinter.CTkEntry(self.sidebar_frame_admin, placeholder_text="Naam")
        self.add_member_name.grid(row=1, column=0, padx=10, pady=10, sticky='nw')
        self.add_member = customtkinter.CTkButton(self.sidebar_frame_admin, text="Add User", command=self.add_user)
        self.add_member.grid(row=2, column=0, padx=10, pady=10, sticky='nw')

        self.add_item_label = customtkinter.CTkLabel(self.sidebar_frame_admin, text="Add Item:")
        self.add_item_label.grid(row=3, column=0, padx=10, pady=10, sticky='nw')
        self.add_item_name = customtkinter.CTkEntry(self.sidebar_frame_admin, placeholder_text="Item Naam")
        self.add_item_name.grid(row=4, column=0, padx=10, pady=10, sticky='nw')
        self.add_item_price = customtkinter.CTkEntry(self.sidebar_frame_admin, placeholder_text="Prijs")
        self.add_item_price.grid(row=5, column=0, padx=10, pady=10, sticky='nw')
        self.add_item = customtkinter.CTkButton(self.sidebar_frame_admin, text="Add Item", command=self.add_item)
        self.add_item.grid(row=6, column=0, padx=10, pady=10, sticky='nw')
        self.save_edits = customtkinter.CTkButton(self.sidebar_frame_admin, text="Save Changes", command=self.save_changes)
        self.save_edits.grid(row=7, column=0, padx=10, pady=10, sticky='nw')
        if self.cfg['debug']:
            self.raw_sql = customtkinter.CTkButton(self.sidebar_frame_admin, text="Raw SQL", command=self.rawsql)
            self.raw_sql.grid(row=8, column=0, padx=10, pady=10, sticky='nw')

        self.tabview_admin = customtkinter.CTkTabview(self.admin_menu, width=900, height=500)
        self.tabview_admin.grid(row=0, column=1, padx=20, pady=20, sticky='nsew')
        self.tabview_admin.grid_rowconfigure(0, weight=1)
        self.tabview_admin.grid_columnconfigure(0, weight=1)
        self.tabview_admin.add("Members")
        self.tabview_admin.tab("Members").grid_rowconfigure(0, weight=1)
        self.tabview_admin.tab("Members").grid_columnconfigure(0, weight=1)
        self.scrollable_frame_members = customtkinter.CTkScrollableFrame(self.tabview_admin.tab("Members"), label_text="Members")
        self.scrollable_frame_members.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

        self.scrollable_frame_members_1 = customtkinter.CTkFrame(self.scrollable_frame_members)
        self.scrollable_frame_members_1.grid(row=0, column=0, sticky='nsw', padx=5)
        self.scrollable_frame_members_1.rowconfigure(100, weight=0)
        self.scrollable_frame_members_legend_1 = customtkinter.CTkButton(self.scrollable_frame_members_1, text="Last Updated", text_color_disabled="white", state="disabled")
        self.scrollable_frame_members_legend_1.grid(row=0, column=0, sticky='ew')

        self.scrollable_frame_members_2 = customtkinter.CTkFrame(self.scrollable_frame_members)
        self.scrollable_frame_members_2.grid(row=0, column=1, sticky='nsw', padx=5)
        self.scrollable_frame_members_2.rowconfigure(100, weight=0)
        self.scrollable_frame_members_legend_2 = customtkinter.CTkButton(self.scrollable_frame_members_2,
                                                                         text="Member ID",
                                                                         text_color_disabled="white", state="disabled")
        self.scrollable_frame_members_legend_2.grid(row=0, column=0, sticky='ew')

        self.scrollable_frame_members_3 = customtkinter.CTkFrame(self.scrollable_frame_members)
        self.scrollable_frame_members_3.grid(row=0, column=2, sticky='nsw', padx=5)
        self.scrollable_frame_members_3.rowconfigure(100, weight=0)
        self.scrollable_frame_members_legend_3 = customtkinter.CTkButton(self.scrollable_frame_members_3,
                                                                         text="Name",
                                                                         text_color_disabled="white", state="disabled")
        self.scrollable_frame_members_legend_3.grid(row=0, column=0, sticky='ew')

        self.scrollable_frame_members_4 = customtkinter.CTkFrame(self.scrollable_frame_members)
        self.scrollable_frame_members_4.grid(row=0, column=4, sticky='nsw', padx=5)
        self.scrollable_frame_members_4.rowconfigure(100, weight=0)
        self.scrollable_frame_members_legend_4 = customtkinter.CTkButton(self.scrollable_frame_members_4,
                                                                         text="Tickets Used",
                                                                         text_color_disabled="white", state="disabled")
        self.scrollable_frame_members_legend_4.grid(row=0, column=0, sticky='ew')

        self.scrollable_frame_members_5 = customtkinter.CTkFrame(self.scrollable_frame_members)
        self.scrollable_frame_members_5.grid(row=0, column=5, sticky='nsw', padx=5)
        self.scrollable_frame_members_5.rowconfigure(100, weight=0)
        self.scrollable_frame_members_legend_5 = customtkinter.CTkButton(self.scrollable_frame_members_5,
                                                                         text="Tickets Unused",
                                                                         text_color_disabled="white", state="disabled")
        self.scrollable_frame_members_legend_5.grid(row=0, column=0, sticky='ew')

        self.scrollable_frame_members_6 = customtkinter.CTkFrame(self.scrollable_frame_members)
        self.scrollable_frame_members_6.grid(row=0, column=6, sticky='nsw', padx=5)
        self.scrollable_frame_members_6.rowconfigure(100, weight=0)
        self.scrollable_frame_members_legend_6 = customtkinter.CTkButton(self.scrollable_frame_members_6,
                                                                         text="Delete Members",
                                                                         text_color_disabled="white", state="disabled")
        self.scrollable_frame_members_legend_6.grid(row=0, column=0, sticky='ew')

        self.scrollable_frame_members_data_1 = {}
        self.scrollable_frame_members_data_2 = {}
        self.scrollable_frame_members_data_3 = {}
        self.scrollable_frame_members_data_4 = {}
        self.scrollable_frame_members_data_5 = {}
        self.scrollable_frame_members_data_6 = {}

        self.tabview_admin.add("Items")
        self.tabview_admin.tab("Items").grid_rowconfigure(0, weight=1)
        self.tabview_admin.tab("Items").grid_columnconfigure(0, weight=1)
        self.scrollable_frame_items = customtkinter.CTkScrollableFrame(self.tabview_admin.tab("Items"), label_text="Items")
        self.scrollable_frame_items.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

        self.scrollable_frame_items_1 = customtkinter.CTkFrame(self.scrollable_frame_items)
        self.scrollable_frame_items_1.grid(row=0, column=0, sticky='nsw', padx=5)
        self.scrollable_frame_items_1.rowconfigure(100, weight=0)
        self.scrollable_frame_items_legend_1 = customtkinter.CTkButton(self.scrollable_frame_items_1,
                                                                         text="Last Updated",
                                                                         text_color_disabled="white", state="disabled")
        self.scrollable_frame_items_legend_1.grid(row=0, column=0, sticky='ew')

        self.scrollable_frame_items_2 = customtkinter.CTkFrame(self.scrollable_frame_items)
        self.scrollable_frame_items_2.grid(row=0, column=1, sticky='nsw', padx=5)
        self.scrollable_frame_items_2.rowconfigure(100, weight=0)
        self.scrollable_frame_items_legend_2 = customtkinter.CTkButton(self.scrollable_frame_items_2,
                                                                       text="ID",
                                                                       text_color_disabled="white", state="disabled")
        self.scrollable_frame_items_legend_2.grid(row=0, column=0, sticky='ew')

        self.scrollable_frame_items_3 = customtkinter.CTkFrame(self.scrollable_frame_items)
        self.scrollable_frame_items_3.grid(row=0, column=2, sticky='nsw', padx=5)
        self.scrollable_frame_items_3.rowconfigure(100, weight=0)
        self.scrollable_frame_items_legend_3 = customtkinter.CTkButton(self.scrollable_frame_items_3,
                                                                       text="Name",
                                                                       text_color_disabled="white", state="disabled")
        self.scrollable_frame_items_legend_3.grid(row=0, column=0, sticky='ew')

        self.scrollable_frame_items_4 = customtkinter.CTkFrame(self.scrollable_frame_items)
        self.scrollable_frame_items_4.grid(row=0, column=3, sticky='nsw', padx=5)
        self.scrollable_frame_items_4.rowconfigure(100, weight=0)
        self.scrollable_frame_items_legend_4 = customtkinter.CTkButton(self.scrollable_frame_items_4,
                                                                       text="Price",
                                                                       text_color_disabled="white", state="disabled")
        self.scrollable_frame_items_legend_4.grid(row=0, column=0, sticky='ew')

        self.scrollable_frame_items_5 = customtkinter.CTkFrame(self.scrollable_frame_items)
        self.scrollable_frame_items_5.grid(row=0, column=4, sticky='nsw', padx=5)
        self.scrollable_frame_items_5.rowconfigure(100, weight=0)
        self.scrollable_frame_items_legend_5 = customtkinter.CTkButton(self.scrollable_frame_items_5,
                                                                       text="Avalible",
                                                                       text_color_disabled="white", state="disabled")
        self.scrollable_frame_items_legend_5.grid(row=0, column=0, sticky='ew')

        self.scrollable_frame_items_6 = customtkinter.CTkFrame(self.scrollable_frame_items)
        self.scrollable_frame_items_6.grid(row=0, column=5, sticky='nsw', padx=5)
        self.scrollable_frame_items_6.rowconfigure(100, weight=0)
        self.scrollable_frame_items_legend_6 = customtkinter.CTkButton(self.scrollable_frame_items_6,
                                                                       text="Sold",
                                                                       text_color_disabled="white", state="disabled")
        self.scrollable_frame_items_legend_6.grid(row=0, column=0, sticky='ew')

        self.scrollable_frame_items_7 = customtkinter.CTkFrame(self.scrollable_frame_items)
        self.scrollable_frame_items_7.grid(row=0, column=6, sticky='nsw', padx=5)
        self.scrollable_frame_items_7.rowconfigure(100, weight=0)
        self.scrollable_frame_items_legend_7 = customtkinter.CTkButton(self.scrollable_frame_items_7,
                                                                       text="Delete",
                                                                       text_color_disabled="white", state="disabled")
        self.scrollable_frame_items_legend_7.grid(row=0, column=0, sticky='ew')

        self.scrollable_frame_items_data_1 = {}
        self.scrollable_frame_items_data_2 = {}
        self.scrollable_frame_items_data_3 = {}
        self.scrollable_frame_items_data_4 = {}
        self.scrollable_frame_items_data_5 = {}
        self.scrollable_frame_items_data_6 = {}
        self.scrollable_frame_items_data_7 = {}



        self.update_user_list()
        self.update_item_list()

    # Fully Functional
    def save_changes(self):
        self.update_users()
        self.update_items()
        self.update_user_list(True)
        self.update_item_list(True)
        self.update_order_list()

    # Fully Functional
    def add_user(self, user_name=False, skip_admin=False):
        id = 1
        max_item = self.currentdb.fetchall(table='members')
        for item in max_item:
          if id <= item[1]:
              id = int(item[1]) + 1
        if user_name:
            name = user_name
        else:
            name = self.add_member_name.get()
        if name != "":
            id_exists = self.currentdb.rowcount(table='members', filters=f"id = {id}")
            if id_exists == -1:
                self.currentdb.insert(table='members', collumns='last_updated,id,name,tickets_used,tickets_unused', values=f"{datetime.datetime.now().timestamp()},{id},'{name}',0,0")
                self.update_user_list(skip_admin)
            else:
                self.error_message(msg="Something went wrong with adding the user!", err="Userid Found in database")

    # Fully Functional
    def delete_user(self, id:int):
        if self.cfg['debug']:
            self.currentdb.delete(table='members', filters=f"id = {id}")
        else:
            self.currentdb.update(table='members', filters=f"id = {id}", collumn='deleted', value=1)
        self.update_user_list()

    # Fully Functional
    def update_users(self):
        row = 1
        for item in self.scrollable_frame_members_data_2:
            currentdata = self.currentdb.fetchone(table='members', filters=f"id = {self.scrollable_frame_members_data_2[row].cget('text')}")
            name = self.scrollable_frame_members_data_3[row].get()
            tickets_used = self.scrollable_frame_members_data_4[row].get()
            tickets_unused = self.scrollable_frame_members_data_5[row].get()
            if (str(currentdata[2]) != str(name)) or (int(currentdata[3]) != int(tickets_used)) or (int(currentdata[4]) != int(tickets_unused)):
                self.currentdb.updatemultiple(table='members',
                                              updates=f"last_updated={datetime.datetime.now().timestamp()},name='{name}',tickets_used={tickets_used},tickets_unused={tickets_unused}",filters=f"id={currentdata[1]}")
            row += 1

    # Fully Functional
    def update_user_list(self, skip_admin=False):
        users = self.currentdb.fetchall(table='members')
        if not skip_admin:
            row = 1
            max_rows = 100
            for user in users:
                if not user[5]:
                    if row % 2 == 0:
                        colour = "gray"
                    else:
                        colour = "black"
                    time = datetime.datetime.fromtimestamp(user[0])
                    member_user_1 = customtkinter.CTkButton(self.scrollable_frame_members_1, text=time.strftime('%H:%M %d-%m-%Y'), fg_color=colour, text_color_disabled="white", state="disabled")
                    member_user_1.grid(row=row, column=0, sticky='ew')
                    self.scrollable_frame_members_data_1[row] = member_user_1

                    member_user_2 = customtkinter.CTkButton(self.scrollable_frame_members_2, text=user[1], fg_color=colour,
                                                            text_color_disabled="white", state="disabled")
                    member_user_2.grid(row=row, column=0, sticky='ew')
                    self.scrollable_frame_members_data_2[row] = member_user_2

                    member_user_3 = customtkinter.CTkEntry(self.scrollable_frame_members_3, placeholder_text="Missing Value",
                                                           fg_color=colour)
                    member_user_3.grid(row=row, column=0, sticky='ew')
                    member_user_3.insert(0, user[2])
                    self.scrollable_frame_members_data_3[row] = member_user_3

                    member_user_4 = customtkinter.CTkEntry(self.scrollable_frame_members_4, placeholder_text="Missing Value",
                                                           fg_color=colour)
                    member_user_4.grid(row=row, column=0, sticky='ew')
                    member_user_4.insert(0, user[3])
                    self.scrollable_frame_members_data_4[row] = member_user_4

                    member_user_5 = customtkinter.CTkEntry(self.scrollable_frame_members_5, placeholder_text="Missing Value",
                                                           fg_color=colour)
                    member_user_5.grid(row=row, column=0, sticky='ew')
                    member_user_5.insert(0, user[4])
                    self.scrollable_frame_members_data_5[row] = member_user_5

                    member_user_6 = customtkinter.CTkButton(self.scrollable_frame_members_6, text="Delete", fg_color='darkred',
                                                            command=lambda i=user[1]: self.delete_user(i))
                    member_user_6.grid(row=row, column=0, sticky='ew')
                    self.scrollable_frame_members_data_6[row] = member_user_6
                    row += 1
            while row <= max_rows:
                if row in self.scrollable_frame_members_data_1:
                    self.scrollable_frame_members_data_1[row].destroy()
                    self.scrollable_frame_members_data_1.pop(row)
                    self.scrollable_frame_members_data_2[row].destroy()
                    self.scrollable_frame_members_data_2.pop(row)
                    self.scrollable_frame_members_data_3[row].destroy()
                    self.scrollable_frame_members_data_3.pop(row)
                    self.scrollable_frame_members_data_4[row].destroy()
                    self.scrollable_frame_members_data_4.pop(row)
                    self.scrollable_frame_members_data_5[row].destroy()
                    self.scrollable_frame_members_data_5.pop(row)
                    self.scrollable_frame_members_data_6[row].destroy()
                    self.scrollable_frame_members_data_6.pop(row)
                    row += 1
                else:
                    row = 125
        userlist = []
        for user in users:
            userlist.append(user[2])
        userlist.sort()
        self.sidebar_user.configure(values=userlist)
        self.sidebar_user.set(userlist[0])

    # Fully Functional
    def add_item(self, name=False, price=False, skip_admin=False):
        id = 1
        max_item = self.currentdb.fetchall(table='items')
        for item in max_item:
            if id <= item[1]:
                id = int(item[1]) + 1
        if not name:
            name = self.add_item_name.get()
        if not price:
            price = self.add_item_price.get()
        if name != "":
            id_exists = self.currentdb.rowcount(table='items', filters=f"id = {id}")
            if id_exists == -1:
                try:
                    self.currentdb.insert(table='items', collumns='last_updated,id,name,price,anmount_avalible,anmount_sold',
                                          values=f"{datetime.datetime.now().timestamp()},{id},'{name}',{price},0,0")
                    self.update_item_list(skip_admin=skip_admin)
                except Exception as e:
                    self.error_message(msg="Something went wrong with adding the item!", err=str(e))
            else:
                self.error_message(msg="Something went wrong with adding the item!", err="Itemid Found in database")
        else:
            self.error_message(msg="Something went wrong with adding the item!", err="Name is empty or price is not an integer")

    # Fully Functional
    def delete_item(self, id:int):
        if self.cfg['debug']:
            self.currentdb.delete(table='items', filters=f"id = {id}")
        else:
            self.currentdb.update(table='items', filters=f"id = {id}", collumn='deleted', value=1)
        self.update_item_list()

    # Fully Functional
    def update_items(self):
        row = 1
        for item in self.scrollable_frame_items_data_2:
            currentdata = self.currentdb.fetchone(table='items',
                                                  filters=f"id = {self.scrollable_frame_items_data_2[row].cget('text')}")
            name = self.scrollable_frame_items_data_3[row].get()
            price = self.scrollable_frame_items_data_4[row].get()
            anmount_avalible = self.scrollable_frame_items_data_5[row].get()
            anmount_sold = self.scrollable_frame_items_data_6[row].get()
            if (str(currentdata[2]) != str(name)) or (int(currentdata[4]) != int(price)) or (int(currentdata[5]) != int(anmount_avalible)) or (int(currentdata[6]) != int(anmount_sold)):
                self.currentdb.updatemultiple(table='items',
                                              updates=f"last_updated={datetime.datetime.now().timestamp()},name='{name}',price={price},anmount_avalible={anmount_avalible},anmount_sold={anmount_sold}",
                                              filters=f"id={currentdata[1]}")
            row += 1

    # Has a bug with deleting buttons. Not sure how to fix yet
    def update_item_list(self, skip_admin=False):
        items = self.currentdb.fetchall(table='items')
        if not skip_admin:
            row = 1
            max_rows = 100
            for item in items:
                if not item[7]:
                    if row % 2 == 0:
                        colour = "gray"
                    else:
                        colour = "black"
                    time = datetime.datetime.fromtimestamp(item[0])
                    item_info_1 = customtkinter.CTkButton(self.scrollable_frame_items_1, text=time.strftime('%H:%M %d-%m-%Y'), fg_color=colour, text_color_disabled="white", state="disabled")
                    item_info_1.grid(row=row, column=0, sticky='ew')
                    self.scrollable_frame_items_data_1[row] = item_info_1

                    item_info_2 = customtkinter.CTkButton(self.scrollable_frame_items_2, text=item[1], fg_color=colour,
                                                          text_color_disabled="white", state="disabled")
                    item_info_2.grid(row=row, column=0, sticky='ew')
                    self.scrollable_frame_items_data_2[row] = item_info_2

                    item_info_3 = customtkinter.CTkEntry(self.scrollable_frame_items_3, placeholder_text="Missing Value",
                                                           fg_color=colour)
                    item_info_3.grid(row=row, column=0, sticky='ew')
                    item_info_3.insert(0, item[2])
                    self.scrollable_frame_items_data_3[row] = item_info_3

                    item_info_4 = customtkinter.CTkEntry(self.scrollable_frame_items_4,
                                                         placeholder_text="Missing Value",
                                                         fg_color=colour)
                    item_info_4.grid(row=row, column=0, sticky='ew')
                    item_info_4.insert(0, item[4])
                    self.scrollable_frame_items_data_4[row] = item_info_4

                    item_info_5 = customtkinter.CTkEntry(self.scrollable_frame_items_5,
                                                         placeholder_text="Missing Value",
                                                         fg_color=colour)
                    item_info_5.grid(row=row, column=0, sticky='ew')
                    item_info_5.insert(0, item[5])
                    self.scrollable_frame_items_data_5[row] = item_info_5

                    item_info_6 = customtkinter.CTkEntry(self.scrollable_frame_items_6,
                                                         placeholder_text="Missing Value",
                                                         fg_color=colour)
                    item_info_6.grid(row=row, column=0, sticky='ew')
                    item_info_6.insert(0, item[6])
                    self.scrollable_frame_items_data_6[row] = item_info_6

                    item_info_7 = customtkinter.CTkButton(self.scrollable_frame_items_7, text="Delete", fg_color='darkred',
                                                            command=lambda i=item[1]: self.delete_item(i))
                    item_info_7.grid(row=row, column=0, sticky='ew')
                    self.scrollable_frame_items_data_7[row] = item_info_7
                    row += 1
            while row <= max_rows:
                if row in self.scrollable_frame_items_data_1:
                    self.scrollable_frame_items_data_1[row].destroy()
                    self.scrollable_frame_items_data_1.pop(row)
                    self.scrollable_frame_items_data_2[row].destroy()
                    self.scrollable_frame_items_data_2.pop(row)
                    self.scrollable_frame_items_data_3[row].destroy()
                    self.scrollable_frame_items_data_3.pop(row)
                    self.scrollable_frame_items_data_4[row].destroy()
                    self.scrollable_frame_items_data_4.pop(row)
                    self.scrollable_frame_items_data_5[row].destroy()
                    self.scrollable_frame_items_data_5.pop(row)
                    self.scrollable_frame_items_data_6[row].destroy()
                    self.scrollable_frame_items_data_6.pop(row)
                    self.scrollable_frame_items_data_7[row].destroy()
                    self.scrollable_frame_items_data_7.pop(row)
                    row += 1
                else:
                    row = 125
        itemlist = []
        itemlist_filtered = ['All']
        for item in items:
            itemlist.append(item)
            itemlist_filtered.append(item[2])
        itemlist.sort()
        itemlist_filtered.sort()
        self.sidebar_sort_item.configure(values=itemlist_filtered)
        self.sidebar_sort_item.set(itemlist_filtered[0])
        column = 0
        max_columns = int(self.cfg['user_preferences']['order_columns'])
        row = 1
        self.order_buttons = {}
        for item in itemlist:
            if column == max_columns:
                column = 0
                row += 1
            order_button = customtkinter.CTkButton(self.lower_frame, text=item[2], font=('calibri', 20), command=lambda i=item[1]: self.handle_order(i))
            order_button.grid(row=row, column=column, padx=10, pady=10, sticky='nw')
            self.order_buttons[f"{column}-{row}"] = order_button
            column += 1
        cont = False
        while not cont:
            if f"{column}-{row}" in self.order_buttons:
                if column == max_columns:
                    column = 0
                    row += 1
                self.order_buttons[f"{column}-{row}"].destroy()
                self.order_buttons.pop(f"{column}-{row}")
                column += 1
            else:
                cont = True

    # Functional as far as needed
    def error_message(self, msg="No Error", err="Unknown error"):
        self.error_messageTL = customtkinter.CTkToplevel(self)
        self.error_messageTL.title("ERROR!")
        self.error_messageTL.grid_columnconfigure(0, weight=1)
        self.error_messageTL.grid_rowconfigure(0, weight=1)
        arg_full = f"{msg}\nError:[{err}]"
        title = customtkinter.CTkLabel(self.error_messageTL, text=str(arg_full))
        title.grid(row=0, column=0, padx=20, pady=(20, 5))
        button = customtkinter.CTkButton(self.error_messageTL, text="Ok", command=self.error_messageTL.destroy)
        button.grid(row=1, column=0, padx=20, pady=(5, 20))
        self.error_messageTL.grab_set_global()

    # Functional as far as needed
    def info_message(self, msg="No Info", update=False):
        if update:
            self.info_messageTL_title.configure(text=msg)
        else:
            self.info_messageTL = customtkinter.CTkToplevel(self)
            self.info_messageTL.title("Info")
            self.info_messageTL.grid_columnconfigure(0, weight=1)
            self.info_messageTL.grid_rowconfigure(0, weight=1)
            self.info_messageTL_title = customtkinter.CTkLabel(self.info_messageTL, text=msg)
            self.info_messageTL_title.grid(row=0, column=0, padx=20, pady=(20, 5))
            self.info_messageTL_button = customtkinter.CTkButton(self.info_messageTL, text="Ok",
                                                                 command=self.info_messageTL.destroy)
            self.info_messageTL_button.grid(row=1, column=0, padx=20, pady=(5, 20))
            self.info_messageTL.grab_set()

    #Debug Functions
    def rawsql(self):
        dialog = customtkinter.CTkInputDialog(text="Enter SQL Query", title="Raw SQL Entry")
        try:
            output = self.currentdb.custom_query(dialog.get_input())
            self.info_message(msg=output)
        except Exception as e:
            self.error_message(msg="Query Error", err=str(e))
        self.save_changes()

def open_second_gui():
    app = App()
    app.mainloop()

def bootgui():
    bootapp = BootGUI()
    bootapp.mainloop()

if __name__ == "__main__":
    customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
    customtkinter.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"
    boot_error = False
    mysql_connected = False
    timetowait = 30

    bootapp = BootGUI()

    with open(r'configs/config.yml') as config:
        cfg = yaml.load(config, Loader=yaml.FullLoader)
        # checks if config entries are valid

        bootapp.updateinfo("Checking configs")
        bootapp.updatesubinfo("checking config.yml")
        bootapp.update()  # Force an update of the GUI

        """if not isinstance(cfg['user_preferences']['item_anmount'], int):
            boot_error = True
            msg = "An error occurred with config.yml"
            err = "item_anmount is not an integer (number)"
        elif not isinstance(cfg['user_preferences']['daterange'], int):
            boot_error = True
            msg = "An error occurred with config.yml"
            err = "daterange is not an integer (number)"""
        if not isinstance(cfg['user_preferences']['fullscreen_borderless'], bool):
            boot_error = True
            msg = "An error occurred with config.yml"
            err = "fullscreen_borderless is not a boolean (True/False)"
        else:
            bootapp.updateinfo("Connecting to databases")
            bootapp.updatesubinfo(f"Connecting to '{cfg['database']['local']['db_id']}'")
            bootapp.update()  # Force an update of the GUI

            try:
                sqdb = database.sqlite()
                sqdb.connect("configs/database.db")
                if cfg['database']['local']['initialize']:
                    sqdb.create_table(table="members", values="last_updated TIMESTAMP,id INTEGER NOT NULL,name TINYTEXT,tickets_used INT,tickets_unused INT,deleted BOOLEAN")
                    sqdb.create_table(table="items", values="last_updated TIMESTAMP,id INTEGER NOT NULL,name TINYTEXT,description TEXT,price TINYINT,anmount_avalible INT,anmount_sold INT,deleted BOOLEAN")
                    sqdb.create_table(table="orders", values="order_placed TIMESTAMP,id INTEGER NOT NULL,user_id INT,item_id INT")
                    #last_connected_exists = sqdb.insert_if_not_exists(table='user_data', filters='key=last_time_connected', collumns='key,value', values=("last_time_connected",datetime.datetime.now()))
            except Exception as e:
                boot_error = True
                msg = "An error occurred with Sqlite"
                err = e

            bootapp.updateinfo("Synchronizing Databases")
            bootapp.updatesubinfo(f"Sync Start")
            bootapp.update()  # Force an update of the GUI

    if boot_error:
        bootapp.close_gui()
        error_app = ErrorGUI(msg=str(msg), err=str(err), time_wait=timetowait)
        error_app.after(timetowait * 1000,
                        open_second_gui)  # Open the second GUI after a delay of 'timetowait' seconds (see param at top of if statement)
        error_app.mainloop()
        sys.exit()
    else:
        bootapp.close_gui()
        open_second_gui()
