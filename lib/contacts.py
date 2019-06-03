import re

from devsim import *
from util.model import *
from util.model_create import *
from util.error import *


class OhmicContact(ContactModel):
	
	def __init__(self, device, region, contact, bandEdge, isCircuit=False):
		
		self._name = []
		self._equation = []
		self._solutionVariables = []
		self._isCircuit = []
		#generate Potential BC if there
		if InNodeModelList(device, region, "Potential"):
			
			if not InNodeModelList(device, region, "PotentialIntrinsicCharge"):
				raise MissingModelError("PotentialIntrinsicCharge", "Potential")

			if not InEdgeModelList(device, region, "PotentialEdgeFlux"):
				raise MissingModelError("PotentialEdgeFlux", "Potential")
	
			if not InNodeModelList(device, region, "IntrinsicCarrierConcentration"):
				raise MissingModelError("IntrinsicCarrierConcentration", "Carrier")
			
			polarity = "+" if "Holes" in bandEdge else "-"
			contactName = GetContactBiasName(contact)
			potentialContactModel = "Potential - {contact} {polarity} V_t*log({bandEdge}/IntrinsicCarrierConcentration)".format(polarity=polarity, contact=contactName, bandEdge=bandEdge)
			
			modelName = contact + "OhmicPotentialBC"
			CreateContactNodeModel(device, contact, modelName, potentialContactModel)
			CreateContactNodeModel(device, contact, "{0}:{1}".format(modelName, "Potential"), "1")

			if isCircuit:
				CreateContactNodeModel(device, contact, "{0}:{1}".format(modelName, GetContactBiasName(contact)), "-1")

			self._name.append("PotentialContinuityEquation")
			self._equation.append((modelName, "", "", "PotentialIntrinsicCharge", "PotentialEdgeFlux", "", "", "", ""))
			self._solutionVariables.append("Potential")
			self._isCircuit.append(isCircuit)
			
		#TODO: combine Electrons and Holes into for loop
		#generate Electron BC if there
		for carrier in ("Electrons", "Holes"):
			if InNodeModelList(device, region, carrier):

				if not InNodeModelList(device, region, "Equilibrium" + carrier):
					raise MissingModelError("Equilibrium" + carrier, "Carrier")

				if not InEdgeModelList(device, region, carrier + "Current"):
					raise MissingModelError(carrier + "Current", "Transport")
			
				contactModel = "{c} - Equilibrium{c}".format(c=carrier) #ifelse(NetDoping == 0, IntrinsicEquilibriumElectrons, ifelse(NetDoping > 0, EquilibriumElectrons, IntrinsicCarrierConcentration^2/EquilibriumHoles))"
				modelName = contact + "Ohmic{}BC".format(carrier)
				CreateContactNodeModel(device, contact, modelName, contactModel)
				CreateContactNodeModel(device, contact, "{0}:{1}".format(modelName, carrier), "1")

				self._name.append(carrier + "ContinuityEquation")
				self._equation.append((modelName, "", "", "", "", "", "", carrier + "Current", ""))
				self._solutionVariables.append(carrier)
				self._isCircuit.append(isCircuit)

		super(OhmicContact, self).generateModel(device, contact)


