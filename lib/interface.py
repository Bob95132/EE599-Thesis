from devsim import *
from util.model import *
from util.model_create import *
from util.model_factory import *

class ContinuousPotential(InterfaceModel):

	def __init__(self, device, interface, region0Equation, region1Equation)
		self._equationName = "ContinousPotential"
		self._region0Equation = region0Equation
		self._region1Equation = region1Equation
		self._name = ("ContinuousPotential",)
		self._equation = ("Potential@r0 - Potential@r1",)
		self._solutionVariable = "Potential"
		self._modelType = "continuous"

		super(ContinuousPotentialInterface, self).generateModel(device, region)

class Schottky(InterfaceModel):

	def __init__(self, device, interface, region0, region1, carrier):

		if InNodeModelList(device, region, "Potential"):


		if InNodeModelList(device, region, "Electrons"):


		if InNodeModelList(device, region
		self._equationName = "{}SchottkyContinuity".format(carrier)
		self._name = ("{}_theta", "{}PotentialBarrier".format(carrier), "{}_nu".format(carrier), self._equationName)
		#TODO: define parameters

		regions = get_region_list(device=device, interface=interface)
		regionTypes = [get_parameter(device=device, region=reg, "material_type") for reg in regions]
		
		theta = "1" if any("metal" in s for s in regionTypes) else "M_{c}@r1/M_{c}@r0".format(c=carrier)
		
		potentials = {"metal" : "Wf@r{r}",
						 "semiconductor" : "E_{c}@r{r}"}

		regPotentials = []
		for idx, reg in regionTypes:
			if reg == "metal":
				regPotentials[idx] = potentials["metal"].format(r=idx)
			else if reg == "semiconductor":
				regPotentials[idx] = potentials["semiconductor"].format(r=idx, c=carrier)

		PotentialBarrier = regPotentials[0] + " - " + regPotentials[1]
		nu = "1" if any("metal" in s for s in regionTypes) else 
				"1 - (1 - 1/{}_theta)*exp(-{}PotentialBarrier/((1-{}_theta)*V_t))".format(carrier) 

		#k,h in eV and M in kg
		richardsonEquation = "4 * pi * M_{c}@r{r} * k^2 / (h^3 * ElectronCharge *  N_{c}@r{r})"
		richardsonConstants = []
		for idx, reg in regionTypes:
			if reg == "metal":
				richardsonConstants[idx] = richardsonEquation.format(c=carrier, r=(idx + 1 % len(regionTypes))
			else if reg == "semiconductor":
				richardsonConstants[idx] = richardsonEquation.format(c=carrier, r=idx)

		
		carriers = {"metal" : "Intrinsic{c}@r{r}",
						"semiconductor" : "{c}@r{r}"}

		carrierVals = []
		for idx, reg in regionTypes:
			if reg == "metal":
				carrierVals[idx] = carriers[reg].format(c=carrier, r=((idx + 1) % len(regionTypes)))
			else if reg == "semiconductor":
				carrierVals[idx] = carriers[reg].format(c=carrier, r=idx)

		#TODO: Have not incorporated imref (deltaPotential) 
		SchottkyFlux = 
			"ElectronCharge * {c}_nu * T^2 * ({c1}*{a1} - {c}_theta*{c0}*{a0}*exp(-{c}PotentialBarrier/V_t))".format(c=carrier,
																																		c0=carrierVals[0],
																																		c1=carrierVals[1], 
																																	a0=richardsonConstants[0],
																																	a1=richardsonConstants[1])
		self._equation = (theta, PotentialBarrier, nu, SchottkyFlux)
		self._solutionVariable = carrier
		self._modeltYpe = "fluxterm"

		super(SchottkyInterface, self).generateModel(device, region)

class InterfaceHoleElectronContinuity:
	
	class InterfaceElectronContinuity(ContinousInterfaceModel):
		self._name = "ElectronsContinuityEquation"
		self._solutionVariables = "Electrons"
		super(InterfaceElectronContinuity, self).generateModel(device, region)

	class InterfaceHoleContinuity(ContinousInterfaceModel):
		self._name = "HolesContinuityEquation"
		self._solutionVariables = "Holes"
		super(InterfaceHoleContinuity, self).generateModel(device, region)

	def __init__(device, region):
		self._HoleInterface = InterfaceHoleContinuity(device,region)
		self._ElectronINterface = InterfaceElectronContinuity(device, region)



