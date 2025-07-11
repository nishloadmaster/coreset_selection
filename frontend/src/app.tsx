import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
    const [activeTab, setActiveTab] = useState<'curate' | 'upload' | 'gallery'>('curate');
    const [darkMode, setDarkMode] = useState(true);
    const [datasetPath, setDatasetPath] = useState('');
    const [modelName, setModelName] = useState('Model1');
    const [samplingFactor, setSamplingFactor] = useState(0.5);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [images, setImages] = useState<string[]>([]);
    const [previewImage, setPreviewImage] = useState<string | null>(null);

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
            const response = await axios.post('/improve_model', {
                dataset_path: datasetPath,
                model_name: modelName,
                sampling_factor: samplingFactor
            });
            setResult(response.data);
        } catch (error) {
            console.error(error);
            alert('Error curating data');
        } finally {
            setLoading(false);
        }
    };

    const handleZipUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const files = event.target.files;
        if (!files) return;
        const formData = new FormData();
        formData.append('file', files[0]);
        try {
            await axios.post('/upload_zip', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            alert('Zip file uploaded successfully and will be processed.');
        } catch (error) {
            console.error(error);
            alert('Error uploading zip file');
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

    return (
        <div style={themeStyles}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h1 style={{ color: '#90caf9' }}>AI Model Improver</h1>
                <button onClick={() => setDarkMode(!darkMode)} style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '1.5rem', color: darkMode ? '#fdd835' : '#212121' }}>{darkMode ? '🌙' : '🌑'}</button>
            </div>

            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
                <button style={tabButtonStyle('curate')} onClick={() => setActiveTab('curate')}>Curate Data</button>
                <button style={tabButtonStyle('upload')} onClick={() => setActiveTab('upload')}>Upload Data (.zip)</button>
                <button style={tabButtonStyle('gallery')} onClick={() => setActiveTab('gallery')}>Gallery</button>
            </div>

            {activeTab === 'curate' && (
                <div>
                    <h2>Curate Data</h2>
                    <select value={datasetPath} onChange={e => setDatasetPath(e.target.value)} style={inputStyle}>
                        <option value=''>Select Dataset</option>
                        <option value='/path/to/dataset1'>Dataset 1</option>
                        <option value='/path/to/dataset2'>Dataset 2</option>
                    </select>
                    <select value={modelName} onChange={e => setModelName(e.target.value)} style={inputStyle}>
                        <option value='Model1'>Model1</option>
                        <option value='Model2'>Model2</option>
                    </select>
                    <input type='number' min={0} max={1} step={0.01} value={samplingFactor} onChange={e => setSamplingFactor(parseFloat(e.target.value))} style={inputStyle} />
                    <button onClick={handleSubmit} disabled={loading} style={smallButtonStyle}>{loading ? 'Processing...' : 'Curate Data'}</button>
                    {result && <pre style={{ marginTop: '1rem', backgroundColor: '#1e1e1e', padding: '1rem', borderRadius: '4px', overflowX: 'auto', width: '25%' }}>{JSON.stringify(result, null, 2)}</pre>}
                </div>
            )}

            {activeTab === 'upload' && (
                <div>
                    <h2>Upload Data (.zip)</h2>
                    <input type='file' accept='.zip' onChange={handleZipUpload} style={inputStyle} />
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
        </div>
    );
}

export default App;
