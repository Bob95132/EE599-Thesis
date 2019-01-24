import itertools
import sys

from devsim import *
from util.model import *
from util.model_create import *

#TODO: maybe implement meta classes
class ChargeDensity:
	name = "{}ChargeDensity"
	equation = "-ElectronCharge * {}"
	parameters = {"ElectronCharge": "charge of an electron in Coulombs"}

class HoleChargeDensity(NodeModel, ChargeDensity):
	carrier = "Holes"

	def __init__(self, device, region):
		
		self._name = (self.name.format(self.carrier),)
		self._equations = (self.equation.format(self.carrier),)
		self._solutionVariables = (self.carrier,)
		self._parameters = self.parameters

		super(HoleChargeDensity, self).generateModel(device, region)

class ElectronChargeDensity(NodeModel, ChargeDensity):
	carrier = "Electrons"

	def __init__(self, device, region):
		
		self._name = (self.name.format(self.carrier),)
		self._equations = (self.equation.format(self.carrier),)
		self._solutionVariables = (self.carrier,)
		self._parameters = self.parameters

		super(ElectronChargeDensity, self).generateModel(device, region)

class DriftDiffusionBernoulli(EdgeModel):
	def __init__(self, device, region):
		self._name = ("VoltageDifference", "DriftDiffusionBernoulli",)
		self._equations = ("(Potential@n0 - Potential@n1)/V_t", "B(VoltageDifference)")
		self._solutionVariables = ("Potential",)
		#self._necessaryNodeModels = ("Potential", )
		self._parameters = {}

		super(DriftDiffusionBernoulli, self).generateModel(device, region)
	
class DriftDiffusionCurrent:
	name = "{}DriftDiffusionCurrent"
	equation = "ElectronCharge * mu_{0} * EdgeInverseLength * V_t * kahan3({1}@n1*DriftDiffusionBernoulli, {1}@n1*VoltageDifference, -{1}@n0*DriftDiffusionBernoulli)"
	parameters = {"ElectronCharge":"charge of an Electron in Coulombs",
						"V_t":"Thermal Voltage"}

class HoleDriftDiffusionCurrent(EdgeModel, DriftDiffusionCurrent):
	carrier = "Holes"
	carrier_short = "p"	

	def __init__(self, device, region):
		self._name = (self.name.format(self.carrier),)
		self._equations = (self.equation.format(self.carrier_short, self.carrier),)
		self._solutionVariables = ("Potential", self.carrier)
		#self._necessaryNodeModels = (self.carrier,)
		#self._necessaryEdgeModels = ()
		self._parameters = self.parameters
		self._parameters["mu_p"] = "mobility of Holes"
		EnsureEdgeFromNodeModelExists(device, region, "Potential", "Potential")
		EnsureEdgeFromNodeModelExists(device, region, self.carrier, "Carrier")

		if not InEdgeModelList(device, region, "DriftDiffusionBernoulli"):
			DriftDiffusionBernoulli(device, region)

		super(HoleDriftDiffusionCurrent, self).generateModel(device, region)

class ElectronDriftDiffusionCurrent(EdgeModel, DriftDiffusionCurrent):
	carrier = "Electrons"
	carrier_short = "n"	

	def __init__(self, device, region):
		self._name = (self.name.format(self.carrier),)
		self._equations = (self.equation.format(self.carrier_short, self.carrier),)
		self._solutionVariables = ("Potential", self.carrier)
		#self._necessaryNodeModels = ()
		#self._necessaryEdgeModels = ()
		self._parameters = self.parameters
		self._parameters["mu_n"] = "mobility of Electrons"
		EnsureEdgeFromNodeModelExists(device, region, "Potential", "Potential")
		EnsureEdgeFromNodeModelExists(device, region, self.carrier, "Carrier")

		if not InEdgeModelList(device, region, "DriftDiffusionBernoulli"):
			DriftDiffusionBernoulli(device, region)

		super(ElectronDriftDiffusionCurrent, self).generateModel(device, region)

class DriftDiffusion:
	models = ("Generation", "ChargeDensity", "DriftDiffusionCurrent") 
	
	def setup(self, device, region):

		for carrier in self._carriers:
			equation(device=device, region=region, name=carrier+"ContinuityEquation", 
					variable_name=carrier, time_node_model=carrier+self.models[1]	, edge_model=carrier+self.models[2], variable_update="positive", 
					node_model=carrier+self.models[0])

	def getCarriers(self):
		return self._carriers

class HoleElectronDriftDiffusion(DriftDiffusion):
	carriers = ("Electrons", "Holes")

	def __init__(self, device, region):
		self._carriers = self.carriers

		self._HoleCharges = HoleChargeDensity(device,region)
		self._HoleCurrent = HoleDriftDiffusionCurrent(device,region)
		self._ElectronCharges = ElectronChargeDensity(device, region)
		self._ElectronCurrent = ElectronDriftDiffusionCurrent(device, region)

		super(HoleElectronDriftDiffusion, self).setup(device, region)	