class SchottkyContact(ContactModel):
	
	def __init__(self, device, region, contact, isCircuit=False):

		self._name = []
		self._equation = []	
		self._solutionVariables = []
		self._isCircuit = []

		if InNodeModelList(device, region, "Potential"):
			if not InNodeModelList(device, region, "PotentialIntrinsicCharge"):
				raise MissingModelError("PotentialIntrinsicCharge", "Potential")

			if not InEdgeModelList(device, region, "PotentialEdgeFlux"):
				raise MissingModelError("PotentialEdgeFlux", "Potential")
	
			if not InNodeModelList(device, region, "IntrinsicCarrierConcentration"):
				raise MissingModelError("IntrinsicCarrierConcentration", "Carrier")
			
			contactName = GetContactBiasName(contact)
			workFunction = float(get_db_entry(material=get_material(device=device, contact=contact), parameter="WorkFunction")[0])
			E_Holes = float(get_db_entry(material=get_material(device=device, region=region), parameter="E_Holes")[0])
			E_Electrons = float(get_db_entry(material=get_material(device=device, region=region), parameter="E_Electrons")[0])
			if (abs(workFunction - E_Electrons) < abs(workFunction - E_Holes)):
				affinity = "E_Electrons"
				bandEdge = "-V_t * log(N_Electrons/IntrinsicCarrierConcentration^1)"
			else:
				affinity = "E_Holes"
				bandEdge = "+V_t * log(N_Holes/IntrinsicCarrierConcentration^1)"
			
			potentialContactModel = "Potential - {contact} {bandEdge} - ({Wf} - {affinity})".format(contact=contactName, bandEdge=bandEdge, Wf=workFunction, affinity=affinity)
			
			modelName = contact + "SchottkyPotentialBC"
			CreateContactNodeModel(device, contact, modelName, potentialContactModel)
			CreateContactNodeModel(device, contact, "{0}:{1}".format(modelName, "Potential"), "1")

			if isCircuit:
				CreateContactNodeModel(device, contact, "{0}:{1}".format(modelName, GetContactBiasName(contact)), "-1")

			self._name.append("PotentialContinuityEquation")
			self._equation.append((modelName, "", "", "PotentialIntrinsicCharge", "PotentialEdgeFlux", "", "", "", ""))
			self._solutionVariables.append("Potential")
			self._isCircuit.append(isCircuit)
			
		
		#combine electrons and holes into for loop
		for carrier in ("Electrons", "Holes"):
			if InNodeModelList(device, region, carrier): 
			
				if not InNodeModelList(device, region, "Equilibrium" + carrier):
					raise MissingModelError("Equilibrium" + carrier, "Carrier")

				if not InEdgeModelList(device, region, carrier + "Current"):
					raise MissingModelError(carrier + "Current", "Transport")

			#In units of eV and additional conversion factor from 1/m^2 -> 1/cm^2 (1/10000)
				workFunction = float(get_db_entry(material=get_material(device=device, contact=contact), parameter="WorkFunction")[0])
				E_Holes = float(get_db_entry(material=get_material(device=device, region=region), parameter="E_Holes")[0])
				E_Electrons = float(get_db_entry(material=get_material(device=device, region=region), parameter="E_Electrons")[0])
				#polarity = 1  if abs(workFunction - E_Electrons) < abs(workFunction - E_Holes) else -1
				#polarity = polarity if carrier == "Electrons" else -1*polarity
				polarity = "1" if carrier == "Electrons" else "-1"
				#polarity = str(polarity)
				modelName = contact + ("Schottky{}BC".format(carrier))
				richardsonConstant = "(4 * pi * M_{c} * (V_t)^2 / (h^3 * N_{c} * 10000))".format(c=carrier)
				carriers = [] 
				carriers.append("Equilibrium" + carrier if contact == "bot" else carrier)
				carriers.append(carrier if contact == "bot" else "Equilibrium" + carrier)
				contactModel = (carrier + "Current + {p}*{R} * ({c1}@n1 - {c0}@n0)").format(p=polarity, R=richardsonConstant, c0=carriers[0], c1=carriers[1])
				CreateContactEdgeModel(device, contact, modelName, contactModel)
				CreateContactEdgeModelDerivative(device, contact, modelName, contactModel, (carrier, "Potential"))

				self._name.append(carrier + "ContinuityEquation")
				self._equation.append(("", modelName, "", "", "", "", "", carrier + "Current", ""))
				self._solutionVariables.append(carrier)
				self._isCircuit.append(isCircuit)
			
		super(SchottkyContact, self).generateModel(device, contact)

class PECContact(ContactModel):
	
	def __init__(self, device, region, contact, wave):
		
		modelName = "OpticalDensityBoundary_" + wave
		if not InNodeModelList(device, region, modelName):
			CreateSolution(device, region, modelName)
			set_node_value(device=device, region=region, name=modelName, value=0)
	
		regionReflectivity = float(get_db_entry(material=get_material(device=device, region=region), parameter="n_{}".format(wave))[0])
		contactReflectivity = float(get_db_entry(material=get_material(device=device, contact=contact), parameter="n_{}".format(wave))[0])

		R = ((regionReflectivity - contactReflectivity) / (regionReflectivity + contactReflectivity)) ** 2
		reflectName = contact + "Reflectivity"
		CreateSolution(device, region, reflectName)
		set_node_value(device=device, region=region, name=reflectName, value=R)

		for val in get_element_node_list(device=device, region=region, contact=contact):
			set_node_value(device=device, region=region, name=modelName, index=val[0], value=1)			
