from abc import *

from ds import *
from util/model_create import *
from util/model import *

class Model(ABC):
	@abstractmethod
	def generateModel(self, device, region):
		pass

	@abstractmethod
	def getModelType(self):
		pass

	def getParameters(self):
		return self._parameters

	

class NodeModel(Model):

	def generateModel(self, device, region):
		for i in self._solutionVariables:
			if not InNodeModelList(device, region, i):
				CreateSolution(device, region, i)

		for i,j in zip(self._name, self._equations):
			CreateNodeModel(device, region, i, j)
			CreateNodeModelDerivative(device, region, i, j, solutionVariables)

	def getModelType(self):
		return "NodeModel"

class EdgeModel(Model):
	
	def generateModel(self, device, region):
		for i in self._solutionVariables:
			if not InEdgeModelList(device, region, i):
				CreateSolution(device, region, i)

		for i, j in zip(self._name, self._equation):
			CreateEdgeModel(device, region, i, j)
			CreateEdgeModelDerivates(device, region, i, j, solutionVariables)
		

	def getModelType(self):
		return "EdgeModel"

class InterfaceModel(Model):
	
	def generateModel(self, device, region):
		model = CreateContinuousInterfaceModel(device, region, self._solutionVariables)
		interface_equation(device=device, interface=region, name=self._name, 
								variable_name=self._solutionVariables, interface_model=model, type="continous")

	def getModelType(self):
		return "InterfaceModel"

class ContactModel(Model):
	
	def generateModel(self, device, region):
		if self._isCircuit:
			contact_equation(device=device, contact=region, name=self._name, 
									variable_name=self._solutionVariables,
									node_model=self._equation[0], 
									edge_model=self._equation[1],
									node_charge_model=self._equation[2],
									edge_charge_model=self._equation[3],
									node_current_model=self._equation[4],
									edge_current_model=self._equation[5],
									circuit_node=GetContactBiasName(contact))
		else:
			contact_equation(device=device, contact=region, name=self._name, 
									variable_name=self._solutionVariables,
									node_model=self._equation[0], 
									edge_model=self._equation[1],
									node_charge_model=self._equation[2],
									edge_charge_model=self._equation[3],
									node_current_model=self._equation[4],
									edge_current_model=self._equation[5])
			
		

	def getModelType(self):
		return "ContactModel" 
