from devsim import *
from util.model import *
from util.model_create import *
from util.error import *
from util.model_factory import *

class Recombination:
	pass

class Langevin(NodeModel, Recombination):
	def __init__(self, device, region):
		self._name = ("LR", "ElectronsGeneration", "HolesGeneration")
		self._equations = ("B_r * (Electrons*Holes - IntrinsicCarrierConcentration^2)",
								"-ElectronCharge * LR",
								"+ElectronCharge * LR")
		self._solutionVariables = ("Electrons", "Holes")
		self._parameters = {"B_r":"Bimolecular recombination rate"}

		if not InNodeModelList(device, region, "IntrinsicCarrierConcentration"):
			raise MissingModelException("IntrinsicCarrierConcentration", "Carrier")

		super(Langevin, self).generateModel(device,region)

class ShockleyReadHall(NodeModel, Recombination):
	def __init__(self, device, region):
		self._name = ("USRH", "ElectronsGeneration", "HolesGeneration")
		sel.f_equations = ("(Electrons*Holes - IntrinsicCarrierConcentration^2)/(tau_p*(Electrons + InstrinicElectrons) + tau_n*(Holes * IntrinsicHoles))",
								"-ElectronCharge * USRH",
								"+ElectronCharge * USRH")
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
	def __init__(self, device, region):
		self._name = ("Auger", "ElectronsGeneration", "HolesGeneration")
		self._equations = ("(K_ec*Electrons + K_hc*Holes)*(Electrons*Holes - IntrinsicCarrierConcentration^2)",
								 "-ElectronCharge * Auger",
								 "+ElectronCharge * Auger")
		self._solutionVariables = ("Electrons", "Holes")
		self._parameters = {"K_ec": "electron rate constant",
								  "K_hc": "hoole rate constant"}

		if not InNodeModelList(device, region, "IntrinsicCarrierConcentration"):
			raise MissingModelException("IntrinsicCarrierConcentration", "Carrier")
	
		super(Auger, self).generateModel(device, region)
class RecombinationFactory(Factory):
	models = Factory.generateFactory(Recombination)
