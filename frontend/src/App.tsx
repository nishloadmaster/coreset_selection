/**
 * AI Model Improver - Frontend Application
 * 
 * This React application provides a user interface for the AI Model Improver tool.
 * It includes functionality for uploading media files, viewing processed images,
 * and triggering model improvement processes.
 * 
 * @author AI Model Improver Team
 * @version 1.0.0
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

// API Configuration
const API_BASE_URL = 'http://localhost:8050';

// TypeScript Interfaces
interface UploadResponse {
  status: string;
  message: string;
  filename?: string;
  path?: string;
  processing?: string;
  processing_result?: {
    status: string;
    upload_id?: string;
    processed_files?: number;
    files?: string[];
  };
}

interface ImageListResponse {
  images: string[];
}

interface UploadListResponse {
  uploads: string[];
}

interface UploadFolderResponse {
  upload_folders: Array<{
    folder_id: string;
    folder_path: string;
    files: Array<{
      name: string;
      path: string;
      size: number;
    }>;
  }>;
}

interface CurateDataRequest {
  dataset_path: string;
  model_name: string;
  sampling_factor: number;
}

interface CurateDataResponse {
  status: string;
  dataset: string;
  model: string;
  sampling_factor: number;
}

// Component State Interfaces
interface AppState {
  activeTab: 'upload' | 'gallery' | 'curate';
  images: string[];
  uploads: string[];
  uploadFolders: UploadFolderResponse['upload_folders'];
  selectedFile: File | null;
  isUploading: boolean;
  uploadProgress: number;
  showToast: boolean;
  toastMessage: string;
  toastType: 'success' | 'error' | 'info';
  darkMode: boolean;
  curateData: {
    datasetPath: string;
    modelName: string;
    samplingFactor: number;
  };
  selectedImage: string | null;
  showImageModal: boolean;
}

/**
 * Main Application Component
 * 
 * Provides the main interface for the AI Model Improver tool with three main sections:
 * - Upload Data: For uploading and processing zip files
 * - Gallery: For viewing and managing processed images
 * - Curate Data: For triggering model improvement processes
 */
