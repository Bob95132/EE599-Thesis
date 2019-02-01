from devsim import *
from util.model import *
from util.model_create import *

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
		self._equations = ("(Nc * Nv) ^ (0.5)  * exp ( - (Ec - Ev) / (2*V_t))",)
		self._solutionVariables = ()
		self._parameters = { "Nc":"Carriers in conduction band in material",
									"Nv": "Carriers in valence band in material",
									"V_t" : "Thermal Voltage",
									"Ec" : "Conduction Band Energy",
									"Ev" : "Valence Band Energy"}
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
								"(1e-10 + 0.5*abs(NetDoping+(NetDoping^2 + 4 * \
									IntrinsicCarrierConcentration^2)^(0.5)))")

		self._solutionVariables = ()
		self._paramters = {}

		super(EquilibriumHolesElectrons, self).generateModel(device,region)


class IntrinsicHoleElectronCharge(NodeModel):
	def __init__(self, device, region):
		if not InNodeModelList(device, region, "NetDoping"):
			Doping(device, region)
			
		if not InNodeModelList(device, region, "IntrinsicCarrierConcentration"):
			IntrinsicCarrier(device, region)

		#TODO: Not Switching MajorityCarrier
		self._name = (	"IntrinsicElectrons", 
							"IntrinsicHoles", 
							"IntrinsicCharge")
		
		self._equations = \
			("IntrinsicCarrierConcentration * exp ( Potential / V_t)", 
			 "IntrinsicCarrierConcentration^2 / IntrinsicElectrons", 
			 "kahan3(IntrinsicHoles, -IntrinsicElectrons, NetDoping)")

		self._solutionVariables = ("Potential",)

		super(IntrinsicHoleElectronCharge, self).generateModel(device, region)

