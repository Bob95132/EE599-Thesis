from devsim import *
from util.model import *
from util.model_create import *
from util.error import *

class LangevinRecombination(NodeModel):
	def __init__(self, device, region):
		self._name = ("LR", "ElectronsGeneration", "HolesGeneration")
		self._equations = ("B_r * (Electrons*Holes - IntrinsicCarrierConcentration^2)",
								"-ElectronCharge * LR",
								"+ElectronCharge * LR")
		self._solutionVariables = ("Electrons", "Holes")
		self._parameters = {"B_r":"Bimolecular recombination rate"}

		if not InNodeModelList(device, region, "IntrinsicCarrierConcentration"):
			raise MissingModelException("IntrinsicCarrierConcentration", "Carrier")

		super(LangevinRecombination, self).generateModel(device,region)

class ShockleyReadHallRecombination(NodeModel):
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

		super(ShockleyReadHallRecombination, self).generateModel(device,region)


