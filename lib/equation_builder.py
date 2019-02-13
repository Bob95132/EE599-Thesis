
from devsim import *
from util.model import *
from util.model_create import *

class EquationBuilder:

	def __init__(self, device, region, 
					solutionVariable, derivatives, variableUpdate):
		self._device = device
		self._region = region
		self._derivatives = derivatives
		self._solutionVariable = solutionVariable
		self._variableUpdate = variableUpdate
		self.reset()
		self._modelLists = {"NodeModel": self._nodeModels,
								  "TimeNodeModel" : self._timeNodeModels,
								  "EdgeModel" : self._edgeModels,
								  "EdgeVolumeModel" : self._edgeVolumeModels,	
								  "ElementModel" : self._elementModels,
								  "ElementVolumeModel" : self._volumeModels}

	def addModel(self, model, modelType):
		self._modelLists[modelType].append(model)

	def deleteModel(self, model, modelType):
		self._modelLists[modelType].remove(model)

	def reset(self):
		self._nodeModels = []
		self._timeNodeModels = []
		self._edgeModels = []
		self._edgeVolumeModels = []
		self._elementModels = []
		self._volumeModels = []

	def buildEquation(self):
		expressions = {}

		for key, value in self._modelLists.items():
			if len(value) > 0:
				expressions[key] = self._solutionVariable+key
				combinedModels = " + ".join(value)
			else:
				expressions[key] = ""
				combinedModels = None
				

			if combinedModels is not None:
				if "Node" in key:
					CreateNodeModel(self._device, self._region, 
									self._solutionVariable+key, combinedModels)
					CreateNodeModelDerivative(self._device, self._region,
									self._solutionVariable+key, combinedModels,
									self._derivatives)

				if "Edge" in key:
					CreateEdgeModel(self._device, self._region,
									self._solutionVariable+key, combinedModels)
					CreateEdgeModelDerivatives(self._device, self._region,
									self._solutionVariable+key, combinedModels,
									self._derivatives)
			
				if "Element" in key:
					CreateElementModel(self._device, self._region,
											self._solutionVariable+key, combinedModels)
					CreateElementModelDerivative(self._device, self._region,
									self._solutionVariable+key, combinedModels,
									self._derivatives)

		equation(device=self._device,
					region=self._region,
					name=self._solutionVariable+"ContinuityEquation",
					variable_name=self._solutionVariable,
					node_model=expressions["NodeModel"],
					edge_model=expressions["EdgeModel"],
					edge_volume_model=expressions["EdgeVolumeModel"],
					time_node_model=expressions["TimeNodeModel"],
					element_model=expressions["ElementModel"],
					volume_model=expressions["ElementVolumeModel"],
					variable_update=self._variableUpdate)
					
			
		
	
