
from devsim import *
from equation_builder import *

class Region:
	
	def __init__(self, device, region, solutionVariables, variableUpdates):
		self._device = device
		self._region = region
		self._solutionVariables = solutionVariables
		self._variableUpdates = variableUpdates
		self._equations = {}
		self._models = []
	
		for i, j in zip(solutionVariables, variableUpdates):
			self._equations[i] = EquationBuilder(device, region, i,
															solutionVariables, j)
		
	def addModel(self, model, solutionVariable=None, modelType=None):
		self._models.append(model)
		if solutionVariable is not None and modelType is not None:
			self._equations[solutionVariable].deleteModel(model, modelType)
		

	def deleteModel(self, model, solutionVariable=None, modelType=None):
		self._models.remove(model)
		if solutionVariable is not None and modelType is not None:
			self._equations[solutionVariable].deleteModel(model, modelType)

	def addModels(self, models):
		for model in models:
			self.addModel(model[0], model[1], model[2])

	def deleteModels(self, models):
		for model in models:
			self.deleteModel(model[0], model[1], model[2])

	def build(self):
		for equation in self._equations:
			equation.buildEquation()
