from ds import *
from util.model import *

class LangevinRecombination(Model):
	def __init__(self, device, region):
		self._name = ("LR", "ElectronGeneration", "HoleGeneration")
		self._equation = ("B_r * (Electrons*Holes - pow(IntrinsicCarrierConcentraction, 2))",
								"-ElectronCharge * LR",
								"+ElectronCharge * LR")
		self._solutionVariables = ("Electrons", "Holes")
		self._parameters = {"B_r":"Bimolecular recombination rate"}

		super(LangevinRecombination, self).generateModel(device,region)

class ShockleyReadHallRecombination(Model):
	def __init__(self, device, region):
		self._name = ("USRH", "ElectronGeneration", "HoleGeneration")
		sel.f_equation = ("(Electrons*Holes - IntrinsicCarrierConcentration^2)/(tau_p*(Electrons + InstrinicElectrons) + tau_n*(Holes * IntrinsicHoles))",
								"-ElectronCharge * USRH",
								"+ElectronCharge * USRH")
		self._solutionVariables = ("Electrons", "Holes")
		self._parameters = { "tau_p":"hole lifetime",
				   "tau_n":"electron lifetime"}

		super(ShockleyReadHallRecombination, self).generateModel(device,region)


