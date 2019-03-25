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
import csv
import mesh as msh

device="PNJunction"
region="MyRegion"

# material db
open_db(filename="../lib/MaterialDatabase")

# create grid
myMesh = msh.OneDOneMaterial(1001, .0000000001)
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

#add potential to create equilibrium conditions
thermal.ThermalVoltage(device, region)
carrier.IntrinsicCarrier(device, region)
carrier.EquilibriumHolesElectrons(device, region)
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

for i in get_contact_list(device=device): #, ("N_Holes", "N_Electrons")):
	#contacts.OhmicContact(device, region, i, edge, False)
	contacts.SchottkyContact(device, region, i, False)
	set_parameter(device=device, name=GetContactBiasName(i), value=0.0)

solve(type="dc", absolute_error=1.0, relative_error=1e-6, maximum_iterations=30)

#add changing bias
recombination.RecombinationFactory.generateModel(device, region, "Langevin")

carrierEquation = {}
for i in (("Electrons", "n"), ("Holes", "p")):
	chargePolarization = "-" if i[0] in "Electrons" else "+"
	chargeCorrection = (i[0], chargePolarization)
	carrier.DensityFactory.generateModel(device, region, "Charge", chargeCorrection)
	mobility.MobilityFactory.generateModel(device, region, "CorrelatedDisorder", i[1])
	transportPolarization = "+" if i[0] in "Electrons" else "-"
	transportCorrection = (i[0], i[1], transportPolarization)
	transport.CurrentFactory.generateModel(device, region, "DriftDiffusion", transportCorrection)
	carrierEquation[i[0]] = equation_builder.EquationBuilder(device, region, i[0], 
																			("Potential", "Electrons", "Holes"),
																			"default")

	carrierEquation[i[0]].addModel(i[0] + "ChargeDensity", "TimeNodeModel")
	carrierEquation[i[0]].addModel(i[0] + "Current", "EdgeModel")
	carrierEquation[i[0]].addModel(i[0] + "Generation", "NodeModel") 
	carrierEquation[i[0]].buildEquation()

potential.SemiconductorExcessCarrierPotential(device, region)
potentialEquation.deleteModel("PotentialIntrinsicCharge", "NodeModel")
potentialEquation.addModel("PotentialNodeCharge", "NodeModel")
potentialEquation.buildEquation()

for i in get_contact_list(device=device):#, ("N_Holes", "N_Electrons")):
	#contacts.OhmicContact(device, region, i, edge, False)
	contacts.SchottkyContact(device, region, i, False)
	set_parameter(device=device, name=GetContactBiasName(i), value=0.0)

set_node_values(device=device, region=region, name="Electrons", init_from="IntrinsicElectrons")
set_node_values(device=device, region=region, name="Holes", init_from="IntrinsicHoles")

#print_node_values(device=device, region=region, name="EquilibriumHoles")
#print_node_values(device=device, region=region, name="Potential")
solve(type="dc", absolute_error=1e10, relative_error=1e-06, maximum_iterations=30)
#print_node_values(device=device, region=region, name="EquilibriumHoles")


current = []
voltage = []
v = 0.0
while v < 5.0:
	set_parameter(device=device, name=GetContactBiasName("bot"), value=v)
	solve(type="dc", absolute_error=1e10, relative_error=1e-07, maximum_iterations=30)
	voltage.append(v)
	e_c = get_contact_current(device=device, contact="bot", equation="ElectronsContinuityEquation")
	h_c = get_contact_current(device=device, contact="bot", equation="HolesContinuityEquation")
	current.append(e_c + h_c)
	PrintCurrents(device, "top")
	PrintCurrents(device, "bot")
	v += .1

#
iv = zip(voltage, current)
with open('iv-curve.csv', 'w') as f:
	writer = csv.writer(f, delimiter=',')
	writer.writerows(iv)
write_devices(file="2D_PPV_diode", device=device,type="vtk")


