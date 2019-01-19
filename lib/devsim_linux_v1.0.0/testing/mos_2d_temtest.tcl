# Copyright 2013 Devsim LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set device mymos
load_devices -file mos_2d_dd.msh
#source mos_2d_create.tcl
# TODO: write out mesh, and then read back in as separate test
source mos_2d_physics.tcl
#setMaterialParameters $device gate
#setMaterialParameters $device bulk
#
#
#setMaterialParameters $device gate
#setMaterialParameters $device bulk
#setMaterialParameters $device $region
#
#createSolution $device gate  Potential
#createSolution $device bulk  Potential
#createSolution $device oxide Potential
#
#

#createSolution $device gate Potential
#createSolution $device bulk Potential
#createSolution $device oxide Potential

setSiliconParameters $device gate
setSiliconParameters $device bulk
setOxideParameters $device oxide

createSiliconPotentialOnly $device bulk
createSiliconPotentialOnly $device gate

createOxidePotentialOnly $device oxide

createSiliconPotentialOnlyContact $device gate gate
createSiliconPotentialOnlyContact $device bulk drain
createSiliconPotentialOnlyContact $device bulk source
createSiliconPotentialOnlyContact $device bulk body

createSiliconOxideInterface $device bulk_oxide
createSiliconOxideInterface $device gate_oxide

#solve -type dc -absolute_error 1.0e-13 -relative_error 1e-12 -maximum_iterations 30
#solve -type dc -absolute_error 1.0e-13 -relative_error 1e-12 -maximum_iterations 30

#write_devices -file mos_2d_potentialonly.flps -type floops
#write_devices -file mos_2d_potentialonly -type vtk

#createSolution $device gate Electrons
#createSolution $device gate Holes
#set_node_values -device $device -region gate -name Electrons -init_from IntrinsicElectrons
#set_node_values -device $device -region gate -name Holes     -init_from IntrinsicHoles
createSiliconDriftDiffusion $device gate
createSiliconDriftDiffusionAtContact $device gate gate

#createSolution $device bulk Electrons
#createSolution $device bulk Holes
#set_node_values -device $device -region bulk -name Electrons -init_from IntrinsicElectrons
#set_node_values -device $device -region bulk -name Holes     -init_from IntrinsicHoles
createSiliconDriftDiffusion $device bulk


createSiliconDriftDiffusionAtContact $device bulk drain
createSiliconDriftDiffusionAtContact $device bulk source
createSiliconDriftDiffusionAtContact $device bulk body
solve -type dc -absolute_error 1.0e30 -relative_error 1e-5 -maximum_iterations 30

element_from_edge_model -edge_model ElectricField -device $device -region bulk
element_from_edge_model -edge_model ElectricField -derivative Potential -device $device -region bulk
debug_triangle_models -device $device -region bulk
#write_devices -file mos_2d_dd.flps -type floops
#write_devices -file mos_2d_dd -type vtk

set y [get_node_model_values -device $device -region bulk -name Potential]
set tcl_precision 15
puts [lindex $y 2183]
puts [lindex $y 2247]
puts [lindex $y 2248]

# test implicit conversion
edge_model         -device $device -region gate -name "foo" -equation "1;";
edge_model         -device $device -region gate -name "foo:Potential@n0" -equation "1;";
edge_model         -device $device -region gate -name "foo:Potential@n1" -equation "-1;";
#puts [element_model -device $device -region gate -name "bar" -equation "foo:Potential@en0;"]
# This currently requires an unknown model to be created as the result of the derivative of a known model name
puts [element_model -device $device -region gate -name "bar:Potential@en0" -equation "diff(foo,Potential@en0);"]
puts [lindex  [get_element_model_values -device $device -region gate -name "bar:Potential@en0"] 0]
puts [element_model -device $device -region gate -name "bar:Potential@en1" -equation "foo:Potential@en1;"]
puts [lindex  [get_element_model_values -device $device -region gate -name "bar:Potential@en1"] 0]

