#!/usr/bin/python3
#	vacationplanner - Small script to plan vacation days
#	Copyright (C) 2018-2018 Johannes Bauer
#
#	This file is part of vacationplanner.
#
#	vacationplanner is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; this program is ONLY licensed under
#	version 3 of the License, later versions are explicitly excluded.
#
#	vacationplanner is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with vacationplanner; if not, write to the Free Software
#	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#	Johannes Bauer <JohannesBauer@gmx.de>

import datetime
import sys
import json
from FriendlyArgumentParser import FriendlyArgumentParser

class Period(object):
	def __init__(self, start, end = None):
		self._start = start
		self._end = end or start
		assert(self._start <= self._end)

	@classmethod
	def from_str(cls, start, end = None):
		start = cls._parse(start)
		end = cls._parse(end) if (end is not None) else None
		return cls(start, end)

	@classmethod
	def from_json_obj(cls, json_obj):
		if isinstance(json_obj, str):
			return cls.from_str(json_obj)
		else:
			return cls.from_str(json_obj[0], json_obj[1])

	@property
	def start(self):
		return self._start

	@property
	def end(self):
		return self._end

	@classmethod
	def _parse(cls, datespec):
		return datetime.datetime.strptime(datespec, "%Y-%m-%d").date()

	def get_weekends(self):
		for day in self:
			if day.weekday() in [ 5, 6 ]:
				yield day

	def __iter__(self):
		cur = self.start
		while cur <= self.end:
			yield cur
			cur = cur + datetime.timedelta(1)

	def __str__(self):
		if self.start == self.end:
			return "Period<%s>" % (self.start)
		else:
			return "Period<%s - %s>" % (self.start, self.end)


def isodate(text):
	return datetime.datetime.strptime(text, "%Y-%m-%d").date()

parser = FriendlyArgumentParser()
parser.add_argument("-e", "--eligibility", metavar = "period", type = str, help = "Eligibility period. Show the period with the current year's name by default.")
parser.add_argument("-n", "--no-merge", action = "store_true", help = "Do not merge subsequent vacation days into one block.")
parser.add_argument("-t", "--to-day", metavar = "date", type = isodate, help = "Only consider period until the given date. Needs to be ISO format, i.e., yyyy-mm-dd.")
parser.add_argument("infile", metavar = "json", type = str, help = "Input file to parse.")
args = parser.parse_args(sys.argv[1:])

with open(args.infile) as f:
	data = json.load(f)

eligibility = args.eligibility or datetime.datetime.now().strftime("%Y")
if eligibility not in data.get("eligibility", { }):
	raise KeyError("Input file has no 'eligibility' section or eligibility section has no '%s' key." % (eligibility))
eligibility = data["eligibility"][eligibility]

# Get the full period first
full_period = Period.from_json_obj(eligibility["period"])

# Restrict if given on command line
if args.to_day is not None:
	full_period = Period(full_period.start, args.to_day)

# No work on weekends
required_work = { day: 1 for day in full_period }
for day in full_period.get_weekends():
	required_work[day] = 0

# Get all holiday periods (only single days!)
holiday_periods = { Period.from_str(hdict["day"]): hdict.get("value", 1) for hdict in data["holidays"] }
for (hperiod, subtract_amount) in holiday_periods.items():
	if hperiod.start in required_work:
		required_work[hperiod.start] -= subtract_amount

# Then go to vacation
vacation_taken = 0
vacation_days = { }
for request in data["request"]:
	if not request.get("active", True):
		continue

	period = Period.from_json_obj(request["period"])

	for vacation_day in period:
		if vacation_day not in required_work:
			# This isn't applicable to this period
			continue
		need_to_work = required_work[vacation_day]
		if need_to_work > 0:
			vacation_days[vacation_day] = need_to_work
			vacation_taken += need_to_work

if args.no_merge:
	for (vacation_day, need_to_work) in vacation_days.items():
		print("%-25s %.1f days" % (vacation_day.strftime("%A, %d.%m.%Y"), need_to_work))
else:
	def print_range(start_day, end_day, need_work_sum):
		if start_day is not None:
			if start_day == end_day:
				print("%-53s %.1f days" % (start_day.strftime("%A, %d.%m.%Y"), need_work_sum))
			else:
				print("%-25s - %-25s %.1f days" % (start_day.strftime("%A, %d.%m.%Y"), end_day.strftime("%A, %d.%m.%Y"), need_work_sum))

	start_day = None
	end_day = None
	need_work_sum = 0
	for (vacation_day, need_to_work) in vacation_days.items():
		if (start_day is None) or (end_day + datetime.timedelta(1) != vacation_day):
			print_range(start_day, end_day, need_work_sum)
			start_day = vacation_day
			end_day = vacation_day
			need_work_sum = need_to_work
		elif end_day + datetime.timedelta(1) == vacation_day:
			end_day = vacation_day
			need_work_sum += need_to_work
	print_range(start_day, end_day, need_work_sum)

print("~" * 80)
shifted_from_prev = eligibility.get("shift_from_prev", 0)
shifted_into_next = eligibility.get("shift_into_next", 0)
allowance = eligibility["days"]
effective_allowance = allowance + shifted_from_prev - shifted_into_next
print("Period             : %s to %s" % (full_period.start.strftime("%d.%m.%Y"), full_period.end.strftime("%d.%m.%Y")))
print("Vacation allowance : %.1f days" % (allowance))
if shifted_from_prev > 0:
	print("Shifted from prev  : %.1f days" % (shifted_from_prev))
if shifted_into_next > 0:
	print("Shifted into next  : %.1f days" % (shifted_into_next))
print("Effective allowance: %.1f days" % (effective_allowance))
print("Vacation taken     : %.1f days" % (vacation_taken))
print("Vacation remaining : %.1f days" % (effective_allowance - vacation_taken))
