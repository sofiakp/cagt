import numpy as np

from src.utils import MatrixMap

def normalize(data):
	ids = data.ids
	data = data.data
	norm_data = np.zeros(data.shape)
	
	for row in range(data.shape[0]):
		std = np.std(data[row,:])
		avg = np.mean(data[row,:])
		if std < .001:
			norm_data[row,:] = np.array(data[row,:])-avg
		else:
			norm_data[row,:] = (np.array(data[row,:])-avg)/std
	
	return MatrixMap(norm_data, ids)
