from devsim import *
from util.model import *
from util.model_create import *
from util.model_factory import *

class Doping(NodeModel):
	#TODO: maybe expand this for varying Donor Acceptor Concentration
	def __init__(self, device, region):
		self._name = ("NetDoping",)
		self._equations = ("Nd - Na",)
		self._solutionVariables = ()
		self._parameters = {"Nd" : "Donor Concentration",
								  "Na" : "Accepotr Concentration"}

		super(Doping, self).generateModel(device,region)

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

class EquilibriumHolesElectrons(NodeModel):
	def __init__(self, device, region):
		if not InNodeModelList(device, region, "NetDoping"):
			Doping(device,region)
	
		if not InNodeModelList(device, region, "IntrinsicCarrierConcentration"):
			IntrinsicCarrier(device,region)

		self._name = ("EquilibriumElectrons", "EquilibriumHoles")
		self._equations = ("(1e-10 + 0.5*abs(NetDoping+(NetDoping^2 + 4 * \
									IntrinsicCarrierConcentration^2)^(0.5)))",
								"(1e-10 + 0.5*abs(-NetDoping+(NetDoping^2 + 4 * \
									IntrinsicCarrierConcentration^2)^(0.5)))")

		self._solutionVariables = ()
		self._parameters = {}

		super(EquilibriumHolesElectrons, self).generateModel(device,region)


class IntrinsicHoleElectronCharge(NodeModel):
	def __init__(self, device, region):
		if not InNodeModelList(device, region, "NetDoping"):
			Doping(device, region)
			
		if not InNodeModelList(device, region, "IntrinsicCarrierConcentration"):
			IntrinsicCarrier(device, region)

		self._name = (	"IntrinsicElectrons", 
							"IntrinsicHoles", 
							"IntrinsicCharge")
		
		self._equations = \
			("IntrinsicCarrierConcentration * exp ( Potential / V_t)", 
			 "IntrinsicCarrierConcentration^2 / IntrinsicElectrons", 
			 "kahan3(IntrinsicHoles, -IntrinsicElectrons, NetDoping)")

		self._solutionVariables = ("Potential",)

		super(IntrinsicHoleElectronCharge, self).generateModel(device, region)

class Density:
	pass

class Charge(NodeModel, Density):
	
	def __init__(self, device, region, carrier):
		self._name = ("{}ChargeDensity".format(carrier[0]),)
		self._equations = ("{p}ElectronCharge * {c}".format(p=carrier[1], c=carrier[0]),)
		self._solutionVariables = (carrier[0],)
		self._parameters = {"ElectronCharge": "charge of an electron in Coulombs"}

		super(Charge, self).generateModel(device, region)

class DensityFactory(Factory):
	models = Factory.generateFactory(Density)
	
