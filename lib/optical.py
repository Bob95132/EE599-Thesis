from devsim import *
from util.model import *
from util.model_create import *
from util.model_factory import *

#Photon Diffusion
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

#Time-dependent Model
class ElectromagneticTransient(NodeModel):
	
	def __init__(self, device, region, wave):
		self._name = (self.getName() + "_{wave}".format(wave=wave) ,)
		self._equations = ("Photons_{wave}".format(wave=wave),)
		self._solutionVariables = ("Photons_{wave}".format(wave=wave),)
		self._parameters = {}

		super(ElectromagneticTransient, self).generateModel(device, region)

class ElectromagneticEmission(NodeModel):

	def __init__(self, device, region, wave):
		self._name = ("PhotonAbsorptionLoss_{wave}".format(wave=wave),
						  "PhotonCavityLoss_{wave}".format(wave=wave),
							"PhotonLifetime_{wave}".format(wave=wave),
							self.getName() + "_{wave}".format(wave=wave))
		self._equations = ("vec_sum(OpticalDensity_{wave} * 4 * pi * k_{wave} * {wave} / (100 * c)) / (vec_sum(OpticalDensity_{wave}) + 1e-50) + 1e-50".format(wave=wave),
								 "pow(2 * RegionLength_x * 100, -1) * log(pow(topReflectivity * botReflectivity, -1))",
								 "pow((c * 100 * (PhotonAbsorptionLoss_{wave} + PhotonCavityLoss_{wave}) / n_eff_{wave}), -1)".format(wave=wave),
								"Photons_{wave} * pow(PhotonLifetime_{wave}, -1)".format(wave=wave),)
		self._solutionVariables = ("Photons_{wave}".format(wave=wave),)
		self._parameters = {}

		super(ElectromagneticEmission, self).generateModel(device, region)

class ElectromagneticGeneration(NodeModel):

	def __init__(self, device, region, wave):
		self._name = (self.getName() + "_{wave}".format(wave=wave),)
		#should add beta term for partial langevin contribution in future
		self._equations = ("-(Langevin + StimulatedEmission_{wave})".format(wave=wave),)
		self._solutionVariables = ("Photons_{wave}".format(wave=wave),)
		self._parameters = {}

		super(ElectromagneticGeneration, self).generateModel(device, region)

class ElectromagneticEmittedPower(NodeModel):
	
	def __init__(self, device, region, wave):
		self._name = (self.getName() + "_{wave}".format(wave=wave),)
		#Not sure about vec_sum here... power output throughout region or at edges...
		self._equations = ("RegionLength_x * 100 * vec_sum(1.602e-19 * (PhotonCavityLoss_{wave}/ (PhotonAbsorptionLoss_{wave} + PhotonCavityLoss_{wave})) * h * {wave} * ElectromagneticEmission_{wave})".format(wave=wave),)	
		self._solutionVariables = ("Photons_{wave}".format(wave=wave),)
		self._parameters = {}

		super(ElectromagneticEmittedPower, self).generateModel(device, region)
