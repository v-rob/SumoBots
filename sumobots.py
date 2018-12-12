import wx
from datetime import datetime
from time import sleep
from os.path import exists
import json
from itertools import combinations
from operator import itemgetter
from random import shuffle
from copy import deepcopy

class SumoBots(wx.Frame):
	year = str(datetime.now().year)
	
	def __init__(self):
		"""Construct the starting window."""
		wx.Frame.__init__(self, None, title = "SHHS SumoBots " + self.year, size = (1200, 650), style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
		self.panel = wx.Panel(self)
		
		self.GetData() # Get the data
		self.MainApp() # Initialize the GUI
		
		self.Centre()
		self.Show()
	
	def MainApp(self):
		"""Initialize the program GUI."""
		self.matchNow = wx.StaticText(self.panel, label = "", pos = (500, 43), size = (650, 32), style = wx.ALIGN_CENTRE_HORIZONTAL | wx.ST_NO_AUTORESIZE)
		self.matchNow.SetFont(wx.Font(20, wx.FONTFAMILY_TELETYPE, wx.NORMAL, wx.BOLD))
		
		self.nextMatches = wx.TextCtrl(self.panel, pos = (500, 75), size = (650, 495), style = wx.TE_MULTILINE | wx.NO_BORDER | wx.TE_CENTRE | wx.TE_READONLY)
		self.nextMatches.SetBackgroundColour(self.panel.GetBackgroundColour())
		self.nextMatches.SetFont(wx.Font(15, wx.FONTFAMILY_TELETYPE, wx.NORMAL, wx.BOLD))
		
		self.matchesLeft = wx.StaticText(self.panel, label = "", pos = (500, 575), size = (650, 32), style = wx.ALIGN_CENTRE_HORIZONTAL | wx.ST_NO_AUTORESIZE)
		self.matchesLeft.SetFont(wx.Font(20, wx.FONTFAMILY_TELETYPE, wx.NORMAL, wx.BOLD))
		
		self.win1 = wx.Button(self.panel, label = "Win", pos = (600, 10), size = (100, 25))
		self.Bind(wx.EVT_BUTTON, lambda x: self.UpdateTeams(winner = 0), self.win1)
		
		self.tie = wx.Button(self.panel, label = "Tie", pos = (775, 10), size = (100, 25))
		self.Bind(wx.EVT_BUTTON, lambda x: self.UpdateTeams(winner = 2), self.tie)
		
		self.win2 = wx.Button(self.panel, label = "Win", pos = (950, 10), size = (100, 25))
		self.Bind(wx.EVT_BUTTON, lambda x: self.UpdateTeams(winner = 1), self.win2)
		
		# Main list of teams
		self.teamsList = wx.ListCtrl(self.panel, -1, style = wx.LC_REPORT | wx.LC_SORT_ASCENDING, pos = (10, 10), size = (475, 560))
		self.teamsList.InsertColumn(0, "Rank", width = 75)
		self.teamsList.InsertColumn(1, "Name", width = 250)
		self.teamsList.InsertColumn(2, "Points", width = 75)
		self.teamsList.InsertColumn(3, "Plays", width = 75)
		self.teamsList.SetFont(wx.Font(13, wx.FONTFAMILY_TELETYPE, wx.NORMAL, wx.NORMAL))
		
		self.UpdateTeams()
		
		self.Bind(wx.EVT_CLOSE, lambda x: self.Exit())
		
		self.editAspects = wx.Button(self.panel, label = "Edit Aspects...", pos = (45, 578), size = (100, 25))
		self.Bind(wx.EVT_BUTTON, lambda x: self.ResetDialog(), self.editAspects)
		
		self.editNames = wx.Button(self.panel, label = "Edit Names...", pos = (155, 578), size = (100, 25))
		self.Bind(wx.EVT_BUTTON, lambda x: self.EditNames(), self.editNames)
		
		self.editScores = wx.Button(self.panel, label = "Edit Scores...", pos = (265, 578), size = (100, 25))
		self.Bind(wx.EVT_BUTTON, lambda x: self.EditScores(), self.editScores)
		
		self.exit = wx.Button(self.panel, label = "Exit", pos = (375, 578), size = (100, 25))
		self.Bind(wx.EVT_BUTTON, lambda x: self.Exit(), self.exit)
		
		self.teamsList.SetFocus()
	
	def CalcMatches(self):
		"""Calculate all possible matches."""
		self.data["match"] = 0
		team = list(range(len(self.data["teams"])))
		self.data["lineup"] = combinations(team, 2)
		self.data["lineup"] = list(self.data["lineup"])
		shuffle(self.data["lineup"])
		for battle in self.data["lineup"]:
			shuffle(list(battle))
	
	# https://stackoverflow.com/questions/3071415/efficient-method-to-calculate-the-rank-vector-of-a-list-in-python,
	# This function is from the above URL, fifth answer.  Licensed under CC BY-SA.
	def GetRank(self, vector):
		a={}
		rank=1
		for num in sorted(vector, reverse = True):
			if num not in a:
				a[num]=rank
				rank=rank+1
		return[a[i] for i in vector]
	
	def UpdateTeams(self, winner = -1):
		"""Update the teams list and change the current match."""
		if winner > -1 and not len(self.data["lineup"]) <= self.data["match"]:
			
			if winner == 2:
				apoints = 1
				bpoints = 1
				winner = 0
			elif winner == 0 or winner == 1:
				apoints = 2
				bpoints = 0
			
			team_win = self.data["teams"][self.data["lineup"][self.data["match"]][winner]]
			team_win[1] = team_win[1] + apoints
			team_win[2] = team_win[2] + 1
			
			if winner == 1:
				loser = 0
			else:
				loser = 1
			team_lose = self.data["teams"][self.data["lineup"][self.data["match"]][loser]]
			team_lose[1] = team_lose[1] + bpoints
			team_lose[2] = team_lose[2] + 1
			
			self.data["match"] = self.data["match"] + 1
		
		scores = []
		for team in self.data["teams"]:
			scores.insert(-1, team[1])
		rank = self.GetRank(scores)
		
		for team_no, team in enumerate(self.data["teams"]):
			for score_no, score in enumerate(scores):
				if team[1] == score:
					self.data["teams"][team_no][3] = rank[score_no]
		
		sorted(self.data["teams"], key = itemgetter(3))
		
		self.teamsList.DeleteAllItems()
		for no, team in enumerate(self.data["teams"]):
			index = self.teamsList.InsertItem(no, str(team[3]))
			self.teamsList.SetItem(index, 1, team[0])
			self.teamsList.SetItem(index, 2, str(team[1]))
			self.teamsList.SetItem(index, 3, str(team[2]))
		
		self.matchNow.SetLabel(self.RetrieveLineup())
		lineupText = ""
		for no in range(len(self.data["lineup"]) - self.data["match"] - 1):
			lineupText = lineupText + self.RetrieveLineup(no + 1, True) + "\n"
		self.nextMatches.Clear()
		self.nextMatches.AppendText(lineupText)
		self.nextMatches.ShowPosition(0)
		
		if self.data["match"] + 1 > len(self.data["lineup"]):
			self.matchesLeft.SetLabel("Game Completed!")
		else:
			self.matchesLeft.SetLabel("Match " + str(self.data["match"] + 1) + " of " + str(len(self.data["lineup"])))
		
		self.Save()
	
	def EditScores(self):
		"""Show the Edit Scores dialog."""
		self.dialog = wx.Dialog(self, title = "Edit Scores...", style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX))
		teamz = []
		for no, team in enumerate(self.data["teams"]):
			wx.StaticText(self.dialog, pos = (10, 25 * no + 10), label = team[0])
		
		for no, team in enumerate(self.data["teams"]):
			teamz.insert(no, wx.TextCtrl(self.dialog, pos = (125, 25 * no + 7)))
			teamz[no].AppendText(str(self.data["teams"][no][1]))
		
		self.dialogSave = wx.Button(self.dialog, label = "Save", pos = (245, 6), size = (100, 25))
		self.dialog.Bind(wx.EVT_BUTTON, lambda x: self.Edit(teamz, 0), self.dialogSave)
		
		self.dialogCancel = wx.Button(self.dialog, label = "Cancel", pos = (245, 36), size = (100, 25))
		self.dialog.Bind(wx.EVT_BUTTON, lambda x: self.dialog.Close(), self.dialogCancel)
		
		self.dialogError = wx.StaticText(self.dialog, label = "", pos = (245, 66))
		
		if len(self.data["teams"]) * 25 + 50 > 130:
			self.dialog.SetSize(0, 0, 370, len(self.data["teams"]) * 25 + 50)
		else:
			self.dialog.SetSize(0, 0, 370, 130)
		self.dialog.Centre()
		self.dialog.ShowModal()
	
	def EditNames(self):
		"""Show the Edit Names dialog."""
		self.dialog = wx.Dialog(self, title = "Edit Team Names...", style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX))
		teamz = []
		for no, team in enumerate(self.data["teams"]):
			wx.StaticText(self.dialog, pos = (10, 25 * no + 10), label = team[0])
		
		for no, team in enumerate(self.data["teams"]):
			teamz.insert(no, wx.TextCtrl(self.dialog, pos = (125, 25 * no + 7)))
			teamz[no].AppendText(str(self.data["teams"][no][0]))
		
		self.dialogSave = wx.Button(self.dialog, label = "Save", pos = (245, 6), size = (100, 25))
		self.dialog.Bind(wx.EVT_BUTTON, lambda x: self.Edit(teamz, 1), self.dialogSave)
		
		self.dialogCancel = wx.Button(self.dialog, label = "Cancel", pos = (245, 36), size = (100, 25))
		self.dialog.Bind(wx.EVT_BUTTON, lambda x: self.dialog.Close(), self.dialogCancel)
		
		self.dialogError = wx.StaticText(self.dialog, label = "", pos = (245, 66))
		
		if len(self.data["teams"]) * 25 + 50 > 130:
			self.dialog.SetSize(0, 0, 370, len(self.data["teams"]) * 25 + 50)
		else:
			self.dialog.SetSize(0, 0, 370, 130)
		self.dialog.Centre()
		self.dialog.ShowModal()
	
	def NewTeamsWarning(self):
		"""Show the warning and get number of teams before show the New Teams dialog."""
		self.dialog.Close()
		self.dialog = wx.Dialog(self, title = "Number of Teams", size = (370, 140), style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX))
		
		wx.StaticText(self.dialog, pos = (10, 10), label = "Warning! This will delete all previous data.")
		wx.StaticText(self.dialog, pos = (10, 40), label = "Number of Teams:")
		
		self.dialogNumTeams = wx.TextCtrl(self.dialog, pos = (125, 37))
		
		self.dialogOk = wx.Button(self.dialog, label = "OK", pos = (245, 6), size = (100, 25))
		self.dialog.Bind(wx.EVT_BUTTON, lambda x: self.NewTeams(self.dialogNumTeams.GetValue()), self.dialogOk)
		
		self.dialogCancel = wx.Button(self.dialog, label = "Cancel", pos = (245, 36), size = (100, 25))
		self.dialog.Bind(wx.EVT_BUTTON, lambda x: self.dialog.Close(), self.dialogCancel)
		
		# self.dialogDelete = wx.Button(self.dialog, label = "Reset...", pos = (245, 66), size = (100, 25))
		# self.dialog.Bind(wx.EVT_BUTTON, lambda x: self.ResetDialog(), self.dialogDelete)
		
		self.dialogError = wx.StaticText(self.dialog, label = "", pos = (10, 70))
		
		self.dialog.Centre()
		self.dialog.ShowModal()
	
	def ResetDialog(self):
		"""Reset certain aspects of the match."""
		self.dialog = wx.Dialog(self, title = "Data Edit...", size = (355, 165), style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX))
		
		wx.StaticText(self.dialog, pos = (10, 70), label = "Jump to match:")
		
		self.dialogMatchJump = wx.TextCtrl(self.dialog, pos = (120, 67), size = (100, 23))
		
		self.dialogJump = wx.Button(self.dialog, label = "Jump", pos = (230, 66), size = (100, 25))
		self.dialog.Bind(wx.EVT_BUTTON, lambda x: self.Reset(-1, self.dialogMatchJump.GetValue()), self.dialogJump)
		
		self.dialogCancel = wx.Button(self.dialog, label = "Close", pos = (230, 96), size = (100, 25))
		self.dialog.Bind(wx.EVT_BUTTON, lambda x: self.dialog.Close(), self.dialogCancel)
		
		self.dialogResetAll = wx.Button(self.dialog, label = "Reset Points", pos = (10, 36), size = (100, 25))
		self.dialog.Bind(wx.EVT_BUTTON, lambda x: self.Reset(3), self.dialogResetAll)
		
		self.dialogNewTeams = wx.Button(self.dialog, label = "New Teams...", pos = (120, 36), size = (100, 25))
		self.dialog.Bind(wx.EVT_BUTTON, lambda x: self.NewTeamsWarning(), self.dialogNewTeams)
		
		self.dialogUltCheat = wx.Button(self.dialog, label = "Ultimate Cheat", pos = (230, 36), size = (100, 25))
		self.dialog.Bind(wx.EVT_BUTTON, lambda x: self.dialogError.SetLabel("Gotcha! Nothin' here."), self.dialogUltCheat)
		
		self.dialogResetAll = wx.Button(self.dialog, label = "Reset All", pos = (10, 6), size = (100, 25))
		self.dialog.Bind(wx.EVT_BUTTON, lambda x: self.Reset(0), self.dialogResetAll)
		
		self.dialogResetMatches = wx.Button(self.dialog, label = "Reset Matches", pos = (120, 6), size = (100, 25))
		self.dialog.Bind(wx.EVT_BUTTON, lambda x: self.Reset(1), self.dialogResetMatches)
		
		self.dialogRecalcMatches = wx.Button(self.dialog, label = "Recalc Matches", pos = (230, 6), size = (100, 25))
		self.dialog.Bind(wx.EVT_BUTTON, lambda x: self.Reset(2), self.dialogRecalcMatches)
		
		self.dialogError = wx.StaticText(self.dialog, label = "", pos = (10, 100))
		
		self.dialog.Centre()
		self.dialog.ShowModal()
	
	def Reset(self, type, match = None):
		if type == 0:
			# Delete all data.
			self.data = deepcopy(self.defaultData)
			self.dialog.Close()
			self.CalcMatches()
			self.UpdateTeams()
		elif type == 1:
			# Reset match to 0.
			self.data["match"] = 0
			for team in self.data["teams"]:
				team[1] = 0
				team[2] = 0
				team[3] = 0
			self.dialog.Close()
			self.UpdateTeams()
		elif type == 2:
			# Recalculate match lineup and reset points.
			self.CalcMatches()
			self.data["match"] = 0
			for team in self.data["teams"]:
				team[1] = 0
				team[2] = 0
				team[3] = 0
			self.dialog.Close()
			self.UpdateTeams()
		elif type == 3:
			# Set all points to 0.
			for team in self.data["teams"]:
				team[1] = 0
				team[2] = 0
				team[3] = 0
			self.dialog.Close()
			self.UpdateTeams()
		else:
			# Jump to a specified match.
			if match.isdigit() and int(match) - 1 <= len(self.data["lineup"]) and int(match) - 1 >= 0:
				self.data["match"] = int(match) - 1
				self.dialog.Close()
				self.UpdateTeams()
			else:
				self.dialogError.SetLabel("Error: Invalid match.")
	
	def NewTeams(self, amount):
		"""Show the New Teams dialog."""
		if amount.isdigit() and int(amount) > 1 and int(amount) <= 30:
			amount = int(amount)
			self.dialog.Close()
			
			self.dialog = wx.Dialog(self, title = "New Teams...", style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX))
			teamz = []
			for no in range(amount):
				wx.StaticText(self.dialog, pos = (10, 25 * no + 10), label = "Team " + str(no + 1))
			
			for no in range(amount):
				teamz.insert(no, wx.TextCtrl(self.dialog, pos = (75, 25 * no + 7)))
			
			self.dialogSave = wx.Button(self.dialog, label = "Save", pos = (195, 6), size = (100, 25))
			self.dialog.Bind(wx.EVT_BUTTON, lambda x: self.Edit(teamz, 2), self.dialogSave)
			
			self.dialogCancel = wx.Button(self.dialog, label = "Cancel", pos = (195, 36), size = (100, 25))
			self.dialog.Bind(wx.EVT_BUTTON, lambda x: self.dialog.Close(), self.dialogCancel)
			
			self.dialogError = wx.StaticText(self.dialog, label = "", pos = (195, 66))
			
			if amount * 25 + 50 > 130:
				self.dialog.SetSize(0, 0, 320, amount * 25 + 50)
			else:
				self.dialog.SetSize(0, 0, 320, 130)
			self.dialog.Centre()
			self.dialog.ShowModal()
		else:
			self.dialogError.SetLabel("Error: Invalid number of teams.")
	
	def Edit(self, edit, type):
		"""Save the input from a dialog."""
		if type == 0:
			# Change the scores.
			valid = True
			for no, team in enumerate(edit):
				if not team.GetValue().isdigit():
					valid = False
					self.dialogError.SetLabel("Invalid score.")
			
			if valid == True:
				for no, team in enumerate(edit):
					self.data["teams"][no][1] = int(team.GetValue())
				self.UpdateTeams()
				self.dialog.Close()
			
		elif type == 1:
			# Change the team names.
			valid = True
			for no, team in enumerate(edit):
				if len(team.GetValue()) > 20 or len(team.GetValue()) == 0:
					valid = False
					self.dialogError.SetLabel("Invalid name length.")
				if valid == True:
					for exno, exteam in enumerate(self.data["teams"]):
						if no != exno and team.GetValue() == exteam[0]:
							valid = False
							self.dialogError.SetLabel("Name already exists.")
					if valid == True:
						for exno, exteam in enumerate(edit):
							if no != exno and team.GetValue() == exteam.GetValue():
								valid = False
								self.dialogError.SetLabel("Name already exists.")
			
			if valid == True:
				for no, team in enumerate(edit):
					self.data["teams"][no][0] = team.GetValue()
				self.UpdateTeams()
				self.dialog.Close()
		elif type == 2:
			# Make new teams.
			valid = True
			for no, team in enumerate(edit):
				if len(team.GetValue()) > 20 or len(team.GetValue()) == 0:
					valid = False
					self.dialogError.SetLabel("Invalid name length.")
				if valid == True:
					for exno, exteam in enumerate(edit):
						if no != exno and team.GetValue() == exteam.GetValue():
							valid = False
							self.dialogError.SetLabel("Name already exists.")
			
			if valid == True:
				self.data = deepcopy(self.defaultData)
				for no, team in enumerate(edit):
					self.data["teams"].insert(no, [team.GetValue(), 0, 0, 0])
				self.CalcMatches()
				self.UpdateTeams()
				self.dialog.Close()
	
	def Save(self):
		"""Save the data."""
		with open("sumobots.json", "w") as file:
			json.dump(self.data, file)
	
	def Exit(self):
		"""Save and exit the program."""
		self.Save()
		self.Destroy()
	
	def RetrieveLineup(self, modifier = 0, big = False):
		if len(self.data["lineup"]) - 1 >= self.data["match"] + modifier:
			
			# Calculate length to add padding
			maxlen = 0
			for team in self.data["teams"]:
				if len(team[0]) > maxlen:
					maxlen = len(team[0])
			
			team1 = self.data["teams"][self.data["lineup"][self.data["match"] + modifier][0]][0]
			team2 = self.data["teams"][self.data["lineup"][self.data["match"] + modifier][1]][0]
			team1 = " " * (maxlen - len(team1)) + team1
			team2 = team2 + " " * (maxlen - len(team2))
			
			if big == True:
				vs = "   vs.   "
			else:
				vs = "  vs.  "
			
			return team1 + vs + team2
		else:
			return ""
	
	def GetData(self):
		if exists("sumobots.json"):
			with open("sumobots.json") as file:
				self.data = json.load(file)
		else:
			self.data = deepcopy(self.defaultData)
		if self.data["match"] == -1:
			self.CalcMatches()
	
	defaultData = {
		"teams" : [],
		"lineup" : [],
		"match" : -1
	}

app = wx.App()
top = SumoBots()
top.Show()
app.MainLoop()