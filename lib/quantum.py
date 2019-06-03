from devsim import *
from util.model import *
from util.model_create import *
from util.model_factory import *

class WaveDensityFlux(EdgeModel):
	
	def __init__(self, device, region, variables):
		self._name = ("{carrier}WaveDensityFlux_{state}".format(state=variables[1], carrier=variables[0]),)
		self._equations = ("-(h/(2 * pi))^2 / (2 * M_{carrier}) * (WaveDensity_{state}@n1 - WaveDensity_{state}@n0) * EdgeInverseLength / 100".format(state=variables[1], carrier=variables[0]),)
		self._solutionVariables = ("{carrier}WaveDensity_{state}".format(state=variables[1], carrier=variables[0]),)
		self._parameters = {"h" : "Planck's Constant",
								  "M_Electrons" : "Mass of Electrons" }

		EnsureEdgeFromNodeModelExists(device, region, "WaveDensity", "Quantum")

		super(WaveDensityFlux, self).generateModel(device, region)

def createWeighter(name, equation, solutionVariables, parameters):
	metaName = "{carrier}WaveDensity{name}_{state}".format(name=name)
	metaEquation = "{equation} * {carrier}WaveDensity_{state}".format(equation=equation)

	class WaveDensityWeight(NodeModel):
		def __init__(self, device, region, variables):
			self._name = (metaName.format(name=name, state=variables[1], carrier=variables[0]),)
			self._equations(metaEquation.format(name=name, state=variables[1], carrier=variables[0]),)
			self._solutionVariables = solutionVariables + ("{carrier}WaveDensity_{state}".format(state=variables[1], carrier=variables[0],)
			self._parameters = parameters

			super(WaveDensityWeight, self).generateModel(device, region)

	return WaveDensityWeight

WaveDensityEnergy = createWeighter("Energy", "{carrier}Energy_{state}", (), {})
WaveDensitySquarePotential = createWeighter("Potential", "Potential - ", ("Potential",), {"PotentialBarrier":"Barrier of the Junction"})

class ConfinedCarrier(NodeModel): 

	def __init__(self, device, region, variables):
		self._name = ("Confined{}".format(variables[0]),)
		self._equations = ("",)

	@classmethod
	def calculateNumStates(PotentialBarrier):
		#assumed square potential
		n_max = math.floor(1 + math.sqrt(PotentialBarrier/E_0))
		for i in range(1, n_max):
			
