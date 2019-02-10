from devsim import *
from util.model_create import *
from util.model import *
from util.model_factory import *

		 
#Gaussian Disorder Model
#TODO: Do something about permutation of models * carriers (METACLASSES?)
class Mobility:
	pass

class GaussianDisorder(EdgeModel, Mobility):
	def __init__(self, device, region, carrierShort):
		self._name = ("mu_{}".format(carrierShort),)
		self._equations =  ("mu_inf_{} * exp(-pow(((2*sigma)/(3*k*T)),2) + C*(pow((sigma/(k*T)),2) - 2.25) * pow(ElectricField, .5))".format(carrierShort),)
		self._solutionVariables = ("Potential",)
		self._parameters = {"mu_inf":"mu steady-state", 
						"sigma":"molecular constant",
						"k":"Boltzmann",
						"C":"molecular constant",
						"T":"Temperature"}

		if not InEdgeModelList(device, region, "ElectricField"):
			raise MissingModelError("ElectricField", "Potential")

		super(GaussianDisorder, self).generateModel(device,region)
		
class CorrelatedDisorder(EdgeModel, Mobility):
	def __init__(self, device, region, carrierShort):
		self._name = ("mu_{}".format(carrierShort),)
		self._equations =  ("mu_inf_{} * exp(-pow((3*sigma)/(5*k*T),2) + 7.8e-1*(pow(sigma/(k*T),1.5) - 2) * pow(a*abs(ElectricField)/sigma, .9))".format(carrierShort),)
		self._solutionVariables = ("Potential",)
		self._parameters = {"mu_inf":"mu steady-state", 
						"sigma":"molecular constant",
						"k":"Boltzmann",
						"a":"lattice constant",
						"ElectronCharge":"charge of an electron",
						"T":"Temperature"}

		if not InEdgeModelList(device, region, "ElectricField"):
			raise MissingModelError("ElectricField", "Potential")

		super(CorrelatedDisorder, self).generateModel(device,region)

class FieldDependent(EdgeModel, Mobility):
	def __init__(self, device, region, carrierShort):
		self._name = ("mu_{}".format(carrierShort),)
		self._equations =  ("mu_0 * exp(-delta/(k*T) + B(1/(k*T) - 1/(k*T_0))*pow(ElectricField, .5))",)
		self._solutionVariables = ("Potential",)
		self._parameters = {"mu_0":"permeability of vacuum", 
						"delta":"activation energy",
						"k":"Boltzmann",
						"B":"BlomPaper-Eq.1.3, 2.8",
						"T_0":"",
						"T":"Temperature"}

		if not InEdgeModelList(device, region, "ElectricField"):
			raise MissingModelError("ElectricField", "Potential")

		super(FieldDependent, self).generateModel(device,region)
	
class MobilityFactory(Factory):
	models = Factory.generateFactory(Mobility)
