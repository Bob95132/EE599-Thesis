
from devsim import *
from util/model import *
from util/model_create import *

class ThermalVoltage(NodeModel):
	self._name=("V_t",)
	self._equation=("k * T / ElectronCharge", )
	self._solutionVariables=()
	self._paramters={"k": "Boltzmann",
						  "T": "Temperature",
						  "ElectronCharge", "Charge of an Electron"}

	def __init__(device, region):
		super(ThermalVoltage, self).generateModel(device, region)
