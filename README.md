# AI Model Improver

This project is a **full-stack local tool** to:

✅ Curate datasets for improving local AI models (with adjustable sampling factor).  
✅ Upload `.zip` files containing large image datasets (supports 50,000+ images, background extraction with stability).  
✅ View and manage uploaded images in a gallery with delete and preview.  
✅ Dark/light mode toggle for comfortable use.  
✅ Clean, responsive frontend with clear tabbed navigation.

---

## Tech Stack

- **Frontend:** React + TypeScript + Vite
- **Backend:** FastAPI + Python
- **Containerization:** Docker (optional)

---

## Features

### Frontend
- Curate Data: Select dataset path, model, sampling factor, and trigger backend training.
- Upload Data: Upload `.zip` files containing images.
- Gallery: Auto-refreshes to display extracted images, with manual refresh button, preview modal, and delete support.
- Responsive UI with structured layout and dark/light toggle.
- Toast notifications when redirecting the user back to Upload if Gallery is empty.

### Backend
- `/improve_model`: Receives dataset path, model name, and sampling factor, returns confirmation (expandable for training integration).
- `/upload_zip`: Streams `.zip` files, extracts on-disk incrementally to avoid memory overload, background extraction with progress logs.
- `/list_images`: Lists extracted images.
- `/delete_image`: Deletes an image from the gallery.
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
pip install fastapi uvicorn python-multipart
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

✅ Upload large `.zip` files (50,000+ images supported) via Upload Data tab.  
✅ Images will be extracted in the background while the frontend remains usable.  
✅ Gallery will auto-refresh every 10 seconds and can be manually refreshed.
✅ Use Curate Data to test local AI model curation workflows.

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
