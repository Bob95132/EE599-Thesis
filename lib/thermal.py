
from devsim import *
from util.model import *
from util.model_create import *

class ThermalVoltage(ParameterModel):
	def __init__(self, device, region):
		self._name="V_t"
		self._equation="k * T / ElectronCharge"
		self._paramters={"k": "Boltzmann",
						  "T": "Temperature",
						  "ElectronCharge": "Charge of an Electron"}

		super(ThermalVoltage, self).generateModel(device, region)
