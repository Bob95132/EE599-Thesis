from ds import *
from util/model import *
from util/model_create import *
from potential import IntrinsicPotential
from carrier import IntrinsicCharge 


class ContactPotential(ContactModel):
	def __init__(self, device, region, contact, isCircuit=False):

		if not InNodeModelList(device, region, "PotentialIntrinsicCharge"):
			IntrinsicCharge(device, region) 

		if not InEdgeModelList(device, region, "PotentialEdgeFlux"):
			IntrinsicPotential(device, region)

		model = "Potential - {0} + \
					ifelse(NetDoping > 0, \
					-V_t*log(/ IntrinsicCarrierConcentration, \
					V_t*log( / IntrinsicCarrierConcentration".format(GetContactBiasName(contact),
																							)
																	
		model_name = GetContactNodeModelName(contact)					
		CreateContactNodeModel(device, contact, model_name, model)
		CreateContactNodeModel(device, contact, 
										"{0}:{1}".format(modelName, "Potential", "1")

		if isCircuit:
			CreateContactNodeModel(device, contact, 
										"{0}:{1}".format(modelName, GetContactBiasName(contact)), "-1")
			
		self._name = "PotentialEquation"
		self._equation = (model, "", "PotentialIntrinsicCharge", "PotentialEdgeFlux", "" , "")
		self._solutionVariables = "Potential"
		super(ContactPotential, self).generateModel(device, region)

class ContactHoleElectronHoleContinuity();
	modelName = "{0}Node{1}"
	model = "{0} - ifelse(NetDoping > 0, {1}, \
				IntrinsicCarrierConcentration^2 / {2}"

	class ContactElectrons(ContactModel):
		

		def __init__(self, device, contact):
			self._model = model.format("Electrons", 
												"EquilibriumElectrons",
												"EquilibriumHoles")

			self._modelName = modelName.format(contact, "Electrons")
			self._name = "ElectronsContinuityEquation"
			self._equation = (self._model, "", "", "", "", 
									"ElectronsDriftDiffusionCurrent")
			self._solutionVariables = "Electrons"

			CreateContactNodeModel(device, contact, 
											self._modelName,
											self._model)

			CreateContactNodeModel(device, contact,
											"{0}:{1}".format(self._modelName, "Electrons"),
											"1")

			super(ContactElectrons, self).generateModel(device, region)


	class ContactHoles(ContactModel):
		def __init__(self, device, region):
			self._model = model.format("Holes", 
												"EquilibriumHoles",
												"EquilibriumElectrons")
			self._modelName = modelName.format(contact, "Holes")
			self._name = "HolesContinutiyEquation"
			self._equation = (self._model, "", "", "", "", 
									"HolesDriftDiffusionCurrent")
			self._solutionVariables = "Holes"

			CreateContactNodeModel(device, contact, 
											self._modelName,
											self._model)

			CreateContactNodeModel(device, contact,
											"{0}:{1}".format(self._modelName, "Holes"),
											"1")

			super(ContactHoles, self).generateModel(device, region)

	def __init__(self, device, region):
		if not InNodeModelList(device, region, "EquilibriumHoles") or
			not InNodeModelList(device, region, "EquilibriumElectrons"):
			IntrinsicCharge(device, region)

		self._Holes = ContactHoles(device, region)
		self._Electrons = ContactElectrons(device, region)

	
