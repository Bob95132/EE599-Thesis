from devsim import *
from util.model import *
from util.model_create import *
from util.model_factory import *

class NetDoping(NodeModel):
	#TODO: maybe expand this for varying Donor Acceptor Concentration
	def __init__(self, device, region):
		self._name = (self.getName(),)
		self._equations = ("Nd - Na",)
		self._solutionVariables = ()
		self._parameters = {"Nd" : "Donor Concentration",
								  "Na" : "Accepotr Concentration"}

		super(NetDoping, self).generateModel(device,region)

class DOS(NodeModel):

	def __init__(self, device, region, carrier):
		self._name = ("N_{}".format(carrier),)
		#ElectronCharge for conversion from eV -> J and 1/10000 converts 1/m^2 -> 1/cm^2
		self._equations = ("2 * (2 * pi * M_{} * k * T / (1.602e-19 *  h^2))^1.5)".format(carrier), )
		self._solutionVariables = ()
		self._parameters = {"pi" : "global constant",
								"M_{}".format(carrier) : "mass of {}".format(carrier),
								"k": "Boltzmann Constant",
								"T": "Temperature",
								"h": "Planck constant"  }

class IntrinsicCarrier(NodeModel):
	def __init__(self, device, region):
		self._name = ("IntrinsicCarrierConcentration",)
		self._equations = ("(N_Electrons * N_Holes) ^ (0.5)  * exp ( - (E_Electrons - E_Holes) / (2*V_t))",)
		self._solutionVariables = ()
		self._parameters = { "N_Electrons":"Carriers in conduction band in material",
									"N_Holes": "Carriers in valence band in material",
									"V_t" : "Thermal Voltage",
									"E_Electrons" : "Conduction Band Energy",
									"E_Holes" : "Valence Band Energy"}
		super(IntrinsicCarrier, self).generateModel(device, region)

class DopedHolesElectrons(NodeModel):
	def __init__(self, device, region):
		if not InNodeModelList(device, region, "NetDoping"):
			NetDoping(device,region)
	
		if not InNodeModelList(device, region, "IntrinsicCarrierConcentration"):
			IntrinsicCarrier(device,region)

		self._name = ("DopedElectrons", "DopedHoles")
		self._equations = ("(1e-10 + 0.5*abs(NetDoping+(NetDoping^2 + 4 * \
									IntrinsicCarrierConcentration^2)^(0.5)))",
								"(1e-10 + 0.5*abs(-NetDoping+(NetDoping^2 + 4 * \
									IntrinsicCarrierConcentration^2)^(0.5)))")

		self._solutionVariables = ()
		self._parameters = {}

		super(EquilibriumHolesElectrons, self).generateModel(device,region)


class IntrinsicHoleElectron(NodeModel):
	def __init__(self, device, region):
		if not InNodeModelList(device, region, "NetDoping"):
			NetDoping(device, region)
	
		if not InNodeModelList(device, region, "IntrinsicCarrierConcentration"):
			IntrinsicCarrier(device, region)

		self._name = (	"IntrinsicElectrons", 
							"IntrinsicHoles")
		
		self._equations = \
			("IntrinsicCarrierConcentration * exp ( Potential / V_t)", 
			 "IntrinsicCarrierConcentration * exp (-Potential / V_t)")

		self._solutionVariables = ("Potential",)

		super(IntrinsicHoleElectron, self).generateModel(device, region)

class EquilibriumElectronsHoles:
	def __init__(self, device, region):
		for carrier in ("Electrons", "Holes"):
			CreateSolution(device=device, region=region, name="Equilibrium"+carrier)
			if not InNodeModelList(device, region, "Intrinsic"+carrier):
				raise MissingModelError("Intrinsic"+carrier, "Carrier")
			set_node_values(device=device, region=region, name="Equilibrium"+carrier, init_from="Intrinsic"+carrier)	

class Density:
	pass

class Charge(NodeModel, Density):
	
	def __init__(self, device, region, carrier, polarity):
		self._name = ("{}ChargeDensity".format(carrier),)
		self._equations = ("{p}ElectronCharge * {c}".format(p=polarity, c=carrier),)
		self._solutionVariables = (carrier,)
		self._parameters = {"ElectronCharge": "charge of an electron in Coulombs"}

		super(Charge, self).generateModel(device, region)
	

#class Photon(NodeModel, Density):
#	def __init__(self, device, region, carrier):
#		self._name = ("PhotonDensity",)
#		self._equations = ("-Photons / c",)
#		self._solutionVariables = ("Photons",)
#		self._parameters = {"c" : "speed of light"}
#
#		super(Photon, self).generateModel(device, region)

class DensityFactory(Factory):
	models = Factory.generateFactory(Density)

	@classmethod
	def ElectronChargeDensity(cls, device, region):
		Charge(device, region, "Electrons", "-")
	
	@classmethod
	def HoleChargeDensity(cls, device, region):
		Charge(device, region, "Holes", "+")

	@classmethod
	def ElectronHoleChargeDensity(cls, device, region):
		cls.ElectronChargeDensity(device, region)
		cls.HoleChargeDensity(device, region)
