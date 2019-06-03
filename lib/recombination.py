import re
import cmath

from devsim import *
from util.model import *
from util.model_create import *
from util.error import *
from util.model_factory import *

class Recombination:
	@classmethod
	def isCarrierDependent(cls):
		return cls._isCarrierDependent

class CarrierGenerator:
	pass

class Langevin(NodeModel, Recombination):
	isCarrierDependent = False

	def __init__(self, device, region):
		self._name = ("BimolecularRate",
							self.getName(),)
		self._equations = ("ElectronCharge * (mu_n + mu_p) / Permittivity",
								"B_r * (Electrons*Holes - IntrinsicCarrierConcentration^2)",) 
		self._solutionVariables = ("Electrons", "Holes")
		self._parameters = {"B_r":"Bimolecular recombination rate"}

		if not InNodeModelList(device, region, "IntrinsicCarrierConcentration"):
			raise MissingModelException("IntrinsicCarrierConcentration", "Carrier")

		super(Langevin, self).generateModel(device,region)

class StimulatedEmission(NodeModel, Recombination):
	isCarrierDependent = True
	
	def __init__(self, device, region, wave):
		self._name = ("Gamma",
						  "EnergyDiff_{wave}".format(wave=wave), 
						  "ElectronFermFunction_{wave}".format(wave=wave),
						   "HoleFermFunction_{wave}".format(wave=wave),
						  "PhotonLocalGain_{wave}".format(wave=wave),
						  "PhotonModalGain_{wave}".format(wave=wave),
							self.getName() + "_{wave}".format(wave=wave), )
		self._equations = ("1 / (pow(N_Electrons / N_Holes, 2/3) + 1)",
								 "abs(h * {wave} - (E_Electrons - E_Holes))".format(wave=wave),
								 "(1/(1+exp((-V_t * log(abs(Electrons / N_Electrons)) + Gamma * EnergyDiff_{wave}) / V_t)))".format(wave=wave),
								 "(1/(1+exp((+V_t*log(abs(Holes/N_Holes)) - (1-Gamma) * EnergyDiff_{wave})/ V_t)))".format(wave=wave),	
								 "gain0_{wave} * pow( EnergyDiff_{wave}  / V_t, .5) * (ElectronFermFunction_{wave} - HoleFermFunction_{wave})".format(wave=wave),
								 "1e-50 + (vec_sum(OpticalDensity_{wave} * PhotonLocalGain_{wave})) / (vec_sum(OpticalDensity_{wave}) + 1e-50)".format(wave=wave),
								 "((c * 100  * PhotonModalGain_{wave} / n_eff_{wave})) * Photons_{wave}".format(wave=wave),)
		self._solutionVariables = ("Electrons",
											"Holes",
											"Photons_{wave}".format(wave=wave))

		if not InNodeModelList(device, region, "OpticalDensity_{wave}".format(wave=wave)):
			CreateSolution(device, region, "OpticalDensity_{wave}".format(wave=wave))
			set_node_value(device=device, region=region, name="OpticalDensity_{wave}".format(wave=wave), value=0)

		if not InNodeModelList(device, region, "n_eff_{wave}".format(wave=wave)):
			CreateSolution(device, region, "n_eff_{wave}".format(wave=wave))
			set_node_value(device=device, region=region, name="n_eff_{wave}".format(wave=wave), value=1e-50)
		self._parameters = {"Permittivity" : "permittivity of the material",
									"h": "Planck's Constant",
									"{wave}" : "frequency of oscillation"}

		super(StimulatedEmission, self).generateModel(device, region)


class PhotonGeneration(NodeModel, CarrierGenerator):
	def __init__(self, device, region, wave):
		self._name = (self.getName() + "_{wave}".format(wave=wave),)
		equation = []
		#Add in Einstein contribution for Langevin
		models = ("Langevin", "PhotonAbsorption_{wave}".format(wave=wave))
		for model in models:
			if InNodeModelList(device, region, model):
				equation.append(model)

		equation = (" + ".join(equation) if len(equation) > 1 else equation[0])
		self._equations = (equation,)
		self._solutionVariables = ("Electrons", "Holes", "OpticalDensity_{wave}".format(wave=wave))
		self._parameters = {}

		super(PhotonGeneration, self).generateModel(device, region)

