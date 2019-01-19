import itertools
import sys

from ds import *
from util/model import *
from util/model_create import *

#TODO: maybe implement meta classes
class ChargeDensity:
	name = "{}ChargeDensity"
	equation = "-ElectronCharge * {}"
	parameters = {"ElectronCharge": "charge of an electron in Coulombs"}

class HoleChargeDensity(NodeModel, ChargeDensity):
	carrier = "Holes"

	def __init__(self, device, region):
		
		self._name = (self.name.format(carrier),)
		self._equation = (self.equation.format(carrier),)
		self._solutionVariables = (carrier,)
		self._parameters = parameters

		super(HoleChargeDensity, self).generateModel(device, region)

class ElectronChargeDensity(NodeModel, ChargeDensity):
	carrier = "Electrons"

	def __init__(self, device, region):
		
		self._name = (self.name.format(carrier),)
		self._equation = (self.equation.format(carrier),)
		self._solutionVariables = (carrier,)
		self._parameters = parameters

		super(HoleChargeDensity, self).generateModel(device, region)

class DriftDiffusionBernoulli(EdgeModel):
	def __init__(self, device, region):
		self._name = ("DriftDiffusionBernoulli",)
		self._equation = ("B(VoltageDifference)",)
		self._solutionVariables = ("Potential",)
		self._parameters = {}

		EnsureEdgeFromNodeModelExists(device, region, "Potential")
		if not InEdgeModelList(device, region, "VoltageDifference"):
			VoltageDifference()
		super(DriftDiffusionBernoulli, self).generateModel(device, region)
	
class DriftDiffusionCurrent:
	name = "{}DriftDiffusionCurrent"
	equation = "ElectronCharge * mu_{0} * EdgeInverseLength * V_t * kahan3({1}@n1*DriftDiffusionBernoulli, {1}@n1*VoltageDifference, -{1}@n0*DriftDiffusionBernoulli)",)
	parameters = {"ElectronCharge":"charge of an Electron in Coulombs",
					  "mu_%s":"mobility of %s",
						"V_t":"Thermal Voltage"}

class HoleDriftDiffusionCurrent(EdgeModel, DriftDiffusionCurrent):
	carrier = "Holes"
	carrier_short = "p"	

	def __init__(self, device, region):
		self._name = (self.name.form(carrier),)
		self._equation = (self.equation.format(carrier_short, carrier),)
		self._solutionVariables = ("Potential", carrier)
		self._paramters = self.parameters
		self._parameters[1] = self._paramters[1].format(carrier_short, carrier)
		EnsureEdgeFromNodeModelExists(device, region, "Potential")
		EnsureEdgeFromNodeModelExists(device, region, carrier)

		if not inEdgeModelList(device, region, "DriftDiffusionBernoulli"):
			DriftDiffusionBernoulli(device, region)

		super(HoleDriftDiffusionCurrent, self).generateModel(device, region)

class ElectronDriftDiffusionCurrent(EdgeModel, DriftDiffusionCurrent):
	carrier = "Electrons"
	carrier_short = "n"	

	def __init__(self, device, region):
		self._name = (self.name.format(carrier),)
		self._equation = (self.equation.format(carrier_short, carrier),)
		self._solutionVariables = ("Potential", carrier)
		self._paramters = self.parameters
		self._parameters[1] = self._paramters[1].format(carrier_short, carrier)
		EnsureEdgeFromNodeModelExists(device, region, "Potential")
		EnsureEdgeFromNodeModelExists(device, region, carrier)

		if not inEdgeModelList(device, region, "DriftDiffusionBernoulli"):
			DriftDiffusionBernoulli(device, region)

		super(HoleDriftDiffusionCurrent, self).generateModel(device, region)

class DriftDiffusion:
	models = ("Generation", "ChargeDensity", "DriftDiffusionCurrent") 
	
	def setup(self, device, region):
		fail = False

		necessaryModels = [x+y for x in self._carriers for y in models]
		for model in necessaryModels:
			if not inEdgeModelList(device, region, model) 
				and not inNodeModelList(device, region, model):
					fail = True
					print("DriftDiffusionModel: %s required, but not in Model List" % model)

		if fail:
			print("A model necessary for DriftDiffusion was not found. Exiting")
			sys.exit()

		for carrier in carriers:
			equation(device=device, region=region, name=carrier+"ContinuityEquation", 
					variable_name=carrier, time_node_model=carrier+models[1]	, 
					edge_model=carrier+models[2], variable_update="positive", 
					node_model=carrier+models[0])

	def getCarriers(self):
		return self._carriers

class HoleElectronDriftDiffusion(DriftDiffusion):
	carriers = ("Electrons", "Holes")

	def __init__(self, device, region):
		self._carriers = carriers

		self._HoleCharges = HoleChargeDensity(device,region)
		self._HoleCurrent = HoleDriftDiffusionCurrent(device,region)
		self._ElectronCharges = ElectronChargeDensity(device, region)
		self._ElectronCurrent = ElectronDriftDiffusion(device, region)

		super(HoleElectronDriftDiffusionModel, self).setup(device, region)	
