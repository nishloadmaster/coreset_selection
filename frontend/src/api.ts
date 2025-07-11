import axios from 'axios';

export const improveModel = async (datasetPath: string, modelName: string, samplingFactor: number) => {
  const response = await axios.post('/improve_model', {
    dataset_path: datasetPath,
    model_name: modelName,
    sampling_factor: samplingFactor
  });
  return response.data;
};