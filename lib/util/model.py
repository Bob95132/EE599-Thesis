from abc import *
from py_expression_eval import Parser

from devsim import *
from util.model_create import *

class Model(ABC):
	@abstractmethod
	def generateModel(self, device, region):
		pass

	@abstractmethod
	def getModelType(self):
		pass

	def getModelName(self):
		return self.__class__.__name__

	def getParameters(self):
		return self._parameters

	

class NodeModel(Model):

	def generateModel(self, device, region):
		for i in self._solutionVariables:
			if not InNodeModelList(device, region, i):
				CreateSolution(device, region, i)

		for i,j in zip(self._name, self._equations):
			CreateNodeModel(device, region, i, j)
			CreateNodeModelDerivative(device, region, i, j, self._solutionVariables)

	def getModelType(self):
		return "NodeModel"

class EdgeModel(Model):
	
	def generateModel(self, device, region):
		for i in self._solutionVariables:
			if not InNodeModelList(device, region, i):
				CreateSolution(device, region, i)

#		for i in self._necessaryNodeModels:
#			EnsureEdgeFromNodeModelExists(device, region, i)

		for i, j in zip(self._name, self._equations):
			CreateEdgeModel(device, region, i, j)
			CreateEdgeModelDerivatives(device, region, i, j, self._solutionVariables)
		

	def getModelType(self):
		return "EdgeModel"

class ElementEdge2DModel(Model):

	def generateModel(self, device, region):
		for i in self._solutionVariables:
			if not InNodeModelList(device, region, i):
				CreateSolution(device, region, i)

		for i in self._necessaryNodeModels:
			EnsureElementEdgeFromNodeModelExists(device, region, i)

		for i in self._necessaryEdgeModels:
			EnsureElementEdgeFromEdgeModelExists(device, region, i)

		for i, j in zip(self._name, self._equations):
			CreateElementModel2d(device, region, i, j)
			CreateElementModelDerivative2d(device, region, i, j, self._solutionVariables)
	
	def getModelType(self):
		return "ElementEdge2DModel"

class ParameterModel(Model):
	parser = Parser()

	def generateModel(self, device, region):
		parsed = self.parser.parse(self._equation)
		params = {}
		material = get_material(device=device, region=region)
		for var in parsed.variables():
			try:
				params[var] = float(get_db_entry(material=material, parameter=var)[0])
			except:
				params[var] = float(get_db_entry(material="global", parameter=var)[0])

		set_parameter(device=device, region=region, name=self._name, value=eval(self._equation, params))

	def getModelType(self):
		return "ParameterModel"

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
