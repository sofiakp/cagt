import numpy as np

def normalize(data):
	norm_data = np.zeros(data.shape)
	
	for row in range(data.shape[0]):
		std = np.std(data[row,:])
		avg = np.mean(data[row,:])
		if std < .001:
			norm_data[row,:] = np.array(data[row,:])-avg
		else:
			norm_data[row,:] = (np.array(data[row,:])-avg)/std
	
	return norm_data
