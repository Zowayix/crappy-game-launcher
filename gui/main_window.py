import os
from threading import Thread

import wx
import wx.adv

import config
import mame_helpers
import scummvm
import steam
import main

from .gui_generated import MeowLauncherGui

start_work_event_type = wx.NewEventType()
start_work_event_binder = wx.PyEventBinder(start_work_event_type)
work_done_event_type = wx.NewEventType()
work_done_event_binder = wx.PyEventBinder(work_done_event_type)
progress_event_type = wx.NewEventType()
progress_event_binder = wx.PyEventBinder(progress_event_type)

class StartWorkEvent(wx.PyCommandEvent):
	def __init__(self):
		super().__init__(start_work_event_type)

class WorkDoneEvent(wx.PyCommandEvent):
	def __init__(self):
		super().__init__(work_done_event_type)

class ProgressEvent(wx.PyCommandEvent):
	def __init__(self, data, should_increment):
		super().__init__(progress_event_type)
		self.data = data
		self.should_increment = should_increment

class WorkerThread(Thread):
	def __init__(self, wx_object, enabled_state):
		super().__init__()
		self.wx_object = wx_object
		self.enabled_state = enabled_state

	def send_progress_event(self, data, should_increment):
		event = ProgressEvent(data, should_increment)
		wx.PostEvent(self.wx_object, event)

	def run(self):
		start_event = StartWorkEvent()
		wx.PostEvent(self.wx_object, start_event)
		main.main(lambda data, should_increment: self.send_progress_event(data, should_increment), *self.enabled_state)
		done_event = WorkDoneEvent()
		wx.PostEvent(self.wx_object, done_event)

class MainWindow(MeowLauncherGui):
	def __init__(self, parent):
		super().__init__(parent)
		self.optionsSizer = self.optionsPanel.GetSizer() #wxFormBuilder won't put it as a property of the main window object
		self.Icon = wx.Icon('gui/icon.png')
		self.setupStuff()

		self.workerThread = None
		self.Bind(start_work_event_binder, self.on_worker_started)
		self.Bind(work_done_event_binder, self.on_worker_done)
		self.Bind(progress_event_binder, self.on_progress)
		self.running_game_types = 0

	def setupStuff(self):
		self.setupMainButtons()
		self.setupRuntimeOptions()

	def setupRuntimeOptions(self):
		for name, opt in config.get_runtime_options().items():
			#TODO These might not always be bools
			checkbox = wx.CheckBox(self.optionsPanel, name=name, label=opt.name)
			checkbox.Value = opt.default_value
			checkbox.SetToolTip(wx.ToolTip(opt.description))
			self.optionsSizer.Add(checkbox, 0, wx.ALL, 5)

	def setupMainButtons(self):
		self.mameMachineCheckBox.Enabled = mame_helpers.have_mame()
		#Is there any condition in which it would make sense to disable the "roms" check box?
		self.macCheckBox.Enabled = os.path.isfile(config.mac_ini_path)
		self.dosCheckBox.Enabled = os.path.isfile(config.dos_ini_path)
		self.scummvmCheckBox.Enabled = scummvm.have_something_vm()
		self.steamCheckBox.Enabled = steam.is_steam_available()

	def loadRuntimeOptions(self):
		for checkbox_sizer_item in self.optionsSizer.GetChildren():
			checkbox = checkbox_sizer_item.GetWindow()
			config.main_config.runtime_overrides[checkbox.Name] = checkbox.IsChecked()

	def okButtonOnButtonClick(self, event):
		self.loadRuntimeOptions()
		enabled_state = (self.mameMachineCheckBox.IsChecked(), self.romsCheckBox.IsChecked(), self.dosCheckBox.IsChecked(), self.macCheckBox.IsChecked(), self.scummvmCheckBox.IsChecked(), self.steamCheckBox.IsChecked())
		self.running_game_types = len([state for state in enabled_state if state])
		self.workerThread = WorkerThread(self, enabled_state)
		self.workerThread.start()

	def exitButtonOnButtonClick(self, event):
		self.Close()

	def on_worker_started(self, event):
		self.okButton.Disable()
		self.progressBar.Value = 0
		self.progressBar.Range = self.running_game_types + 4 #For the removing of old folder, remove non-existing games, disambiguation, and organization of folders

	def on_worker_done(self, event):
		self.okButton.Enable()
		self.progressBar.Value = 0
		notification = wx.adv.NotificationMessage('Meow Launcher', 'Done creating launchers! Have fun!', self)
		notification.Show()

	def on_progress(self, event):
		if event.should_increment:
			self.progressBar.Value += 1
		if event.data:
			self.progressLabel.Label = event.data