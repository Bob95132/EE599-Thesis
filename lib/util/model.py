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


		for i, j in zip(self._name, self._equations):
			CreateEdgeModel(device, region, i, j)
			CreateEdgeModelDerivatives(device, region, i, j, self._solutionVariables)
		

	def getModelType(self):
		return "EdgeModel"

class ElementModel(Model):

	def generateModel(self, device, region):
		for i in self._solutionVariables:
			if not InNodeModelList(device, region, i):
				CreateSolution(device, region, i)

		for i, j in zip(self._name, self._equations):
			CreateElementModel(device, region, i, j)
			CreateElementModelDerivative(device, region, i, j, self._solutionVariables)
	
	def getModelType(self):
		return "ElementModel"

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
		for n, m in zip(self._name, self._equations):
			CreateInterfaceModel(device, region, n, m)
			CreateInterfaceModelDerivative(device, region, n, m, self._solutionVariable)
		
		interface_equation(device=device, interface=region, name=self._equationName, 
								variable_name=self._solutionVariable, name0=self._region0Equation,
								name1=self._region1Equation, interface_model=self._name, 
								type=self._modelType)

	def getModelType(self):
		return "InterfaceModel"

class ContactModel(Model):
	
	def generateModel(self, device, region):
		if self._isCircuit:
			contact_equation(device=device, contact=region, name=self._name, 
									variable_name=self._solutionVariables,
									node_model=self._equation[0], 
									edge_model=self._equation[1],
									element_model=self._equation[2],
									node_charge_model=self._equation[3],
									edge_charge_model=self._equation[4],
									element_charge_model=self._equation[5],
									node_current_model=self._equation[6],
									edge_current_model=self._equation[7],
									element_current_model=self._equation[8],
									circuit_node=GetContactBiasName(region))
		else:
			contact_equation(device=device, contact=region, name=self._name, 
									variable_name=self._solutionVariables,
									node_model=self._equation[0], 
									edge_model=self._equation[1],
									element_model=self._equation[2],
									node_charge_model=self._equation[3],
									edge_charge_model=self._equation[4],
									element_charge_model=self._equation[5],
									node_current_model=self._equation[6],
									edge_current_model=self._equation[7],
									element_current_model=self._equation[8])
			
		

	def getModelType(self):
		return "ContactModel" 
