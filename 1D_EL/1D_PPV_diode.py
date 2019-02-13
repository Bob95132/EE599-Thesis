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
region="MyRegion"

# material db
open_db(filename="../lib/MaterialDatabase")

# create grid
create_gmsh_mesh(mesh="diode1d", file="1D_1Materialv2.msh")
add_gmsh_region(mesh="diode1d", gmsh_name="Bulk",    
					region=region, material="OC1C10")
add_gmsh_contact(mesh="diode1d", gmsh_name="Base",    
						region=region, material="metal", name="top")
add_gmsh_contact(mesh="diode1d", gmsh_name="Emitter", 
						region=region, material="metal", name="bot")
finalize_mesh    (mesh="diode1d")
create_device    (mesh="diode1d", device=device)


#add potential to create equilibrium conditions
thermal.ThermalVoltage(device, region)
carrier.IntrinsicCarrier(device, region)
carrier.EquilibriumHolesElectrons(device, region)
carrier.IntrinsicHoleElectronCharge(device, region)

potential.ElectricField(device, region)
potential.SemiconductorIntrinsicCarrierPotential(device, region)

potentialEquation = equation_builder.EquationBuilder(device, region, 
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
	#mobility.MobilityFactory.generateModel(device, region, "CorrelatedDisorder", i[1])
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


