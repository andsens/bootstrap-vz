

class PreferenceLists(object):
    """Represents a list of preferences lists for apt
    """

    def __init__(self, manifest_vars):
        """
        :param dict manifest_vars: The manifest variables
        """
        # A dictionary with the name of the file in preferences.d as the key
        # That values are lists of Preference objects
        self.preferences = {}
        # Save the manifest variables, we need the later on
        self.manifest_vars = manifest_vars

    def add(self, name, preferences):
        """Adds a preference to the apt preferences list

        :param str name: Name of the file in preferences.list.d, may contain manifest vars references
        :param object preferences: The preferences
        """
        name = name.format(**self.manifest_vars)
        self.preferences[name] = [Preference(p) for p in preferences]


class Preference(object):
    """Represents a single preference
    """

    def __init__(self, preference):
        """
        :param dict preference: A apt preference dictionary
        """
        self.preference = preference

    def __str__(self):
        """Convert the object into a preference block

        :rtype: str
        """
        return "Package: {package}\nPin: {pin}\nPin-Priority: {pin-priority}\n".format(**self.preference)
