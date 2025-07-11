import axios from 'axios';

export const improveModel = async (datasetPath: string, modelName: string, samplingFactor: number) => {
  const response = await axios.post('/improve_model', {
    dataset_path: datasetPath,
    model_name: modelName,
    sampling_factor: samplingFactor
  });
  return response.data;
};

export const uploadZip = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await axios.post('/upload_zip', formData);
  return response.data;
};

export const listImages = async () => {
  const response = await axios.get('/list_images');
  return response.data;
};

export const deleteImage = async (filename: string) => {
  const response = await axios.delete(`/delete_image?filename=${filename}`);
  return response.data;
};