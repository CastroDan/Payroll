from tkinter import filedialog
import tkinter.scrolledtext as tkst
from tkinter import *
import pygame

import csv
import os
import da

class PayrollGUI:
	def __init__(self, master):
		self.master = master

		self.das = []
		self.reg_shifts = []
		self.sched_shifts = []

		self.set_widgets(master)
		self.register_file = ""
		self.schedule_file = ""
		master.title("Payroll Viewer")

		if self.read_ini():
			try:
				self.load_register()
			except:
				pass

			try:
				self.load_schedule()
			except:
				pass

	def set_widgets(self, master):
		self.payroll_label = Label(master, text="Register Log Output")
		self.payroll_label.grid(row=0, column = 1, columnspan=2)
		self.payroll_display = tkst.ScrolledText(master, width=60)
		self.payroll_display.grid(row=1, column=1, rowspan=2, columnspan=2)

		self.schedule_label = Label(master, text="Schedule Output")
		self.schedule_label.grid(row=0, column = 3, columnspan=2)
		self.schedule_display = tkst.ScrolledText(master, width=60)
		self.schedule_display.grid(row=1, column=3, rowspan=2, columnspan=2)

		self.logger = tkst.ScrolledText(master, width=140)
		self.logger.grid(row=4, columnspan=7)

		self.da_label = Label(master, text="Desk Assistants")
		self.da_label.grid(row=0, column=0, columnspan=1)
		self.da_listbox = Listbox(master, height=24, width=20, selectmode=EXTENDED)
		self.da_listbox.grid(row=1, column=0)
		self.da_listbox.bind("<<ListboxSelect>>", self.filter)

		self.menuBar = Menu(master)

		self.fileMenu = Menu(self.menuBar, tearoff=0)
		self.fileMenu.add_command(label="Open Register Log...", command=lambda: self.open_file("register"))
		self.fileMenu.add_command(label="Open Schedule...", command=lambda: self.open_file("payroll"))
		self.menuBar.add_cascade(label="File", menu=self.fileMenu)

		self.aboutMenu = Menu(self.menuBar, tearoff=0)
		self.aboutMenu.add_command(label="About...", command=self.about)
		self.menuBar.add_cascade(label="Help", menu=self.aboutMenu)

		master.config(menu=self.menuBar)

		self.disable_text_boxes()

	def open_file(self, command):
		filetoload = filedialog.askopenfilename(initialdir=os.path.dirname(os.path.realpath(__file__)), title = "Open File", filetypes = (('Comma Separated Values (*.csv)', '*.csv'),("all files (*.*)", "*.*")))
		if filetoload != "":
			if command == "register":
				self.register_file = filetoload
				self.load_register()
			
				# TODO: Log File Path for future use
			if command == "payroll":
				self.schedule_file = filetoload
				self.load_schedule()
				# TODO: Log File Path for future use

			self.write_ini()

	def read_ini(self):
		ret_val = False
		with open("file.ini", 'r') as ini:
			files = ini.readlines()

			p = [x.split("\n") for x in files]

			prop = []
			for s in p:
				prop.append(s[0].split("="))


			for f in prop:
				if f[0] == "register":
					self.register_file = f[1]
					ret_val = True
				elif f[0] == "schedule":
					self.schedule_file = f[1]
					ret_val = True

		if ret_val:
			self.logger_update_single("Detected Old File: Preloading...")
		return ret_val

	def write_ini(self):
		#filetype=filepath
		with open("file.ini", 'w') as f:
			f.write("register="+self.register_file+'\n')
			f.write("schedule="+self.schedule_file+'\n')

	def enable_text_boxes(self):
		self.payroll_display.config(state="normal")
		self.schedule_display.config(state="normal")
		self.logger.config(state="normal")

	def disable_text_boxes(self):
		self.payroll_display.config(state="disabled")
		self.schedule_display.config(state="disabled")
		self.logger.config(state="disabled")

	##########################
	# LISTBOX FILTER FUNCTIONS
	##########################

	def filter(self, event):
		all_its = self.da_listbox.get(0, END)
		sel_idx = self.da_listbox.curselection()
		sel_list = [all_its[item] for item in sel_idx]
		for s in sel_list:
			self.logger_update_single("Filtering Register on: " + s)

		self.filter_register(event)
		self.filter_schedule(event)

	def filter_register(self, event):
		all_its = self.da_listbox.get(0, END)
		sel_idx = self.da_listbox.curselection()
		sel_list = [all_its[item] for item in sel_idx]

		filtered_shifts = []

		for s in sel_list:
			for sh in self.reg_shifts:
				if s == sh[0]:
					filtered_shifts.append(sh)

		self.payroll_display.config(state="normal")
		self.payroll_display.delete("1.0", END)
		self.payroll_display.config(state="disabled")
		self.register_disp(filtered_shifts)

	def filter_schedule(self, event):
		all_its = self.da_listbox.get(0, END)
		sel_idx = self.da_listbox.curselection()
		sel_list = [all_its[item] for item in sel_idx]

		filtered_shifts = []

		for s in sel_list:
			for sh in self.sched_shifts:
				if s == sh[0]:
					filtered_shifts.append(sh)

		self.schedule_display.config(state="normal")
		self.schedule_display.delete("1.0", END)
		self.schedule_display.config(state="disabled")
		self.schedule_disp(filtered_shifts)

	def load_register(self):
		try:
			# clear existing data in register_disp
			self.payroll_display.config(state="normal")
			self.payroll_display.delete("1.0", END)
			self.payroll_display.config(state="disabled")

			self.reg_shifts = []
			
			data = self.csv_reader(self.register_file)
			config = self.register_config()
			
			i = 1
			# loop over data and pull shifts
			while i < len(data):
				j = 2
				shifts = []
				while j < len(data[i]):
					if data[i][j] != "":
						shifts.append((data[i][j], da.Shift(data[i+1][j],data[i+2][j], data[i+2][j+1])))
					j = j+2

				self.register_disp(shifts)
				i = i + int(config[3])

				for s in shifts:
					self.reg_shifts.append(s)

				self.add_das()
			

			self.da_list_update()

			self.logger_update_single("Successfully parsed " + self.register_file)
		except FileNotFoundError:
			self.logger_update_single("ERROR!: Failed to open file. File Not Found")

	def load_schedule(self):
		try:
			# clear existing data
			self.sched_shifts = []
			#row0 col1 onwards contains the date
			#col0 row1 onwards contains the shift time

			data = self.csv_reader(self.schedule_file)
			time_const = 12
			two_weeks = 14

			times = []
			i = 0

			while i < time_const:
				times.append(data[i+1][0])
				i += 1

			t = [x.split("-") for x in times]
			#[start, end]

			old_i = -1
			old_name = ""

			for j in range(two_weeks):
				date = data[0][j+1]

				for i in range(time_const):
					name = data[i+1][j+1]

					if name == old_name: #same worker, same shift, ignore
						continue

					else:
						if old_i != -1: #indicates a new worker and we need to close old worker
							new_i = i

							if old_name != "": #don't add a worker who has no name
								sh = da.Shift(date, t[old_i-1][0], t[new_i-1][1])
								self.sched_shifts.append((old_name, sh))
							#[start, g]
							#[g, end]
							old_i = (new_i+1)%time_const
							old_name = name
						else: #new worker at the very start
							old_i = i+1
							old_name = name

			# Enter last shift of the two week period
			if old_name != "":
				sh = da.Shift(date, t[old_i-1][0], t[new_i][1])
				self.sched_shifts.append((old_name, sh))

			self.add_das()
			self.da_list_update()

			self.schedule_disp(self.sched_shifts)

			self.logger_update_single("Successfully parsed " + self.schedule_file)
		except:
			self.logger_update_single("ERROR!: Failed to open file. File Not Found")


	def register_disp(self, shifts):
		self.payroll_display.config(state="normal")
		for s in shifts:
			self.payroll_display.insert(END, s[0] + " -- " + str(s[1]) + '\n')
		self.payroll_display.config(state="disabled")

	def schedule_disp(self, shifts):
		self.schedule_display.config(state="normal")
		for s in shifts:
			self.schedule_display.insert(END, s[0] + " -- " + str(s[1]) + '\n')
		self.schedule_display.config(state="disabled")

	def add_das(self):
		# Clear DAs list
		self.das.clear()

		# Update with register DAs
		for s in self.reg_shifts:
			name = s[0]

			if name not in self.das:
				self.das.append(name)

		# Update with schedule DAs
		for s in self.sched_shifts:
			name = s[0]

			if name not in self.das:
				self.das.append(name)

	def da_list_update(self):
		self.da_listbox.delete(0, END)
		self.names = []
		for d in self.das:
			# check to see if duplicate name detected
			n = d.split()

			exists = False
			for na in self.names:
				if na[0].lower() == n[0].lower():
					self.logger_update_single("\tWarning! :: Duplicate name detected: " + na[0] + " :: Possible duplicate added to Desk Assistant list")
					exists = True
				elif len(na) > 1 and len(n) > 1: 
					if na[1].lower() == n[1].lower():
						self.logger_update_single("\tWarning! :: Duplicate name detected: " + na[1] + " :: Possible duplicate added to Desk Assistant list")
						exists = True

			if not exists:
				self.names.append(n)
			# insert the DAs name in here
			self.da_listbox.insert(END, d)

	def load_payroll(self):
		pass

	def csv_reader(self, filename):
		data = []
		with open(filename, 'r') as f:
			r = csv.reader(f)

			for row in r:
				data.append(row)

		return data

	def register_config(self):
		name = 1
		date = 2
		time = 3
		row_offsets = 22
		try:
			with open("register.ini", 'r') as config:
				content = config.readlines()
				content = [x.strip() for x in content]
				content = [x.split("=") for x in content]

			for r in content:
				if r[0] == "name":
					name = r[1]
				if r[0] == "date":
					date = r[1]
				if r[0] == "time":
					time = r[1]
				if r[0] == "row_offsets":
					row_offsets = r[1]
		except:
			# do nothing. ini doesn't exist, we dont care
			pass
		finally:
			register = [name, date, time, row_offsets]
			return register

	def about(self):
		aboutWindow = Toplevel(self.master)
		aboutWindow.minsize(width=400, height=200)
		aboutWindow.maxsize(width=400, height=200)
		aboutWindow.description = Label(aboutWindow, text="Written by Dan Castro-Estremera, former Senior Desk Assistant")
		aboutWindow.description.pack(fill=BOTH, expand=1)

	def logger_update_list(self, data):
		self.logger.config(state="normal")
		for d in data:
			self.logger.insert(END, d)
		self.logger.insert(END, '\n')
		self.logger.see(END)
		self.logger.config(state="disabled")
		pass

	def logger_update_single(self, data):
		self.logger.config(state="normal")
		self.logger.insert(END, data + '\n')
		self.logger.see(END)
		self.logger.config(state="disabled")


def main():
	root = Tk()

	app = PayrollGUI(root)

	root.mainloop()

if __name__ == "__main__":
	main()