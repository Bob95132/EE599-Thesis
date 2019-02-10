from devsim import *
from util.model import *
from util.model_create import *
from util.error import *


class ContactPotential(ContactModel):
	def __init__(self, device, region, contact, isCircuit=False):

		if not InNodeModelList(device, region, "PotentialIntrinsicCharge"):
			raise MissingModelError("PotentialIntrinsicCharge", "Potential")

		if not InNodeModelList(device, region, "IntrinsicCarrierConcentration"):
			raise MissingModelError("IntrinsicCarrierConcentration", "Carrier")

		if not InNodeModelList(device, region, "NetDoping"):
			raise MissingModelError("NetDoping", "Carrier")
	
		if not InNodeModelList(device, region, "EquilibriumElectrons") or not InNodeModelList(device,region, "EquilibriumHoles"):
			raise MissingModelError("EquilibriumHolesElectrons", "Carrier")

		model = "Potential - {0} + ifelse(NetDoping > 0, -V_t*log(EquilibriumElectrons/IntrinsicCarrierConcentration), V_t*log(EquilibriumHoles/IntrinsicCarrierConcentration))".format(GetContactBiasName(contact))
																	
		modelName = GetContactBiasName(contact)
		CreateContactNodeModel(device, contact, modelName, model)
		CreateContactNodeModel(device, contact, "{0}:{1}".format(modelName, "Potential"), "1")

		if isCircuit:
			CreateContactNodeModel(device, contact, "{0}:{1}".format(modelName, GetContactBiasName(contact)), "-1")
			
		self._name = "PotentialContinuityEquation"
		self._equation = (modelName, "", "", "PotentialIntrinsicCharge", "PotentialEdgeFlux", "", "", "" , "")
		self._solutionVariables = "Potential"
		self._isCircuit = isCircuit
		super(ContactPotential, self).generateModel(device, contact)

class ContactCarrier:
	modelName = "{0}Node{1}"
	model = "{0} - ifelse(NetDoping > 0, {1}, {2})"


class ContactElectrons(ContactModel, ContactCarrier):		

	def __init__(self, device, region, contact, isCircuit=False):

		if not InNodeModelList(device, region, "EquilibriumElectrons") \
			or not InNodeModelList(device, region, "EquilibriumHoles"):
			raise MissingModelError("EquilibriumCarriers", "Carrier")

		if not InNodeModelList(device, region, "IntrinsicCarrierConcentration"):
			raise MissingModelList("IntrinsicCarrierConcentration", "Carrier")

		if not InNodeModelList(device, region, "NetDoping"):
			raise MissingModelError("NetDoping", "Carrier")

		if not InEdgeModelList(device, region, "ElectronsCurrent"):
			raise MissingModelError("ElectronsCurrent", "Transport")

		self._model = self.model.format("Electrons", 
											"EquilibriumElectrons",
											"IntrinsicCarrierConcentration^2/EquilibriumHoles")

		self._modelName = self.modelName.format(contact, "Electrons")
		self._name = "ElectronsContinuityEquation"
		self._equation = (self._modelName, "", "", "", "", "", "", "ElectronsCurrent", "")
		self._solutionVariables = "Electrons"
		self._isCircuit = isCircuit

		CreateContactNodeModel(device, contact, 
										self._modelName,
										self._model)

		CreateContactNodeModel(device, contact,
										"{0}:{1}".format(self._modelName, "Electrons"),
										"1")

		super(ContactElectrons, self).generateModel(device, contact)


class ContactHoles(ContactModel, ContactCarrier):
	def __init__(self, device, region, contact, isCircuit=False):

		if not InNodeModelList(device, region, "EquilibriumElectrons") or \
			not InNodeModelList(device, region, "EquilibriumHoles"):
			raise MissingModelError("EquilibriumCarriers", "Carrier")

		if not InNodeModelList(device, region, "IntrinsicCarrierConcentration"):
			raise MissingModelList("IntrinsicCarrierConcentration", "Carrier")

		if not InNodeModelList(device, region, "NetDoping"):
			raise MissingModelError("NetDoping", "Carrier")

		if not InEdgeModelList(device, region, "HolesCurrent"):
			raise MissingModelError("HolesCurrent", "Transport")

		self._model = self.model.format("Holes", 
											"IntrinsicCarrierConcentration^2 / EquilibriumElectrons",
											"EquilibriumHoles")
		self._modelName = self.modelName.format(contact, "Holes")
		self._name = "HolesContinuityEquation"
		self._equation = (self._modelName, "", "", "", "", "", "", "HolesCurrent", "")
		self._solutionVariables = "Holes"
		self._isCircuit = isCircuit

		CreateContactNodeModel(device, contact, 
										self._modelName,
										self._model)

		CreateContactNodeModel(device, contact,
										"{0}:{1}".format(self._modelName, "Holes"),
										"1")

		super(ContactHoles, self).generateModel(device, contact)

class ContactHoleElectronContinuity:


	def __init__(self, device, region, contact, isCircuit=False):
		ContactHoles(device, region, contact, isCircuit)
		ContactElectrons(device, region, contact, isCircuit)

	
