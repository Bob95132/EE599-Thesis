from devsim import *
from util.model_create import *
import transport
import contacts
import carrier
import potential
import mobility
import recombination
import thermal

device="PNJunction"
region="MyRegion"

# material db
open_db(filename="MaterialDatabase")

# create grid
create_gmsh_mesh(mesh="diode2d", file="gmsh_diode2d.msh")
add_gmsh_region(mesh="diode2d", gmsh_name="Bulk",    
					region=region, material="OC1C10")
add_gmsh_contact(mesh="diode2d", gmsh_name="Base",    
						region=region, material="metal", name="top")
add_gmsh_contact(mesh="diode2d", gmsh_name="Emitter", 
						region=region, material="metal", name="bot")
finalize_mesh    (mesh="diode2d")
create_device    (mesh="diode2d", device=device)

#set_parameter(name="debug_level", value="verbose")

#add potential to create equilibrium conditions
thermal.ThermalVoltage(device, region)
carrier.IntrinsicCarrier(device, region)
carrier.EquilibriumHolesElectrons(device, region)
carrier.IntrinsicHoleElectronCharge(device, region)

potential.IntrinsicPotential(device, region)

for i in get_contact_list(device=device):
	contacts.ContactPotential(device, region, i, False)
	set_parameter(device=device, name=GetContactBiasName(i), value=0.0)

solve(type="dc", absolute_error=1.0, relative_error=1e-6, maximum_iterations=30)

#add changing bias
potential.DynamicPotential(device, region)
mobility.GCDFactory(device, region)
recombination.LangevinRecombination(device, region)
transport.HoleElectronDriftDiffusion(device, region)

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
write_devices(file="2D_PPV_diode", device=device,type="devsim_data")


