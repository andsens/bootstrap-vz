

class Phase(object):
    """The Phase class represents a phase a task may be in.
    It has no function other than to act as an anchor in the task graph.
    All phases are instantiated in common.phases
    """

    def __init__(self, name, description):
        # The name of the phase
        self.name = name
        # The description of the phase (currently not used anywhere)
        self.description = description

    def pos(self):
        """Gets the position of the phase

        :return: The positional index of the phase in relation to the other phases
        :rtype: int
        """
        from bootstrapvz.common.phases import order
        return next(i for i, phase in enumerate(order) if phase is self)

    def __cmp__(self, other):
        """Compares the phase order in relation to the other phases
        :return int:
        """
        return self.pos() - other.pos()

    def __str__(self):
        """
        :return: String representation of the phase
        :rtype: str
        """
        return self.name
