
import inspect


class Factory:
	@classmethod
	def generateModel(cls, device, region, model, carrier = None):
		if model in cls.models:
			if carrier is not None:
				return cls.models[model](device, region, carrier)
			else:
				return cls.models[model](device, region)

	def generateFactory(factoryClass):
		retrievedModels = factoryClass.__subclasses__()
		modelNames = [clazz.__name__ for clazz in retrievedModels]
		return dict(zip(modelNames, retrievedModels))

	@classmethod
	def getModels(cls):
		return list(cls.models.keys())

	@classmethod
	def getParams(cls, model):
		return inspect.getargspec(cls.models[model])

