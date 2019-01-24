from devsim import *
from util.model import *
from util.model_create import *
from util.error import *

class ElectricField(EdgeModel):
	def __init__(self, device, region):

		self._name = ("ElectricField", "PotentialEdgeFlux")
		self._equations = ("(Potential@n0-Potential@n1)*EdgeInverseLength", 
								"Permittivity*ElectricField")
		self._solutionVariables = ("Potential",)
		self._necessaryNodeModels = ()
		self._parameters = {"Permittivity":"permittivity of material"}

		EnsureEdgeFromNodeModelExists(device, region, "Potential", "Potential")
		
		super(ElectricField, self).generateModel(device, region)

class ElectricFieldMag(ElementEdge2DModel):
	def __init__(self, device, region):
		self._name = ("ElectricFieldMag",)
		self._equations = ("pow(ElectricField_x^2 + ElectricField_y^2 + 1e-100, .5)",)
		self._solutionVariables = ("Potential",)
		self._parameters = {}

		EnsureElementEdge2DFromEdgeModelExists(device, region, "ElectricField", "Potential")

		super(ElectricFieldMag, self).generateModel(device, region)

class IntrinsicPotential(NodeModel):

	def __init__(self, device, region):

		if not InNodeModelList(device, region, "IntrinsicCharge"):
			raise MissingModelError("IntrinsicCharge", "Carrier")

		self._name = ("PotentialIntrinsicCharge",)
		self._equations = ("-ElectronCharge * IntrinsicCharge",)
		self._solutionVariables = ("Potential",)
		self._parameters = {"ElectronCharge" : "Charge of an Electron"}

		super(IntrinsicPotential, self).generateModel(device, region)

		if not InEdgeModelList(device, region, "ElectricField"):
			ElectricField(device,region)

		equation(device=device, 
					region=region, 
					name="PotentialEquation", 
					variable_name="Potential", 						
					node_model="PotentialIntrinsicCharge", 
					edge_model="PotentialEdgeFlux",
					time_node_model="", 
					variable_update="log_damp")	

class DynamicPotential(NodeModel):
	def __init__(self, device, region):
		if not InNodeModelList(device, region, "NetDoping"):
			raise MissingModelError("NetDoping", "Carrier")
		
		self._name = ("PotentialNodeCharge",)
		self._equations = ("-ElectronCharge * kahan3(Holes, -Electrons, NetDoping)",)
		self._solutionVariables = ("Electrons", "Holes")
		self._parameters = {"ElectronCharge":"charge of an electron in coulombs"}

		super(DynamicPotential, self).generateModel(device,region)
		#TODO: check what variable update means

		if not InEdgeModelList(device, region, "ElectricField"):
			ElectricField(device, region)

		if not InElementEdgeModelList(device, region, "ElectricFieldMag"):
			ElectricFieldMag(device, region)

		equation(device=device, 
					region=region, 
					name="PotentialEquation", 
					variable_name="Potential", 						
					node_model="PotentialNodeCharge", 
					edge_model="PotentialEdgeFlux",
					time_node_model="", 
					variable_update="log_damp")

