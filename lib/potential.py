from ds import *
from util/model import *
from util/model_create import *

class IntrinsicPotential(EdgeModel):
	def __init__(self, device, region):
		self._name = ("ElectricField", "PotentialEdgeFlux")
		self._equation = ("(Potential@n0-Potential@n1)*EdgeInverseLength", "Permittivity*ElectricField")
		self._solutionVariables = ("Potential",)
		self._parameters = {"Permittivity":"permittivity of material"}
	
		if not InNodeModelList(device, region, "PotentialIntrinsicCharge"):
			IntrinsicCharge(device, region) 
		super(IntrinsicPotential, self).generateModel(device, region)

class DynamicPotential(NodeModel):
	def __init__(self, device, region):
		self._name = ("PotentialNodeCharge",)
		self._equation = ("-ElectronCharge * kahan3(Holes, -Electrons, NetDoping)",)
		self._solutionVariables = ("Electrons", "Holes")
		self._parameters = {"ElectronCharge":"charge of an electron in coulombs"}

		super(DynamicPotential, self).generateModel(device,region)
		#TODO: check what variable update means
		equation(device=device, region=region, name="PotentialEquation", variable_name="Potential", 						node_model="PotentialNodeCharge", edge_model="PotentialEdgeFlux",
					 time_node_model="", variable_update="log_damp")

