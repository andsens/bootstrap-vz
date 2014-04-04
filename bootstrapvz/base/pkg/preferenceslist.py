

class PreferenceLists(object):
	"""Represents a list of preferences lists for apt
	"""

	def __init__(self, manifest_vars):
		"""
		Args:
			manifest_vars (dict): The manifest variables
		"""
		# A dictionary with the name of the file in preferences.d as the key
		# That values are lists of Preference objects
		self.preferences = {}
		# Save the manifest variables, we need the later on
		self.manifest_vars = manifest_vars

	def add(self, name, preferences):
		"""Adds a preference to the apt preferences list

		Args:
			name (str): Name of the file in preferences.list.d, may contain manifest vars references
			preferences (object): The preferences
		"""
		name = name.format(**self.manifest_vars)
                self.preferences[name] = [Preference(p) for p in preferences]


class Preference(object):
	"""Represents a single preference
	"""

	def __init__(self, preference):
		"""
		Args:
			preference (dict): A apt preference dictionary

		Raises:
			PreferenceError
		"""
                self.preference = preference

	def __str__(self):
		"""Convert the object into a preference block

		Returns:
			string.
		"""
                return "Package: {package}\nPin: {pin}\nPin-Priority: {pin-priority}\n".format(**self.preference)
