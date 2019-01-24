class MissingModelError(Exception):
	def __init__(self, cls, package):
		self._expression = "Missing Class: {0} from Package: {1}".format(cls,package)

		super(MissingModelError, self).__init__(self._expression)
