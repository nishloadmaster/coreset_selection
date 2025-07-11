# Data Curator

This project is a **full-stack local tool** to:

✅ Curate datasets for improving local AI models (with adjustable sampling factor).  
✅ Upload `.zip` files containing **images and videos**, with automatic frame extraction from videos.  
✅ Supports **large datasets (50,000+ images/frames) with background extraction and stability**.  
✅ View and manage uploaded images and extracted frames in a gallery with delete and preview.  
✅ Dark/light mode toggle for comfortable use.  
✅ Clean, responsive frontend with clear tabbed navigation and toast notifications.

---

## Tech Stack

- **Frontend:** React + TypeScript + Vite
- **Backend:** FastAPI + Python
- **Video Frame Extraction:** `imageio` (replacing `opencv-python` for stability)
- **Containerization:** Docker (optional)

---

## Features

### Frontend
- **Curate Data:** Select dataset path, model, sampling factor, and trigger backend training.
- **Upload Data:** Upload `.zip` files containing **images and videos**.
- **Gallery:** Auto-refreshes to display extracted images and frames, with manual refresh, preview modal, and delete support.
- Responsive UI with structured layout and dark/light toggle.
- Toast notifications when redirecting the user back to Upload if Gallery is empty.

### Backend
- `/improve_model`: Receives dataset path, model name, and sampling factor, returns confirmation (expandable for training integration).
- `/upload_zip`: Streams `.zip` files, extracts on-disk incrementally to avoid memory overload, **uses `MediaProcessor` to extract frames from videos**, and logs progress.
- `/list_images`: Lists extracted images and frames.
- `/delete_image`: Deletes an image/frame from the gallery.
- Serves images via `/static/images` for frontend gallery use.

---

## Installation

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

### 2️⃣ Setup Backend

#### With Python directly
- Ensure you have **Python 3.10+**.
- Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
- Install dependencies:
```bash
pip install -r requirements.txt
```
- Run the backend:
```bash
uvicorn main:app --reload
```

#### With Docker (Optional)
If you want consistent environment handling:
```bash
docker build -t ai-model-improver-backend .
docker run -p 8000:8000 ai-model-improver-backend
```

### 3️⃣ Setup Frontend

- Ensure you have **Node.js (18+) and npm** installed.
- Navigate to the frontend directory (or project root if unified):
```bash
npm install
```
- Start the frontend:
```bash
npm run dev
```
- Visit [http://localhost:5173](http://localhost:5173) in your browser.

---

## Usage Notes

✅ Upload `.zip` files with images and videos; videos will have frames extracted automatically for use in the gallery and pipelines.  
✅ Handles large `.zip` uploads while the frontend remains usable.  
✅ Gallery auto-refreshes every 10 seconds, with manual refresh button available.  
✅ Curate Data section for local AI model improvement workflows.  
✅ Dark/light toggle for comfortable long work sessions.

---

## Directory Structure

```
project-root/
├── frontend/ (or unified structure)
│   ├── src/
│   │   ├── App.tsx
│   │   └── ...
│   ├── package.json
│   └── vite.config.ts
├── main.py
├── media_processor.py
├── requirements.txt
├── static/
│   └── images/
├── .gitignore
└── README.md
```

---

## .gitignore
Ensure you add:
```
node_modules/
.env
__pycache__/
*.pyc
*.pyo
*.pyd
env/
venv/
.venv/
.DS_Store
```
to your `.gitignore` to keep your repository clean.

---

## Contributing
Feel free to fork, contribute, and create pull requests for improvements or additional features.

---

## License
This project is under the MIT License.

---