function App() {
  // Application state
  const [state, setState] = useState<AppState>({
    activeTab: 'upload',
    images: [],
    uploads: [],
    uploadFolders: [],
    selectedFile: null,
    isUploading: false,
    uploadProgress: 0,
    showToast: false,
    toastMessage: '',
    toastType: 'info',
    darkMode: false,
    curateData: {
      datasetPath: '',
      modelName: '',
      samplingFactor: 0.5,
    },
    selectedImage: null,
    showImageModal: false,
  });

  // Load initial data on component mount
  useEffect(() => {
    loadImages();
    loadUploads();
    loadUploadFolders();
    
    // Set up auto-refresh for gallery
    const interval = setInterval(() => {
      if (state.activeTab === 'gallery') {
        loadImages();
      }
    }, 10000); // Refresh every 10 seconds

    return () => clearInterval(interval);
  }, [state.activeTab]);

  /**
   * Load processed images from the backend
   */
  const loadImages = async () => {
    try {
      const response = await axios.get<ImageListResponse>(`${API_BASE_URL}/list_images`);
      setState(prev => ({ ...prev, images: response.data.images }));
    } catch (error) {
      console.error('Error loading images:', error);
      showToast('Failed to load images', 'error');
    }
  };

  /**
   * Load uploaded zip files from the backend
   */
  const loadUploads = async () => {
    try {
      const response = await axios.get<UploadListResponse>(`${API_BASE_URL}/list_uploads`);
      setState(prev => ({ ...prev, uploads: response.data.uploads }));
    } catch (error) {
      console.error('Error loading uploads:', error);
    }
  };

  /**
   * Load upload folder information from the backend
   */
  const loadUploadFolders = async () => {
    try {
      const response = await axios.get<UploadFolderResponse>(`${API_BASE_URL}/list_upload_folders`);
      setState(prev => ({ ...prev, uploadFolders: response.data.upload_folders }));
    } catch (error) {
      console.error('Error loading upload folders:', error);
    }
  };

  /**
   * Handle file selection for upload
   */
  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.name.toLowerCase().endsWith('.zip')) {
      setState(prev => ({ ...prev, selectedFile: file }));
    } else {
      showToast('Please select a valid zip file', 'error');
    }
  };

  /**
   * Upload and process the selected zip file
   */
  const handleUpload = async () => {
    if (!state.selectedFile) {
      showToast('Please select a file to upload', 'error');
      return;
    }

    setState(prev => ({ ...prev, isUploading: true, uploadProgress: 0 }));

    try {
      const formData = new FormData();
      formData.append('file', state.selectedFile);

      const response = await axios.post<UploadResponse>(
        `${API_BASE_URL}/upload_zip`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: (progressEvent) => {
            if (progressEvent.total) {
              const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
              setState(prev => ({ ...prev, uploadProgress: progress }));
            }
          },
        }
      );

      if (response.data.status === 'success') {
        showToast(response.data.message, 'success');
        setState(prev => ({ 
          ...prev, 
          selectedFile: null,
          uploadProgress: 0 
        }));
        
        // Refresh data
        loadUploads();
        loadUploadFolders();
        
        // If processing was synchronous, refresh images immediately
        if (response.data.processing_result?.status === 'success') {
          loadImages();
        }
      } else {
        showToast('Upload failed', 'error');
      }
    } catch (error) {
      console.error('Upload error:', error);
      showToast('Upload failed', 'error');
    } finally {
      setState(prev => ({ ...prev, isUploading: false }));
    }
  };

  /**
   * Delete an image from the gallery
   */
  const deleteImage = async (imagePath: string) => {
    try {
      await axios.delete(`${API_BASE_URL}/delete_image?filename=${encodeURIComponent(imagePath)}`);
      showToast('Image deleted successfully', 'success');
      loadImages();
    } catch (error) {
      console.error('Error deleting image:', error);
      showToast('Failed to delete image', 'error');
    }
  };

  /**
   * Delete an uploaded zip file
   */
  const deleteUpload = async (filename: string) => {
    try {
      await axios.delete(`${API_BASE_URL}/delete_upload?filename=${encodeURIComponent(filename)}`);
      showToast('Upload deleted successfully', 'success');
      loadUploads();
    } catch (error) {
      console.error('Error deleting upload:', error);
      showToast('Failed to delete upload', 'error');
    }
  };

  /**
   * Delete an entire upload folder
   */
  const deleteUploadFolder = async (folderId: string) => {
    try {
      await axios.delete(`${API_BASE_URL}/delete_upload_folder?folder_id=${folderId}`);
      showToast('Upload folder deleted successfully', 'success');
      loadUploadFolders();
      loadImages();
    } catch (error) {
      console.error('Error deleting upload folder:', error);
      showToast('Failed to delete upload folder', 'error');
    }
  };

  /**
   * Handle curate data form submission
   */
  const handleCurateData = async () => {
    const { datasetPath, modelName, samplingFactor } = state.curateData;
    
    if (!datasetPath || !modelName) {
      showToast('Please fill in all required fields', 'error');
      return;
    }

    try {
      const response = await axios.post<CurateDataResponse>(`${API_BASE_URL}/improve_model`, {
        dataset_path: datasetPath,
        model_name: modelName,
        sampling_factor: samplingFactor,
      });

      if (response.data.status === 'success') {
        showToast('Model improvement process started successfully', 'success');
      } else {
        showToast('Failed to start model improvement', 'error');
      }
    } catch (error) {
      console.error('Error starting model improvement:', error);
      showToast('Failed to start model improvement', 'error');
    }
  };

  /**
   * Show toast notification
   */
  const showToast = (message: string, type: 'success' | 'error' | 'info') => {
    setState(prev => ({ 
      ...prev, 
      showToast: true, 
      toastMessage: message, 
      toastType: type 
    }));
    
    setTimeout(() => {
      setState(prev => ({ ...prev, showToast: false }));
    }, 3000);
  };

  /**
   * Toggle dark mode
   */
  const toggleDarkMode = () => {
    setState(prev => ({ ...prev, darkMode: !prev.darkMode }));
  };

  /**
   * Open image modal for preview
   */
  const openImageModal = (imagePath: string) => {
    setState(prev => ({ 
      ...prev, 
      selectedImage: imagePath, 
      showImageModal: true 
    }));
  };

  /**
   * Close image modal
   */
  const closeImageModal = () => {
    setState(prev => ({ 
      ...prev, 
      selectedImage: null, 
      showImageModal: false 
    }));
  };

  // Redirect to upload if gallery is empty
  useEffect(() => {
    if (state.activeTab === 'gallery' && state.images.length === 0) {
      showToast('No images found. Please upload some data first.', 'info');
      setState(prev => ({ ...prev, activeTab: 'upload' }));
    }
  }, [state.activeTab, state.images.length]);

  return (
    <div className={`App ${state.darkMode ? 'dark' : ''}`}>
      {/* Header */}
      <header className="header">
        <h1>AI Model Improver</h1>
        <button 
          className="theme-toggle" 
          onClick={toggleDarkMode}
          title={state.darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
        >
          {state.darkMode ? '☀️' : '🌙'}
        </button>
      </header>

      {/* Navigation Tabs */}
      <nav className="nav">
        <button 
          className={`nav-button ${state.activeTab === 'upload' ? 'active' : ''}`}
          onClick={() => setState(prev => ({ ...prev, activeTab: 'upload' }))}
        >
          Upload Data
        </button>
        <button 
          className={`nav-button ${state.activeTab === 'gallery' ? 'active' : ''}`}
          onClick={() => setState(prev => ({ ...prev, activeTab: 'gallery' }))}
        >
          Gallery
        </button>
        <button 
          className={`nav-button ${state.activeTab === 'curate' ? 'active' : ''}`}
          onClick={() => setState(prev => ({ ...prev, activeTab: 'curate' }))}
        >
          Curate Data
        </button>
      </nav>

      {/* Main Content */}
      <main className="main-content">
        {/* Upload Data Tab */}
        {state.activeTab === 'upload' && (
          <div className="upload-section">
            <h2>Upload Data</h2>
            <p>Upload a zip file containing images and videos for processing.</p>
            
            <div className="upload-area">
              <input
                type="file"
                accept=".zip"
                onChange={handleFileSelect}
                className="file-input"
              />
              {state.selectedFile && (
                <p className="selected-file">Selected: {state.selectedFile.name}</p>
              )}
              
              <button 
                onClick={handleUpload}
                disabled={!state.selectedFile || state.isUploading}
                className="upload-button"
              >
                {state.isUploading ? 'Uploading...' : 'Upload & Process'}
              </button>
              
              {state.isUploading && (
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{ width: `${state.uploadProgress}%` }}
                  ></div>
                </div>
              )}
            </div>

            {/* Upload History */}
            <div className="upload-history">
              <h3>Upload History</h3>
              <div className="upload-list">
                {state.uploads.map((upload, index) => (
                  <div key={index} className="upload-item">
                    <span>{upload}</span>
                    <button 
                      onClick={() => deleteUpload(upload)}
                      className="delete-button"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            </div>

            {/* Upload Folders */}
            <div className="upload-folders">
              <h3>Processed Uploads</h3>
              <div className="folder-list">
                {state.uploadFolders.map((folder) => (
                  <div key={folder.folder_id} className="folder-item">
                    <div className="folder-info">
                      <strong>Folder: {folder.folder_id}</strong>
                      <span>{folder.files.length} files</span>
                    </div>
                    <button 
                      onClick={() => deleteUploadFolder(folder.folder_id)}
                      className="delete-button"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Gallery Tab */}
        {state.activeTab === 'gallery' && (
          <div className="gallery-section">
            <h2>Gallery</h2>
            <button 
              onClick={loadImages}
              className="refresh-button"
            >
              Refresh Gallery
            </button>
            
            <div className="image-grid">
              {state.images.map((imagePath, index) => (
                <div key={index} className="image-item">
                  <img 
                    src={`${API_BASE_URL}${imagePath}`} 
                    alt={`Processed image ${index + 1}`}
                    onClick={() => openImageModal(imagePath)}
                    className="gallery-image"
                  />
                  <button 
                    onClick={() => deleteImage(imagePath)}
                    className="delete-button"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
            
            {state.images.length === 0 && (
              <p className="no-images">No images found. Upload some data first.</p>
            )}
          </div>
        )}

        {/* Curate Data Tab */}
        {state.activeTab === 'curate' && (
          <div className="curate-section">
            <h2>Curate Data</h2>
            <p>Configure parameters for model improvement process.</p>
            
            <div className="form-group">
              <label htmlFor="datasetPath">Dataset Path:</label>
              <input
                type="text"
                id="datasetPath"
                value={state.curateData.datasetPath}
                onChange={(e) => setState(prev => ({
                  ...prev,
                  curateData: { ...prev.curateData, datasetPath: e.target.value }
                }))}
                placeholder="Enter dataset path"
                className="form-input"
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="modelName">Model Name:</label>
              <input
                type="text"
                id="modelName"
                value={state.curateData.modelName}
                onChange={(e) => setState(prev => ({
                  ...prev,
                  curateData: { ...prev.curateData, modelName: e.target.value }
                }))}
                placeholder="Enter model name"
                className="form-input"
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="samplingFactor">Sampling Factor (0.0 - 1.0):</label>
              <input
                type="range"
                id="samplingFactor"
                min="0"
                max="1"
                step="0.1"
                value={state.curateData.samplingFactor}
                onChange={(e) => setState(prev => ({
                  ...prev,
                  curateData: { ...prev.curateData, samplingFactor: parseFloat(e.target.value) }
                }))}
                className="form-range"
              />
              <span>{state.curateData.samplingFactor}</span>
            </div>
            
            <button 
              onClick={handleCurateData}
              className="curate-button"
            >
              Curate Data
            </button>
          </div>
        )}
      </main>

      {/* Image Modal */}
      {state.showImageModal && state.selectedImage && (
        <div className="modal-overlay" onClick={closeImageModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={closeImageModal}>×</button>
            <img 
              src={`${API_BASE_URL}${state.selectedImage}`} 
              alt="Full size preview"
              className="modal-image"
            />
          </div>
        </div>
      )}

      {/* Toast Notifications */}
      {state.showToast && (
        <div className={`toast ${state.toastType}`}>
          {state.toastMessage}
        </div>
      )}
    </div>
  );
}

export default App; 