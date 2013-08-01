from base import Task
from common import phases
import os.path

class Fake(Task):
	description = 'create fake file'
	phase = phases.system_modification

	def run(self, info):
		fake_path = os.path.join(info.root, 'fake.txt')
		with open(fake_path, 'a') as fakefile:
			fakefile.write("fake file")

