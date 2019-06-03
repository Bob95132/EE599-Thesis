
from devsim import *

from util.model import *
from util.model_create import *
from util.model_factory import *

class RegionLength(NodeModel):
	
	def __init__(self, device, region):
		dimension = get_dimension(device=device)
		modelName = "RegionLength_"
		directions = ["x", "y", "z"]
		for d in range(0, dimension):
			direction = directions[d]
			nodeValues = get_node_model_values(device=device, region=region, name=direction)
			nodeValues = sorted(nodeValues)
			distance = nodeValues[-1] - nodeValues[0]
			CreateSolution(device=device, region=region, name=modelName+direction)
			set_node_value(device=device, region=region, name=modelName+direction, value=distance)

