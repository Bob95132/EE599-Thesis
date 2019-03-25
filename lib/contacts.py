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
		if InNodeModelList(device, region, "Electrons"):

			if not InNodeModelList(device, region, "EquilibriumElectrons"):
				raise MissingModelError("EquilibriumElectrons", "Carrier")

			if not InEdgeModelList(device, region, "ElectronsCurrent"):
				raise MissingModelError("ElectronsCurrent", "Transport")
			
			CreateSolution(device=device, region=region, name="IntrinsicEquilibriumElectrons")
			set_node_values(device=device, region=region, name="IntrinsicEquilibriumElectrons", init_from="IntrinsicElectrons")
			electronsContactModel = "Electrons - IntrinsicEquilibriumElectrons"#ifelse(NetDoping == 0, IntrinsicEquilibriumElectrons, ifelse(NetDoping > 0, EquilibriumElectrons, IntrinsicCarrierConcentration^2/EquilibriumHoles))"
			modelName = contact + "OhmicElectronsBC"
			CreateContactNodeModel(device, contact, modelName, electronsContactModel)
			CreateContactNodeModel(device, contact, "{0}:{1}".format(modelName, "Electrons"), "1")

			self._name.append("ElectronsContinuityEquation")
			self._equation.append((modelName, "", "", "", "", "", "", "ElectronsCurrent", ""))
			self._solutionVariables.append("Electrons")
			self._isCircuit.append(isCircuit)
			
		#generate Electron BC if there
		if InNodeModelList(device, region, "Holes"):
			
			if not InNodeModelList(device, region, "EquilibriumHoles"):
				raise MissingModelError("EquilibriumHoles", "Carrier")

			if not InEdgeModelList(device, region, "HolesCurrent"):
				raise MissingModelError("HolesCurrent", "Transport")

			CreateSolution(device=device, region=region, name="IntrinsicEquilibriumHoles")
			set_node_values(device=device, region=region, name="IntrinsicEquilibriumHoles", init_from="IntrinsicHoles")
			holesContactModel = "Holes - IntrinsicEquilibriumHoles" #ifelse(NetDoping == 0, IntrinsicEquilibriumHoles, ifelse(NetDoping > 0, IntrinsicCarrierConcentration^2/EquilibriumElectrons, EquilibriumHoles))"
			modelName = contact + "OhmicHolesBC"
			CreateContactNodeModel(device, contact, modelName, electronsContactModel)
			CreateContactNodeModel(device, contact, "{0}:{1}".format(modelName, "Holes"), "1")
			
			self._name.append("HolesContinuityEquation")
			self._equation.append((modelName, "", "", "", "", "", "", "HolesCurrent", ""))
			self._solutionVariables.append("Holes")
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
			potentialContactModel = potentialContactModel + "- ({Wf} - {affinity})".format(Wf=workFunction, affinity=affinity)
			
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
		if InNodeModelList(device, region, "Electrons"): 
			
			if not InNodeModelList(device, region, "EquilibriumElectrons"):
				raise MissingModelError("EquilibriumElectrons", "Carrier")

			if not InEdgeModelList(device, region, "ElectronsCurrent"):
				raise MissingModelError("ElectronsCurrent", "Transport")

			#In units of eV and additional conversion factor from 1/m^2 -> 1/cm^2 (1/10000)
			workFunction = float(get_db_entry(material=get_material(device=device, contact=contact), parameter="WorkFunction")[0])
			E_Holes = float(get_db_entry(material=get_material(device=device, region=region), parameter="E_Holes")[0])
			E_Electrons = float(get_db_entry(material=get_material(device=device, region=region), parameter="E_Electrons")[0])
			polarity = "+"  if abs(workFunction - E_Electrons) < abs(workFunction - E_Holes) else "-"
			modelName = contact + "SchottkyElectronsBC"
			richardsonConstant = "(4 * pi * M_Electrons * (V_t)^2 / (h^3 * N_Electrons * 10000))"
			CreateSolution(device=device, region=region, name="IntrinsicEquilibriumElectrons")
			set_node_values(device=device, region=region, name="IntrinsicEquilibriumElectrons", init_from="IntrinsicElectrons")
			carriers = []
			carriers.append("IntrinsicEquilibriumElectrons" if contact == "top" else "Electrons")
			carriers.append("Electrons" if contact == "top" else "IntrinsicEquilibriumElectrons")
			electronsContactModel = "ElectronsCurrent + {p}{R} * ({c1}@n1 - {c0}@n0)".format(p=polarity, R=richardsonConstant, c0=carriers[0], c1=carriers[1])
			CreateContactEdgeModel(device, contact, modelName, electronsContactModel)
			CreateContactEdgeModelDerivative(device, contact, modelName, electronsContactModel, ("Electrons", "Potential"))

			self._name.append("ElectronsContinuityEquation")
			self._equation.append(("", modelName, "", "", "", "", "", "ElectronsCurrent", ""))
			self._solutionVariables.append("Electrons")
			self._isCircuit.append(isCircuit)
			
		if InNodeModelList(device, region, "Holes"):
			
			if not InNodeModelList(device, region, "EquilibriumHoles"):
				raise MissingModelError("EquilibriumHoles", "Carrier")

			if not InEdgeModelList(device, region, "HolesCurrent"):
				raise MissingModelError("HolesCurrent", "Transport")

			#In units of eV and additional conversion factor from 1/m^2 -> 1/cm^2 (1/10000)
			workFunction = float(get_db_entry(material=get_material(device=device, contact=contact), parameter="WorkFunction")[0])
			E_Holes = float(get_db_entry(material=get_material(device=device, region=region), parameter="E_Holes")[0])
			E_Electrons = float(get_db_entry(material=get_material(device=device, region=region), parameter="E_Electrons")[0])
			polarity = "-"  if abs(workFunction - E_Electrons) < abs(workFunction - E_Holes) else "+"
			modelName = contact + "SchottkyHolesBC"
			richardsonConstant = "(4 * pi * M_Holes * (V_t)^2 / (h^3 * N_Holes * 10000))"
			CreateSolution(device=device, region=region, name="IntrinsicEquilibriumHoles")
			set_node_values(device=device, region=region, name="IntrinsicEquilibriumHoles", init_from="IntrinsicHoles")
			carriers = []
			carriers.append("IntrinsicEquilibriumHoles" if contact == "top" else "Holes")
			carriers.append("Holes" if contact == "top" else "IntrinsicEquilibriumHoles")
			holesContactModel = "HolesCurrent + {p}{R} * ({c1}@n1 - {c0}@n0)".format(p = polarity, R=richardsonConstant, c0=carriers[0], c1=carriers[1])
			CreateContactEdgeModel(device, contact, modelName, holesContactModel)
			CreateContactEdgeModelDerivative(device, contact, modelName, holesContactModel, ("Potential", "Holes"))

			self._name.append("HolesContinuityEquation")
			self._equation.append(("", modelName, "", "", "", "", "", "HolesCurrent", ""))
			self._solutionVariables.append("Holes")
			self._isCircuit.append(isCircuit)
			
		super(SchottkyContact, self).generateModel(device, contact)

class PECContact(ContactModel):
	
	def __init__(self, device, region, contact, isCircuit=False):
		nodeModels = filter(lambda x: "OpticalDensity_" in x, get_node_model_list(device, region))

		for model in nodeModels:
			modelName = contact + model + "BC"
			CreateContactNodeModel(device, contact, modelName, model)
			CreateContactNodeModelDerivative(device, contact, modelName, model, model)
			self._name.append(model + "Equation")
			self._equation.append(modelName, "", "", "", "", "", "", "", "")
			self._solutionVariables.append(model)
			self._isCircuit.append(isCircuit)

		super(PECContact, self).generateModel(device, contact)
