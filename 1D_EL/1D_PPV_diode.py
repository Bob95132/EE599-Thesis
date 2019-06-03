from devsim import *

#set_parameter(name="debug_level", value="verbose")


from util.model_create import *
import transport
import contacts
import carrier
import potential
import mobility
import recombination
import thermal
import equation_builder
import optical
import csv
import mesh as msh
import helmholtz
import geom

device="PNJunction"
region="MyRegion"

# material db
open_db(filename="../lib/MaterialDatabase")

# create grid
myMesh = msh.OneDOneMaterial(501, .000000000600)
create_gmsh_mesh(mesh="diode1d", coordinates=myMesh[1], elements=myMesh[2], physical_names=myMesh[0])
add_gmsh_region(mesh="diode1d", gmsh_name="Bulk",    
					region=region, material="OC1C10")
add_gmsh_contact(mesh="diode1d", gmsh_name="Base",    
						region=region, material="Calcium", name="top")
add_gmsh_contact(mesh="diode1d", gmsh_name="Emitter", 
						region=region, material="ITO", name="bot")
finalize_mesh    (mesh="diode1d")
create_device    (mesh="diode1d", device=device)

set_parameter(name="threads_available", value=4)
set_parameter(name="threads_task_size", value=1024)
set_parameter(name = "extended_solver", value=True)
set_parameter(name = "extended_model", value=True)
set_parameter(name = "extended_equation", value=True)

#print(get_node_model_values(device=device, region=region, name="AtContactNode"))
#exit()

geom.RegionLength(device, region)
#add potential to create equilibrium conditions
thermal.ThermalVoltage(device, region)
carrier.IntrinsicCarrier(device, region)
carrier.IntrinsicHoleElectron(device, region)


potential.ElectricField(device, region)
potential.SemiconductorIntrinsicCarrierPotential(device, region)

potentialEquation = equation_builder.EquationBuilder(device, region, 
																	"Potential", 
																	("Potential", "Electrons", "Holes"),
																	"default" )

potentialEquation.addModel("PotentialEdgeFlux", "EdgeModel")
potentialEquation.addModel("PotentialIntrinsicCharge", "NodeModel")
potentialEquation.buildEquation()



for i, edge in zip(get_contact_list(device=device), ("N_Holes", "N_Electrons")):
	contacts.OhmicContact(device, region, i, edge, False)
	contacts.PECContact(device, region, i, "5e14")
	#contacts.SchottkyContact(device, region, i, False)
	set_parameter(device=device, name=GetContactBiasName(i), value=0.0)

solve(type="dc", absolute_error=1.0, relative_error=1e-6, maximum_iterations=30)

carrier.EquilibriumElectronsHoles(device, region)


#add changing bias
recombination.RecombinationFactory.generateModel(device, region, "Langevin")
#recombination.RecombinationFactory.generateModel(device, region, "Auger")
#recombination.RecombinationFactory.generateModel(device, region, "ShockleyReadHall")
recombination.RecombinationFactory.generateModel(device, region, "StimulatedEmission", "5e14")

optical.ElectromagneticTransient(device, region, "5e14")
optical.ElectromagneticEmission(device, region, "5e14")
optical.ElectromagneticGeneration(device, region, "5e14")
opticalEquation = equation_builder.EquationBuilder(device, region, "Photons_5e14",
																	("Electrons", "Holes", "Photons_5e14"),
																	"default")
opticalEquation.addModel("ElectromagneticTransient_5e14", "TimeNodeModel")
opticalEquation.addModel("ElectromagneticEmission_5e14", "NodeModel")
opticalEquation.addModel("ElectromagneticGeneration_5e14", "NodeModel")
opticalEquation.buildEquation()
optical.ElectromagneticEmittedPower(device, region, "5e14")

carrierEquation = {}

carrier.DensityFactory.ElectronHoleChargeDensity(device, region)
mobility.MobilityFactory.ElectronHoleMobility(device, region, "CorrelatedDisorder")
transport.CurrentFactory.ElectronHoleDriftDiffusionCurrent(device, region)
for carrier in ("Electrons", "Holes"):	
	carrierEquation[carrier] = equation_builder.EquationBuilder(device, region, carrier, 
																			("Potential", "Electrons", "Holes"),
																			"default")

	carrierEquation[carrier].addModel(carrier + "ChargeDensity", "TimeNodeModel")
	carrierEquation[carrier].addModel(carrier + "Current", "EdgeModel")
	carrierEquation[carrier].addModel(carrier + "Generation", "NodeModel") 
	carrierEquation[carrier].buildEquation()

potential.SemiconductorExcessCarrierPotential(device, region)
potentialEquation.deleteModel("PotentialIntrinsicCharge", "NodeModel")
potentialEquation.addModel("PotentialNodeCharge", "NodeModel")
potentialEquation.buildEquation()

for i,edge in zip(get_contact_list(device=device), ("N_Holes", "N_Electrons")):
	contacts.OhmicContact(device, region, i , edge, False)
	#contacts.SchottkyContact(device, region, i, False)
	set_parameter(device=device, name=GetContactBiasName(i), value=0.0)

set_node_values(device=device, region=region, name="Electrons", init_from="IntrinsicElectrons")
set_node_values(device=device, region=region, name="Holes", init_from="IntrinsicHoles")

solve(type="dc", absolute_error=1e06, relative_error=1e-06, maximum_iterations=30)
opticalDensity = helmholtz.HelmholtzSolver(device, "5e14", "MyRegion")
opticalDensity.Solve()

#write_devices(file="2D_PPV_diode", device=device,type="vtk")
#exit()

current = []
voltage = []
gain = []
power = []
v = 0.0
while v < 155.1:
	set_parameter(device=device, name=GetContactBiasName("bot"), value=v)
	solve(type="dc", absolute_error=1e17, relative_error=1e+05, maximum_iterations=30)
	voltage.append(v)
	e_c = get_contact_current(device=device, contact="bot", equation="ElectronsContinuityEquation")
	h_c = get_contact_current(device=device, contact="bot", equation="HolesContinuityEquation")
	p_c = get_node_model_values(device=device, region=region, name="ElectromagneticEmittedPower_5e14")[0]
	g_c = get_node_model_values(device=device, region=region, name="PhotonModalGain_5e14")[255]
	ef_c = get_node_model_values(device=device, region=region, name="ElectronFermFunction_5e14")[255]
	hf_c = get_node_model_values(device=device, region=region, name="HoleFermFunction_5e14")[255]
	current.append(e_c + h_c)
	power.append(p_c)
	gain.append(g_c)
	PrintCurrents(device, "top")
	PrintCurrents(device, "bot")
	print(v, e_c, h_c, p_c, g_c, ef_c, hf_c)
	v += .1
	opticalDensity.Solve()

#
iv = zip(voltage, current, power, gain)
with open('MidStimulatedOhmicField_iv-curve.csv', 'w') as f:
	writer = csv.writer(f, delimiter=',')
	writer.writerows(iv)

write_devices(file="MidStimulatedOhmicField", device=device,type="vtk")