class ShockleyReadHall(NodeModel, Recombination):
	#TODO: Change this in the future, should be dependent
	isCarrierDependent = False

	def __init__(self, device, region):
		self._name = ("tau_n", "tau_p", self.getName(),)
		self._equations = ("pow(ElectronCharge * mu_n * N_t / Permittivity, -1)",
								 "pow(ElectronCharge * mu_p * N_t / Permittivity, -1)", 
								 "(Electrons*Holes - IntrinsicCarrierConcentration^2)/(tau_p*(Electrons + EquilibriumElectrons) + tau_n*(Holes + EquilibriumHoles))",)
		self._solutionVariables = ("Electrons", "Holes")
		self._parameters = { "tau_p":"hole lifetime",
				   "tau_n":"electron lifetime"}
		if not InNodeModelList(device, region, "IntrinsicCarrierConcentration"):
			raise MissingModelException("IntrinsicCarrierConcentration", "Carrier")

		if not InNodeModelList(device, region, "IntrinsicHoles") or \
		   not InNodeModelList(device, region, "IntrinsicElectrons"):
			raise MissingModelException("IntrinsicHoleCarrierCharge", "Carrier")

		super(ShockleyReadHall, self).generateModel(device,region)

class Auger(NodeModel, Recombination):
	isCarrierDependent = False

	def __init__(self, device, region):
		self._name = ("K_ec",
						  "K_hc",
							self.getName(), )
		self._equations = ("1e-33",
								 "1e-32",
								"(K_ec*Electrons + K_hc*Holes)*(Electrons*Holes - IntrinsicCarrierConcentration^2)",)
		self._solutionVariables = ("Electrons", "Holes")
		self._parameters = {"K_ec": "electron rate constant",
								  "K_hc": "hoole rate constant"}

		if not InNodeModelList(device, region, "IntrinsicCarrierConcentration"):
			raise MissingModelException("IntrinsicCarrierConcentration", "Carrier")
	
		super(Auger, self).generateModel(device, region)

class ElectronHoleGeneration(NodeModel, CarrierGenerator):
	def __init__(self, device, region, solutionVariables):
		self._name = ("ElectronsGeneration", "HolesGeneration")
		self._equations = ("-ElectronCharge * NetRecombination", "+ElectronCharge * NetRecombination")
		self._solutionVariables = ("Electrons", "Holes") + solutionVariables
		self._parameters = {"ElectronCharge": "Charge of an electron"}
	
		super(ElectronHoleGeneration, self).generateModel(device, region)

class RecombinationFactory(Factory):
	models = Factory.generateFactory(Recombination)
	generators = Factory.generateFactory(CarrierGenerator)

	@classmethod
	def checkCarrier(cls, device, region, model, carrier, wave):
		if carrier in model and carrier+"Generation" not in model:
			cls.generators[carrier+"Generation"](device, region, wave)

	@classmethod
	def generateModel(cls, device, region, model, carrier = None):
		super().generateModel(device, region, model, carrier)
		#NOTE: All recombination classes must only use one equation!!
		cls.checkCarrier(device, region, model, "Photon", carrier)

		addedModels = set()
		for models in cls.getModels():
			if cls.models[models].isCarrierDependent:
				for added in get_node_model_list(device=device,region=region):
					match = re.search(models + "_([0-9e]+)", added) 
					if match is not None:
						addedModels.add(match.group(0))
			elif InNodeModelList(device, region, models):
				addedModels.add(models)

		addedModels = list(addedModels)

		equation = " + ".join(addedModels) if len(addedModels) > 1 else addedModels[0]

		CreateNodeModel(device, region, "NetRecombination", equation)
		CreateNodeModelDerivative(device, region, "NetRecombination", equation, ("Electrons", "Holes", "OpticalDensity_5e14"))
		ElectronHoleGeneration(device, region, ())

			
		
		
