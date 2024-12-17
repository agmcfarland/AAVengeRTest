from datetime import datetime
import pytz
import argparse
import logging
from os.path import join as pjoin
import os

def make_time_stamp():
	"""
	Get a time stamp of the run (year_month_day_hr_minute_second)
	Set to United States Eastern Standard Time (EST)
	"""
	now = datetime.now(pytz.timezone('US/Eastern'))
	return f'{now.year}_{now.month}_{now.day}_{now.hour}_{now.minute}_{now.second}'


def make_stamped_run_id(time_stamp, run_id, run_tag):
	return f"{time_stamp}_{run_id}_{run_tag}"


def parse_cli_arguments():
	parser = argparse.ArgumentParser(prog = "AAVengeRTest")

	parser.add_argument('--output_dir', type = str, help = '', metavar = '')
	parser.add_argument('--test_data_sheet', type = str, help = '', metavar = '')
	parser.add_argument('--expected_output_dir', default = '', type = str, help = '', metavar = '')
	parser.add_argument('--microb120_user', type = str, help = '', metavar = '')
	parser.add_argument('--docker_image_name', type = str, help = '', metavar = '')
	parser.add_argument('--aavenger_dir', type = str, help = '', metavar = '')
	parser.add_argument('--docker_source_mount', type = str, help = '', metavar = '')
	parser.add_argument('--docker_target_mount', default = '/data', type = str, help = '', metavar = '')
	
	return parser.parse_args()


class Logger:
	def __init__(self, time_stamp, log_dir: str, log_file: str, level=logging.INFO):
		"""
		Initializes the logger.
		
		:param log_file: Path to the log file.
		:param level: Logging level (e.g., logging.INFO, logging.DEBUG).
		:param fmt: Log message format. If None, a default format is used.
		"""
		self.log_file = log_file
		self.level = level
		self.fmt = '%(asctime)s - %(levelname)s - %(message)s'
		self.logger = None
		self.handler = None

		os.makedirs(log_dir, exist_ok = True)

		self.log_file = pjoin(log_dir, f"{time_stamp}_{log_file}.log")

	def __enter__(self):
		"""
		Set up the logger and file handler when entering the context.
		"""
		self.logger = logging.getLogger(self.log_file)
		self.logger.setLevel(self.level)
		self.handler = logging.FileHandler(self.log_file)
		formatter = logging.Formatter(self.fmt)
		self.handler.setFormatter(formatter)
		self.logger.addHandler(self.handler)
		return self.logger

	def __exit__(self, exc_type, exc_value, traceback):
		"""
		Close and clean up the file handler when exiting the context.
		"""
		if self.handler:
			self.handler.close()
			self.logger.removeHandler(self.handler)





