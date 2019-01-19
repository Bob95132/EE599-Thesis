from ds import *
from util/model import *
from util/model_create import *

class Doping(NodeModel):
	#TODO: maybe expand this for varying Donor Acceptor Concentration
	def __init__(self, device, region):
		self._name = ("NetDoping",)
		self._equation = ("Nd - Na",)
		self._solutionVariables = ()
		self._parameters = {"Nd" : "Donor Concentration",
								  "Na" : "Accepotr Concentration"}

		super(Doping, self).genterateModel(device,region)

class IntrinsicCarrier(NodeModel):
	def __init__(self, device, region):
		self._name = ("IntrinsicCarrierConcentration",)
		self._equation = ("(Nc * Nv) ^ (0.5)  * exp (- Eg / V_t)",)
		self._solutionVariables = ()
		self._parameters = { "Nc":"Carriers in conduction band in material"
									"Nv", "Carriers in valence band in material",
									"V_t" : "Thermal Voltage",
									"Eg" : "Bandgap Energy"}
		super(IntrinsicCarrier, self).generateModel(device, region)

class EquilibriumHolesElectrons(NodeModel):
	def __init__(self, device, region):
		if not InNodeModelList(device, region, "NetDoping"):
			Doping(device,region)
	
		if not InNodeModelList(device, region, "IntrinsicCarrierConcentration"):
			IntrinsicCarrier(device,region)

		self._name = ("EquilibriumElectrons", "EquilibriumHoles")
		self._equation = ("(1e-10 + 0.5*abs(NetDoping+(NetDoping^2 + 4 * \
									IntrinsicCarrierConcentration^2)^(0.5)))",
								"(1e-10 + 0.5*abs(NetDoping+(NetDoping^2 + 4 * \
									IntrinsicCarrierConcentration^2)^(0.5)))")

		self._solutionVariables = ()
		self._paramters = {}

		super(EquilibriumHolesElectrons, self).generateModel(device,region)


class InstrinsicHoleElectronCharge(NodeModel):
	#TODO: May need to redefine current impl with the ifelse equations due to derivative
	#		 sign problem
	carrierMajority = "ifelse(NetDoping > 0, \
								IntrinsicCarrierConcentration * exp(Potential / V_t), \
								(IntrinsicCarrierConcentration) ^ 2 / {})"

	carrierMajorityDerivative = "ifelse(NetDoping > 0, \
									IntrinsicCarrierConcentration * exp(Potential / V_t) / V_t, \
									-IntrinsicCarrierConcentration * exp(Potential / V_t) / V_t)"
	

	def __init__(self, device, region):
		if not InNodeModelList(device, region, "NetDoping"):
			Doping(device, region)
			
		if not InNodeModelList(device, region, "IntrinsicCarrierConcentration"):
			IntrinsicCarrier(device, region)

		#TODO: Not Switching MajorityCarrier
		self._name = (	"IntrisicElectrons", 
							"IntrinsicHoles", 
							"IntrinsicCharge", 
							"PotentialIntrinsicCharge")
		
		self._equation = ("IntrinsicCarrierConcentration * exp (Potential / V_t)"),
					"IntrinsicCarrierConcentration^2 / IntrinsicElectrons", 
					"kahan3(IntrinsicHoles, -IntrinsicElectrons, NetDoping)",
					"-ElectronCharge * IntrinsicCharge")

		self._solutionVariables = ("Potential",)

		super(IntrinsicCharge, self).generateModel(device, region)

