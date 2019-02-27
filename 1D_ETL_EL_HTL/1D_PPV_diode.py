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

device="PNJunction"
regions=("ETL", "EL", "HTL")
materials=("Calcium", "OC1C10", "ITO")
interfaces=("ETL-EL", "EL-HTL")
contacts = ("Top", "Bottom")

# material db
open_db(filename="../lib/MaterialDatabase")

# create grid
create_gmsh_mesh(mesh="diode1d", file="1D_3Material2Interface.msh")

for idx, reg in regions:
	add_gmsh_region(mesh="diode1d", gmsh_name=reg,
					region=reg, material=materials[idx])

for idx, interface in interfaces:
	reg0, reg1 = interface.split("-")
	add_gmsh_interface(mesh="diode1d", gmsh_name=interface,
							name=interface, region0=reg0, region1=reg1)

add_gmsh_contact(mesh="diode1d", gmsh_name="Top",    
						region=regions[0], material="metal", name="Top")
add_gmsh_contact(mesh="diode1d", gmsh_name="Bottom", 
						region=regions[1], material="metal", name="Bottom")
finalize_mesh    (mesh="diode1d")
create_device    (mesh="diode1d", device=device)


#conductors
conductorPotentialEquation={}
for reg in (regions[0], regions[2]):
	potential.ElectricField(device, reg)
	carrier.ConductorIntrinsicCarrierPotential(device, reg)
	conductorPotentialEquation[reg] = equation_builder.EquationBuilder(device, region,
																							"Potential",
																							("Potential", "Electrons")
																							"positive")
	conductorPotentialEquation[reg].addModel("PotentialEdgeFlux", "EdgeModel")
	conductorPotentialEquation[reg].addModel("PotentialIntrinsicCharge", "NodeModel")
	conductorPotentialEquation.buildEquation()

#semiconductor	
thermal.ThermalVoltage(device, regions[1])
carrier.IntrinsicCarrier(device, regions[1])
carrier.EquilibriumHolesElectrons(device, regions[1])
carrier.IntrinsicHoleElectronCharge(device, regions[1])

potential.ElectricField(device, regions[1])
potential.SemiconductorIntrinsicCarrierPotential(device, regions[1])

potentialEquation = equation_builder.EquationBuilder(device, regions[1], 
																	"Potential", 
																	("Potential", "Electrons", "Holes"),
																	"log_damp" )

potentialEquation.addModel("PotentialEdgeFlux", "EdgeModel")
potentialEquation.addModel("PotentialIntrinsicCharge", "NodeModel")
potentialEquation.buildEquation()

for i in get_contact_list(device=device):
	contacts.ContactPotential(device, region, i, False)
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
																			"positive")

	carrierEquation[i[0]].addModel(i[0] + "ChargeDensity", "TimeNodeModel")
	carrierEquation[i[0]].addModel(i[0] + "Current", "EdgeModel")
	carrierEquation[i[0]].addModel(i[0] + "Generation", "NodeModel") 
	carrierEquation[i[0]].buildEquation()

potential.SemiconductorExcessCarrierPotential(device, region)
potentialEquation.deleteModel("PotentialIntrinsicCharge", "NodeModel")
potentialEquation.addModel("PotentialNodeCharge", "NodeModel")
potentialEquation.buildEquation()

for i in get_contact_list(device=device):
	contacts.ContactHoleElectronContinuity(device, region, i, False)
	set_parameter(device=device, name=GetContactBiasName(i), value=0.0)

set_node_values(device=device, region=region, name="Electrons", init_from="IntrinsicElectrons")
set_node_values(device=device, region=region, name="Holes", init_from="IntrinsicHoles")

solve(type="dc", absolute_error=1.0, relative_error=1e-12, maximum_iterations=30)

v = 0.0
while v < 5.0:
	set_parameter(device=device, name=GetContactBiasName("top"), value=v)
	solve(type="dc", absolute_error=1e10, relative_error=1e-10, maximum_iterations=30)
	PrintCurrents(device, "top")
	PrintCurrents(device, "bot")
	v += 0.1

#
write_devices(file="2D_PPV_diode", device=device,type="vtk")


