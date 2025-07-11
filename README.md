# AI Model Improver - CoreSet Selection Tool

A **full-stack web application** for curating datasets and improving AI models through intelligent data selection and processing.

## 🚀 Features

### Core Functionality
- ✅ **Dataset Curation**: Upload and process large datasets with adjustable sampling factors
- ✅ **Media Processing**: Automatic extraction of frames from videos and image processing
- ✅ **Gallery Management**: View, preview, and manage processed images with delete functionality
- ✅ **Model Improvement**: Interface for AI model training with custom parameters
- ✅ **Responsive UI**: Dark/light mode toggle with modern, clean interface

### Technical Features
- **Large Dataset Support**: Handles 50,000+ images/frames with background processing
- **Video Frame Extraction**: Automatic frame extraction from videos using `imageio-ffmpeg`
- **Real-time Updates**: Auto-refreshing gallery with manual refresh options
- **Production Ready**: Docker containerization with proper error handling

---

## 🛠️ Tech Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for fast development and building
- **Axios** for API communication
- **Modern CSS** with responsive design

### Backend
- **FastAPI** with Python 3.10+
- **Uvicorn** ASGI server
- **Docker** containerization
- **Media Processing**: `imageio-ffmpeg` for video frame extraction

---

## 📦 Installation & Setup

### Prerequisites
- **Docker** and **Docker Compose** (recommended)
- **Node.js 18+** and **npm** (for frontend development)
- **Python 3.10+** (for backend development)

### Quick Start (Docker - Recommended)

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd coreset_selection
   ```

2. **Start the backend**
   ```bash
   docker-compose up --build -d
   ```

3. **Start the frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Access the application**
   - Frontend: http://localhost:3058
   - Backend API: http://localhost:8050

### Manual Setup (Development)

#### Backend Setup
```bash
cd coreset_selection/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --host 0.0.0.0 --port 8050 --reload
```

#### Frontend Setup
```bash
cd coreset_selection/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

---

## 🏗️ Project Structure

```
coreset_selection/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── media_processor.py      # Video/image processing logic
│   ├── train_utils.py          # Training utilities
│   ├── requirements.txt        # Python dependencies
│   ├── Dockerfile             # Backend container
│   ├── uploads/               # Uploaded zip files (gitignored)
│   └── static/
│       └── images/            # Processed images (gitignored)
├── frontend/
│   ├── src/
│   │   ├── App.tsx           # Main React component
│   │   └── main.tsx          # React entry point
│   ├── package.json          # Node.js dependencies
│   └── vite.config.mts       # Vite configuration
├── docker-compose.yml         # Docker orchestration
├── .gitignore                # Git ignore rules
└── README.md                 # This file
```

---

## 🔧 API Endpoints

### Upload & Processing
- `POST /upload_zip` - Upload and process zip files
  - Query params: `process_sync` (boolean) for immediate processing
- `GET /list_uploads` - List uploaded zip files
- `GET /list_upload_folders` - List processed upload folders
- `DELETE /delete_upload` - Delete uploaded zip file
- `DELETE /delete_upload_folder` - Delete entire upload folder

### Gallery Management
- `GET /list_images` - List all processed images
- `DELETE /delete_image` - Delete specific image

### Model Training
- `POST /improve_model` - Trigger model improvement with parameters

---

## 🎯 Usage Guide

### 1. Upload Data
1. Navigate to the "Upload Data" tab
2. Select a `.zip` file containing images and/or videos
3. The system will automatically:
   - Extract all images
   - Extract frames from videos (1 frame per second, max 100 per video)
   - Organize files in unique folders

### 2. View Gallery
1. Navigate to the "Gallery" tab
2. View all processed images and video frames
3. Click on images for full-size preview
4. Use the delete button (×) to remove unwanted files

### 3. Curate Data
1. Navigate to the "Curate Data" tab
2. Select dataset path and model parameters
3. Adjust sampling factor (0.0-1.0)
4. Click "Curate Data" to start processing

---

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:
```env
# Backend Configuration
BACKEND_PORT=8050
BACKEND_HOST=0.0.0.0

# Frontend Configuration
FRONTEND_PORT=3058
VITE_API_BASE_URL=http://localhost:8050
```

### Docker Configuration
The `docker-compose.yml` file includes:
- Volume mappings for persistent storage
- Port configurations
- Environment variables

---

## 🚀 Production Deployment

### Docker Production
```bash
# Build and run in production mode
docker-compose -f docker-compose.prod.yml up -d
```

### Manual Production
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8050

# Frontend
cd frontend
npm run build
npm run preview
```

---

## 🐛 Troubleshooting

### Common Issues

**Backend not starting:**
```bash
# Check Docker logs
docker-compose logs backend

# Check if port is available
netstat -tlnp | grep 8050
```

**Frontend not connecting to backend:**
- Verify backend is running on port 8050
- Check Vite proxy configuration in `vite.config.mts`
- Ensure CORS is properly configured

**Video processing not working:**
```bash
# Verify ffmpeg is installed in container
docker exec coreset_selection-backend-1 ffmpeg -version

# Check imageio-ffmpeg installation
docker exec coreset_selection-backend-1 python3 -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_version())"
```

---

## 📝 Development

### Code Style
- **Python**: Follow PEP 8 guidelines
- **TypeScript**: Use strict mode and proper typing
- **React**: Use functional components with hooks

### Adding New Features
1. Create feature branch: `git checkout -b feature/new-feature`
2. Implement changes with proper documentation
3. Test thoroughly
4. Submit pull request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section above
- Review the API documentation

---

**Happy coding! 🎉**
