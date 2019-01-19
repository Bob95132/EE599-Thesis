from ds import *
import transport
import contacts
import carrier
import potential
import mobility
import recombination
import thermal

device="PNJunction"
region="MyRegion"

# create grid
create_gmsh_mesh(mesh="diode2d", file="gmsh_diode2d.msh")
add_gmsh_region(mesh="diode2d", gmsh_name="Bulk",    
					region=region, material="PPV")
add_gmsh_contact(mesh="diode2d", gmsh_name="Base",    
						region=region, material="metal", name="top")
add_gmsh_contact(mesh="diode2d", gmsh_name="Emitter", 
						region=region, material="metal", name="bot")
finalize_mesh    (mesh="diode2d")
create_device    (mesh="diode2d", device=device)

# material db
open_db("Materials")

#add potential to create equilibrium conditions
thermal.ThermalVoltage(device, region)
carrier.EquilibriumHolesElectrons(device, region)
carrier.IntrinsicHoleElectronCharge(device, region)

potential.IntrinsicPotential(device, region)

contact.ContactPotential(device, region)

solve(type="dc", absolute_error=1.0, relative_error=1e-12, maximum_iterations=30)

#add changing bias
mobility.GaussianDisorderModel(device, region)
potential.DynamicPotential(device, region)
recombination.LangevinRecombiantion(device, region)
transport.HoleElectronDriftDiffusion(device, region)

contact.ContactHoleElectronContinuity(device, region)

set_node_values(device=device, region=region, name="Electrons", init_from="IntrinsicElectrons")
set_node_values(device=device, region=region, name="Holes", init_from="IntrinsicHoles")

solve(type="dc", absolute_error=1.0, relative_error=1e-12, maximum_iterations=30)

v = 0.0
while v < 5.0:
	set_parameter(device=device, name=GetContactBiasName("top"), value=v)
	solve(type="dc", absolute_error=1e10, relative_error=1e-10, maximum_iterations=30)
	PrintCurrents(device, "top")
	PrintCurrents(device, "bot")
	v += 0.25

#



