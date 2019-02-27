import itertools
import sys

from devsim import *
from util.model import *
from util.model_create import *
from util.model_factory import *

#TODO: maybe implement meta classes
	
	
class Bernoulli(EdgeModel):
	def __init__(self, device, region):
		self._name = ("VoltageDifference", "Bernoulli01", "Bernoulli10")
		self._equations = ("(Potential@n0 - Potential@n1)/V_t", "B(VoltageDifference)", "B(-VoltageDifference)")
		self._solutionVariables = ("Potential",)
		self._parameters = {}

		EnsureEdgeFromNodeModelExists(device, region, "Potential", "Potential")

		super(Bernoulli, self).generateModel(device, region)

class Current:
	pass
	
class DriftDiffusion(EdgeModel, Current):
	
	def __init__(self, device, region, carrier):
		self._name = ("{}Current".format(carrier[0]),)
		self._equations = ("{p}ElectronCharge * mu_{cs} * EdgeInverseLength / 100 * V_t * ({c}@n1*Bernoulli10 - {c}@n0*Bernoulli01)".format(p=carrier[2], c=carrier[0], cs=carrier[1]),)
		self._solutionVariables = ("Potential", carrier[0])
		self._parameters = {"ElectronCharge":"charge of an Electron in Coulombs",
									"V_t":"Thermal Voltage"}
		self._parameters["mu_{}".format(carrier[1])]="Mobility of {}".format(carrier)
		EnsureEdgeFromNodeModelExists(device, region, "Potential", "Potential")
		EnsureEdgeFromNodeModelExists(device, region, carrier[0], "Carrier")
		
		if not InEdgeModelList(device, region, "Bernoulli01") or not InEdgeModelList(device, region, "Bernoulli10"):
			Bernoulli(device, region)

		super(DriftDiffusion, self).generateModel(device, region)


#TODO: Fill out these two
class Ohmic(EdgeModel, Current):
	
	def __init__(self, device, region, carrier):
		self._name = ("{}Current".format(carrier),)
		#TODO: Use D-Field or E-Field?
		self._equations = ("ElectronCharge * ElectricField / R",)
		self._solutionVariables = ("Potential",)
		self._parameters = {"R" : "resistivity of material"}

		EnsureEdgeFromNodeModelExists(device, region, "Potential", "Potential")

		super(Ohmic, self).generateModel(device, region)
		

class SpaceChargeLimited(EdgeModel, Current):

	def __init__(self, device, region, carrier):
		self._name = ("{}Current".format(carrier[0]),)
		#TODO: L (length of material?) needs to filled in
		self._equations = ("(9/8)*Permittivity*mu_{}*((Potential@n0 - Potential@n1)/V_t)^2 / (EdgeLength^3)".format(carrier[1]),)
		self._solutionVariables = ("Potential",)
		self._parameters = {"mu_{}".format(carrier[1]): "Mobility of {}".format(carrier[0]),
					  "Permittivity" : "permittivity of material"}

		EnsureEdgeFromNodeModelExists(device, region, "Potential", "Potential")
		super(SpaceChargeLimited, self).generateModel(device, region)
		
class CurrentFactory(Factory):
	models = Factory.generateFactory(Current)
