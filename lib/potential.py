from devsim import *
from util.model import *
from util.model_create import *
from util.error import *

class ElectricField(EdgeModel):
	def __init__(self, device, region):

		self._name = ("ElectricField", "PotentialEdgeFlux")
		self._equations = ("(Potential@n0-Potential@n1)*EdgeInverseLength + 1e-50", 
								"Permittivity*ElectricField")
		self._solutionVariables = ("Potential",)
		self._parameters = {"Permittivity":"permittivity of material"}

		EnsureEdgeFromNodeModelExists(device, region, "Potential", "Potential")
		
		super(ElectricField, self).generateModel(device, region)

class ElectricFieldMag(ElementModel):
	def __init__(self, device, region):
		self._name = ("ElectricFieldMag",)
		self._equations = ("pow(ElectricField_x^2 + ElectricField_y^2 + 1e-100, .5)",)
		self._solutionVariables = ("Potential",)
		self._parameters = {}

		EnsureElementEdge2DFromEdgeModelExists(device, region, "ElectricField", "Potential")

		super(ElectricFieldMag, self).generateModel(device, region)

class SemiconductorIntrinsicCarrierPotential(NodeModel):

	def __init__(self, device, region):

		if not InNodeModelList(device, region, "IntrinsicCharge"):
			raise MissingModelError("IntrinsicCharge", "Carrier")

		self._name = ("PotentialIntrinsicCharge",)
		self._equations = ("-ElectronCharge * IntrinsicCharge",)
		self._solutionVariables = ("Potential",)
		self._parameters = {"ElectronCharge" : "Charge of an Electron"}

		super(SemiconductorIntrinsicCarrierPotential, self).generateModel(device, region)

class SemiconductorExcessCarrierPotential(NodeModel):
	def __init__(self, device, region):
		if not InNodeModelList(device, region, "NetDoping"):
			raise MissingModelError("NetDoping", "Carrier")
		
		self._name = ("PotentialNodeCharge",)
		self._equations = ("-ElectronCharge * kahan3(Holes, -Electrons, NetDoping)",)
		self._solutionVariables = ("Electrons", "Holes")
		self._parameters = {"ElectronCharge":"charge of an electron in coulombs"}

		super(SemiconductorExcessCarrierPotential, self).generateModel(device,region)
		#TODO: check what variable update means

class ConductorIntrinsicCarrierPotential(NodeModel):
	def __init__(self, device, region):
		self._name = ("PotentialIntrinsicCharge",)
		self._equations = ("ElectronCharge * IntrinsicElectrons")
		self._solutionVariables = ()
		self._parameters = {"ElectronCharge": "charge of an electron in coulombs"}

		super(ConductorCarrierPotential, self).generateModel(device, region)

class ConductorExcessCarrierPotential(NodeModel):
	def __init__(self, device, region):
		self._name = ("PotentialNodeCharge",)
		self._equations = ("ElectronCharge * Electrons")
		self._solutionVariables = ("Electrons",)
		self._parameters = {"ElectronCharge": "charge of an electron in coulombs"}

		super(ConductorCarrierPotential, self).generateModel(device, region)
