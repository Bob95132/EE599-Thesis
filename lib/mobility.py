from ds import *
from util.model_create import *
from util.model import *

		 
#Gaussian Disorder Model
class GaussianDisorderModel(NodeModel):
	def __init__(self, device, region):
		self._name = ("GaussianDisorderModel",)
		self._equation =  ("mu_inf * exp(-pow(((2*sigma)/(3*k*T)),2) + C*(pow((sigma/(k*T)),2) - 2.25) - pow(ElectricField, .5))",)
		self._solutionVariables = ("Potential",)
		self._parameters = {"mu_inf":"mu steady-state", 
						"sigma":"molecular constant",
						"k":"Boltzmann",
						"C":"molecular constant",
						"T":"Temperature"}

		super(GaussianDisorderModel, self).generateModel(device,region)
		
class CorrelatedDisorderModel(NodeModel):
	def __init__(self, device, region):
		self._name = ("CorrelatedDisorderModel",)
		self._equation =  ("mu_inf * exp(-pow(((3*sigma)/(5*k*T)),2) + .78*(pow((sigma/(k*T)),1.5) - 2) - pow(ElectronCharge*a*ElectricField/sigma, .5))",)
		self._solutionVariables = ("Potential",)
		self._parameters = {"mu_inf":"mu steady-state", 
						"sigma":"molecular constant",
						"k":"Boltzmann",
						"a":"lattice constant",
						"ElectronCharge":"charge of an electron",
						"T":"Temperature"}

		super(CorrelatedDisorderModel, self).generateModel(device,region)

class FieldDependentModel(NodeModel):
	def __init__(self, device, region):
		self._name = ("FieldDependentModel",)
		self._equation =  ("mu_0 * exp(-delta/(k*T) + B(1/(k*T) - 1/(k*T_0))*pow(ElectricField, .5))",)
		self._solutionVariables = ("Potential",)
		self._parameters = {"mu_0":"permeability of vacuum", 
						"delta":"activation energy",
						"k":"Boltzmann",
						"B":"BlomPaper-Eq.1.3, 2.8",
						"T_0":"",
						"T":"Temperature"}

		super(FieldDependentModel, self).generateModel(device,region)
	 
	
