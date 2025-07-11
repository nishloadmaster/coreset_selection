import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
    const [activeTab, setActiveTab] = useState<'data_management' | 'gallery'>('data_management');
    const [darkMode, setDarkMode] = useState(true);
    const [datasetPath, setDatasetPath] = useState('');
    const [modelName, setModelName] = useState('Model1');
    const [samplingFactor, setSamplingFactor] = useState(0.5);
    const [labels, setLabels] = useState('');
    const [uploadModelName, setUploadModelName] = useState('Model1');
    const [uploadLabels, setUploadLabels] = useState<string[]>([]);
    const [newLabel, setNewLabel] = useState('');
    const [uploadSamplingFactor, setUploadSamplingFactor] = useState(0.5);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [images, setImages] = useState<string[]>([]);
    const [previewImage, setPreviewImage] = useState<string | null>(null);
    const [showUploadPopup, setShowUploadPopup] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [uploadStatus, setUploadStatus] = useState('');
    const [selectedFile, setSelectedFile] = useState<File | null>(null);

    useEffect(() => {
        let interval: ReturnType<typeof setInterval>;
        if (activeTab === 'gallery') {
            fetchImages();
            interval = setInterval(fetchImages, 10000);
        }
        return () => clearInterval(interval);
    }, [activeTab]);

    const fetchImages = async () => {
        try {
            const res = await axios.get('/list_images');
            setImages(res.data.images);
        } catch (error) {
            console.error('Error fetching images:', error);
        }
    };

    const handleSubmit = async () => {
        setLoading(true);
        try {
            // Parse labels string into array of strings
            const labelsList = labels
                .split(',')
                .map(label => label.trim())
                .filter(label => label.length > 0);

            const response = await axios.post('/improve_model', {
                dataset_path: datasetPath,
                model_name: modelName,
                sampling_factor: samplingFactor,
                labels: labelsList
            });
            setResult(response.data);
        } catch (error) {
            console.error(error);
            alert('Error curating data');
        } finally {
            setLoading(false);
        }
    };

    const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
        const files = event.target.files;
        if (files && files[0]) {
            setSelectedFile(files[0]);
        }
    };

    const handleZipUpload = async () => {
        if (!selectedFile) {
            alert('Please select a file first');
            return;
        }

        setShowUploadPopup(true);
        setUploadProgress(0);
        setUploadStatus('Preparing upload...');

        try {
            const formData = new FormData();
            formData.append('file', selectedFile);
            formData.append('model_name', uploadModelName);
            formData.append('labels', uploadLabels.join(','));
            formData.append('sampling_factor', uploadSamplingFactor.toString());

            // Debug: Log what we're sending
            console.log('Frontend sending labels:', uploadLabels);
            console.log('Frontend sending labels string:', uploadLabels.join(','));
            console.log('FormData contents:');
            for (let [key, value] of formData.entries()) {
                console.log(`${key}: ${value}`);
            }

            // Simulate upload progress
            const progressInterval = setInterval(() => {
                setUploadProgress(prev => {
                    if (prev >= 90) {
                        clearInterval(progressInterval);
                        return prev;
                    }
                    return prev + 10;
                });
            }, 200);

            setUploadStatus('Uploading file...');

            const response = await axios.post('/upload_zip', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
                onUploadProgress: (progressEvent) => {
                    if (progressEvent.total) {
                        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                        setUploadProgress(progress);
                    }
                }
            });

            clearInterval(progressInterval);
            setUploadProgress(100);
            setUploadStatus('Processing dataset...');

            // Simulate processing time
            setTimeout(() => {
                setUploadStatus('Dataset processing completed!');
                setTimeout(() => {
                    setShowUploadPopup(false);
                    setUploadProgress(0);
                    setUploadStatus('');
                    
                    // Reset all form state
                    resetForm();
                    
                    alert('Zip file uploaded successfully and will be processed.');
                }, 1000);
            }, 2000);

        } catch (error) {
            console.error(error);
            setUploadStatus('Upload failed');
            setTimeout(() => {
                setShowUploadPopup(false);
                setUploadProgress(0);
                setUploadStatus('');
            }, 2000);
            alert('Error uploading zip file');
        }
    };

    const addLabel = () => {
        if (newLabel.trim() && !uploadLabels.includes(newLabel.trim())) {
            setUploadLabels([...uploadLabels, newLabel.trim()]);
            setNewLabel('');
        }
    };

    const removeLabel = (index: number) => {
        setUploadLabels(uploadLabels.filter((_, i) => i !== index));
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') {
            addLabel();
        }
    };

    const resetForm = () => {
        setSelectedFile(null);
        setUploadLabels([]);
        setNewLabel('');
        setUploadModelName('Model1');
        setUploadSamplingFactor(0.5);
        
        // Reset the file input
        const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
        if (fileInput) {
            fileInput.value = '';
        }
    };

    const handleDeleteImage = async (filename: string) => {
        try {
            await axios.delete(`/delete_image?filename=${encodeURIComponent(filename)}`);
            setImages(prev => prev.filter(img => !img.endsWith(filename)));
        } catch (error) {
            console.error(error);
            alert('Error deleting image');
        }
    };

    const themeStyles = {
        backgroundColor: darkMode ? '#121212' : '#f0f0f0',
        color: darkMode ? '#e0e0e0' : '#121212',
        minHeight: '100vh',
        padding: '2rem',
        fontFamily: 'sans-serif',
        transition: 'background-color 0.3s, color 0.3s'
    };

    const inputStyle = {
        width: '25%',
        padding: '0.5rem',
        marginBottom: '1rem',
        borderRadius: '4px',
        display: 'block'
    };

    const tabButtonStyle = (tab: string) => ({
        padding: '0.4rem 0.8rem',
        border: 'none',
        borderRadius: '4px',
        cursor: 'pointer',
        fontWeight: 'bold',
        transition: 'background-color 0.3s, transform 0.2s',
        backgroundColor: activeTab === tab ? '#90caf9' : '#1e1e1e',
        color: activeTab === tab ? '#000' : '#e0e0e0'
    });

    const smallButtonStyle = {
        padding: '0.4rem 0.8rem',
        backgroundColor: '#90caf9',
        color: '#000',
        border: 'none',
        borderRadius: '4px',
        cursor: loading ? 'not-allowed' : 'pointer',
        fontWeight: 'bold',
        width: '25%',
        display: 'block',
        marginBottom: '1rem'
    };

    const sectionStyle = {
        backgroundColor: darkMode ? '#2d2d2d' : '#ffffff',
        padding: '1.5rem',
        borderRadius: '8px',
        marginBottom: '2rem',
        border: `1px solid ${darkMode ? '#555' : '#e9ecef'}`
    };

    const sectionTitleStyle = {
        color: darkMode ? '#ffffff' : '#333',
        marginBottom: '1rem',
        fontSize: '1.25rem',
        borderBottom: `2px solid ${darkMode ? '#90caf9' : '#667eea'}`,
        paddingBottom: '0.5rem'
    };

    const uploadButtonStyle = {
        padding: '0.4rem 0.8rem',
        backgroundColor: '#28a745',
        color: 'white',
        border: 'none',
        borderRadius: '4px',
        cursor: selectedFile ? 'pointer' : 'not-allowed',
        fontWeight: 'bold',
        width: '25%',
        display: 'block',
        marginBottom: '1rem',
        opacity: selectedFile ? 1 : 0.6
    };

    const popupOverlayStyle = {
        position: 'fixed' as const,
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0,0,0,0.8)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000
    };

    const popupContentStyle = {
        backgroundColor: darkMode ? '#2d2d2d' : '#ffffff',
        padding: '2rem',
        borderRadius: '8px',
        minWidth: '400px',
        textAlign: 'center' as const,
        border: `1px solid ${darkMode ? '#555' : '#ddd'}`
    };

    const progressBarStyle = {
        width: '100%',
        height: '20px',
        backgroundColor: darkMode ? '#555' : '#f0f0f0',
        borderRadius: '10px',
        overflow: 'hidden',
        margin: '1rem 0'
    };

    const progressFillStyle = {
        height: '100%',
        backgroundColor: '#28a745',
        width: `${uploadProgress}%`,
        transition: 'width 0.3s ease'
    };

    return (
        <div style={themeStyles}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h1 style={{ color: '#90caf9' }}>AI Model Improver</h1>
                <button onClick={() => setDarkMode(!darkMode)} style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '1.5rem', color: darkMode ? '#fdd835' : '#212121' }}>{darkMode ? '🌙' : '🌑'}</button>
            </div>

            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
                <button style={tabButtonStyle('data_management')} onClick={() => setActiveTab('data_management')}>Data Management</button>
                <button style={tabButtonStyle('gallery')} onClick={() => setActiveTab('gallery')}>Gallery</button>
            </div>

            {activeTab === 'data_management' && (
                <div>
                    <h2>Data Management</h2>
                    <p>Upload data and configure model improvement parameters.</p>
                    
                    {/* Upload Section */}
                    <div style={sectionStyle}>
                        <h3 style={sectionTitleStyle}>Upload Data</h3>
                        <p>Upload a zip file containing images and videos for processing.</p>
                        <input 
                            type='file' 
                            accept='.zip' 
                            onChange={handleFileSelect} 
                            style={inputStyle}
                            key={selectedFile ? 'file-selected' : 'file-empty'}
                        />
                        {selectedFile && (
                            <p style={{ color: '#28a745', marginBottom: '1rem' }}>
                                Selected: {selectedFile.name}
                            </p>
                        )}
                        
                        <select value={uploadModelName} onChange={e => setUploadModelName(e.target.value)} style={inputStyle}>
                            <option value='Model1'>YOLO v8 COCO</option>
                            <option value='Model2'>RESNET50</option>
                            <option value='Model3'>CLIP</option>
                        </select>
                        
                        <input 
                            type='text' 
                            value={newLabel} 
                            onChange={e => setNewLabel(e.target.value)} 
                            placeholder='Enter a label'
                            onKeyPress={handleKeyPress}
                            style={inputStyle} 
                        />
                        <button 
                            onClick={addLabel}
                            disabled={!newLabel.trim()}
                            style={{
                                ...smallButtonStyle,
                                width: 'auto',
                                marginLeft: '0.5rem',
                                padding: '0.4rem 0.8rem',
                                backgroundColor: newLabel.trim() ? '#28a745' : '#ccc'
                            }}
                        >
                            Add Label
                        </button>
                        
                        {uploadLabels.length > 0 && (
                            <div style={{ marginTop: '1rem', marginBottom: '1rem' }}>
                                <p style={{ color: darkMode ? '#ccc' : '#666', marginBottom: '0.5rem' }}>Labels:</p>
                                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                                    {uploadLabels.map((label, index) => (
                                        <div 
                                            key={index}
                                            style={{
                                                backgroundColor: '#667eea',
                                                color: 'white',
                                                padding: '0.25rem 0.5rem',
                                                borderRadius: '4px',
                                                display: 'flex',
                                                alignItems: 'center',
                                                gap: '0.25rem',
                                                fontSize: '0.875rem'
                                            }}
                                        >
                                            <span>{label}</span>
                                            <button 
                                                onClick={() => removeLabel(index)}
                                                style={{
                                                    background: 'none',
                                                    border: 'none',
                                                    color: 'white',
                                                    cursor: 'pointer',
                                                    fontSize: '0.75rem',
                                                    padding: '0',
                                                    marginLeft: '0.25rem'
                                                }}
                                            >
                                                ×
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                        
                        <input 
                            type='number' 
                            min={0} 
                            max={1} 
                            step={0.01} 
                            value={uploadSamplingFactor} 
                            onChange={e => setUploadSamplingFactor(parseFloat(e.target.value))} 
                            placeholder='Sampling factor (0.0-1.0)'
                            style={inputStyle} 
                        />
                        
                        <button 
                            onClick={handleZipUpload} 
                            disabled={!selectedFile}
                            style={uploadButtonStyle}
                        >
                            Upload & Process
                        </button>
                    </div>
                </div>
            )}

            {activeTab === 'gallery' && (
                <div>
                    <h2>Gallery</h2>
                    <button onClick={fetchImages} style={smallButtonStyle}>Refresh Gallery</button>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '1rem', marginTop: '1rem' }}>
                        {images.map((src, index) => {
                            const filename = src.split('/').pop() || '';
                            return (
                                <div key={index} style={{ position: 'relative', backgroundColor: '#1e1e1e', borderRadius: '8px' }}>
                                    <img src={src} alt={filename} onClick={() => setPreviewImage(src)} style={{ width: '100%', borderRadius: '8px', cursor: 'pointer' }} />
                                    <button onClick={() => handleDeleteImage(filename)} style={{ position: 'absolute', top: '5px', right: '5px', backgroundColor: 'red', color: 'white', border: 'none', borderRadius: '50%', cursor: 'pointer' }}>×</button>
                                </div>
                            );
                        })}
                    </div>
                    {previewImage && (
                        <div onClick={() => setPreviewImage(null)} style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
                            <img src={previewImage} alt='Preview' style={{ maxHeight: '80%', maxWidth: '80%', borderRadius: '8px' }} />
                        </div>
                    )}
                </div>
            )}

            {/* Upload Popup */}
            {showUploadPopup && (
                <div style={popupOverlayStyle}>
                    <div style={popupContentStyle}>
                        <h3 style={{ color: darkMode ? '#ffffff' : '#333', marginBottom: '1rem' }}>
                            {uploadStatus}
                        </h3>
                        <div style={progressBarStyle}>
                            <div style={progressFillStyle}></div>
                        </div>
                        <p style={{ color: darkMode ? '#ccc' : '#666', marginTop: '1rem' }}>
                            {uploadProgress}% Complete
                        </p>
                        {uploadProgress === 100 && uploadStatus.includes('completed') && (
                            <div style={{ marginTop: '1rem', color: '#28a745' }}>
                                ✓ Processing finished successfully!
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}

export default App;
