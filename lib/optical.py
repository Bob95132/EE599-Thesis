from devsim import *
from util.model import *
from util.model_create import *
from util.model_factory import *

class Absorption(NodeModel):
	def __init__(self, device, region):
		self._name = ("PhotonAbsorption",)
		self._equations = ("-mu_p_a * Photons",)
		self._solutionVariables = ("Photons",)
		self._parameters = {"mu_p_a": "absorption coefficient"}

class PhotonDiffusion(ParameterModel):
	def __init__(self, device, region):
		self._name = ("PhotonDiffusion",)
		self._equations = ("1/(3 * ((1 - Photon_iso)*mu_p_s + Photon_alpha*mu_p_a))",)
		self._solutionVariables = ()
		self._parameters = {"Photon_iso" : "isotropy of the material",
								  "mu_p_s": "scattering coefficient",
								  "Photon_alpha" : "contribution of absorption to diffusion",
								  "mu_p_a" : "absorption coefficient"}

class PhotonFlux(EdgeModel):
	def __init__(self, device, region):
		self._name = ("PhotonFlux",)
		self._equations = ("PhotonDiffusion * (Photons@n1 - Photons@n0) * EdgeInverseLength / 100",)
		self._solutionVariables = ("Photons",)
		self._parameters = {"PhotonDiffusion" : "diffusion coefficient for photons"}

		PhotonDiffusion(device, region)

		super(PhotonFlux, self).generateModel(device, region)


class OpticalDensityFlux(EdgeModel):
	def __init__(self, device, region, variables)
		self._name = ("OpticalDensityFlux_{wave}".format(wave=variables[0],)
		self._equations = ("(c^2 / {wave}^2) * (OpticalDensity_{wave}@n1 - OpticalDensity_{wave}@n0) * EdgeInverseLength / 100".format(wave=variables[0],)
		self._solutionVariables = ("OpticalDensity_{wave}".format(wave=variables[0],)
		self._parameters = {}

		super(OpticalDensityFlux, self).generateModel(device, region)

class OpticalDensitySource(NodeModel):
	def __init__(self, device, region):
		self._name = ("OpticalDensitySource_{wave}".format(wave=variables[0], )
		self._equations = ("pow(2 * h * {wave} * PhotonsGeneration / Permittivity, .5)",)
		self._solutionVariables = ("Electrons", "Holes")
		self._parameters = {}

		super(OpticalDensitySource, self).generateModel(device, region)

def createWeighter(name, equation, solutionVariables, parameters):
	metaName = "OpticalDensity{name}_{wave}".format(name=name)
	metaEquation = "{equation} * OpticalDensity_{wave}".format(equation=equation)

	class OpticalDensityWeight(NodeModel):
	#TODO: weight must be a scalar, so do not have to add dependencies (maybe add dependency tracker)
		def __init__(self, device, region, variables):
			self._name = (metaName.format(wave=variables[0],)
			self._equations = (metaEquation.format(wave=variables[0],)
			self._solutionVariables = solutionVariables + ("OpticalDensity_{wave}".format(wave=variables[0],)
			self._parameters = parameters

			super(OpticalDensityWeight, self).generateModel(device, region)

	return OpticalDensityWeight

OpticalDensityRefractive = createWeighter("Refractive", "(n[{wave}])^2", (), {"n[{wave}]" : "Refractive Index of material at given wavelength"})
OpticalDensityAbsorption = createWeighter("Absorption", "(-(k[{wave}])^2", (), {"k[{wave}]" : "Extinction Coefficient of material at given wavelength"}


