from ds import *
from util/model import *
from util/model_create import *

class InterfacePotential(ContinousInterfaceModel):
	self._name = "PotentialEquation"
	self._solutionVariables = "Potential"

	super(InterfacePotential, self).generateModel(device, region)

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



