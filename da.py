class DeskAssistant:
	def __init__(self, name):
		self.name = name
		self.shifts = []


	def add_shift(self, date, start_time, end_time):
		self.shifts.append(Shift(date, start_time, end_time))

	def get_shifts(self, date):
		pass
	
	def get_shifts(self):
		pass

class Shift:
	def __init__(self, date, start_time, end_time):
		self.date = date
		self.start_time = Time(start_time)
		self.end_time = Time(end_time)

	def __str__(self):
		return self.date + " | " + str(self.start_time) + " - " + str(self.end_time)
	
class Time:
	def __init__(self, time):
		self.str_time = time

	def __str__(self):
		return self.str_time

	def __repr__(self):
		return self.str_time