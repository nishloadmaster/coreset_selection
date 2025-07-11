# Combined Upload & Curate Functionality

## Overview

The AI Model Improver now includes a combined "Upload & Curate" workflow that allows users to upload data and immediately trigger the curation process in a single operation. This streamlines the workflow and reduces the number of steps required to process and curate data.

## New Features

### 1. Combined Upload & Curate Endpoint

**Backend Endpoint**: `POST /upload_and_curate`

This endpoint combines the upload and curate functionality into a single API call:

- **File Upload**: Accepts zip files containing images and videos
- **Processing**: Extracts and processes media files
- **Curation**: Immediately triggers model improvement with the processed data

#### Parameters:
- `file` (UploadFile): The zip file to upload
- `model_name` (str): Name of the model to improve
- `sampling_factor` (float): Sampling factor for data selection (0.0-1.0)
- `process_sync` (bool): If True, processes immediately and returns results

#### Response:
```json
{
  "status": "success",
  "message": "Zip file uploaded, processed, and curation triggered successfully.",
  "filename": "dataset.zip",
  "path": "/uploads/dataset.zip",
  "processing_result": {
    "status": "success",
    "upload_id": "uuid",
    "processed_files": 150,
    "output_folder": "/static/images/uuid"
  },
  "curation_result": {
    "status": "success",
    "dataset": "/static/images/uuid",
    "model": "yolov8n",
    "sampling_factor": 0.5
  },
  "workflow": "upload_and_curate_sync"
}
```

### 2. Frontend Integration

**New Tab**: "Upload & Curate"

The frontend now includes a dedicated tab that provides:

- **File Selection**: Upload zip files containing media data
- **Curation Parameters**: Configure model name and sampling factor
- **Combined Workflow**: Single button to upload, process, and curate
- **Progress Tracking**: Real-time progress indication
- **Workflow Information**: Clear instructions and workflow steps

## Usage

### Step-by-Step Workflow

1. **Navigate to "Upload & Curate" tab**
2. **Select a zip file** containing images and videos
3. **Configure curation parameters**:
   - Model Name: Enter the name of the model to improve
   - Sampling Factor: Set the data selection ratio (0.0-1.0)
4. **Click "Upload & Curate"** to start the combined process
5. **Monitor progress** through the progress bar
6. **View results** in the Gallery tab

### Workflow Information

The system will:
- ✅ Upload your zip file containing images and videos
- ✅ Configure model name and sampling factor
- ✅ Process the data and extract media files
- ✅ Immediately trigger the model improvement process
- ✅ Make results available in the Gallery tab

## Technical Implementation

### Backend Changes

1. **New Endpoint**: `/upload_and_curate`
   - Combines file upload with immediate processing
   - Triggers curation process automatically
   - Supports both synchronous and asynchronous processing

2. **Enhanced Processing**:
   - Validates file type and parameters
   - Processes zip files using MediaProcessor
   - Triggers model improvement with processed data
   - Returns comprehensive status information

### Frontend Changes

1. **New Tab**: "Upload & Curate"
   - Dedicated interface for combined workflow
   - Form validation and error handling
   - Progress tracking and user feedback

2. **Enhanced State Management**:
   - New state for upload and curate data
   - Combined form handling
   - Progress tracking for combined operations

3. **Improved UX**:
   - Clear workflow instructions
   - Real-time feedback
   - Error handling and validation

## Benefits

### For Users
- **Streamlined Workflow**: Single operation instead of multiple steps
- **Reduced Complexity**: No need to manually trigger curation after upload
- **Better UX**: Clear progress indication and feedback
- **Error Prevention**: Validation and error handling built-in

### For Developers
- **Modular Design**: Reuses existing upload and curate functionality
- **Extensible**: Easy to add more parameters or processing steps
- **Maintainable**: Clear separation of concerns
- **Testable**: Comprehensive error handling and validation

## API Documentation

### Combined Upload & Curate

```http
POST /upload_and_curate
Content-Type: multipart/form-data

Parameters:
- file: UploadFile (required)
- model_name: string (required)
- sampling_factor: float (optional, default: 0.5)
- process_sync: boolean (optional, default: true)
```

### Response Examples

**Success Response**:
```json
{
  "status": "success",
  "message": "Zip file uploaded, processed, and curation triggered successfully.",
  "filename": "dataset.zip",
  "path": "/uploads/dataset.zip",
  "processing_result": {
    "status": "success",
    "upload_id": "550e8400-e29b-41d4-a716-446655440000",
    "processed_files": 150,
    "output_folder": "/static/images/550e8400-e29b-41d4-a716-446655440000"
  },
  "curation_result": {
    "status": "success",
    "dataset": "/static/images/550e8400-e29b-41d4-a716-446655440000",
    "model": "yolov8n",
    "sampling_factor": 0.5
  },
  "workflow": "upload_and_curate_sync"
}
```

**Error Response**:
```json
{
  "error": "File must be a zip file"
}
```

## Future Enhancements

1. **Batch Processing**: Support for multiple file uploads
2. **Advanced Parameters**: More curation options and model configurations
3. **Progress Tracking**: Real-time progress updates for long-running operations
4. **Result Visualization**: Enhanced display of processing and curation results
5. **Export Functionality**: Download processed datasets and model improvements

## Testing

To test the combined functionality:

1. **Start the backend server**:
   ```bash
   cd coreset_selection/backend
   python main.py
   ```

2. **Start the frontend**:
   ```bash
   cd coreset_selection/frontend
   npm run dev
   ```

3. **Navigate to the "Upload & Curate" tab**
4. **Upload a zip file** with images/videos
5. **Configure parameters** and click "Upload & Curate"
6. **Verify results** in the Gallery tab

## Troubleshooting

### Common Issues

1. **File Upload Fails**:
   - Ensure the file is a valid zip file
   - Check file size limits
   - Verify network connectivity

2. **Processing Errors**:
   - Check that the zip contains supported media files
   - Verify backend dependencies are installed
   - Check server logs for detailed error messages

3. **Curation Fails**:
   - Ensure model name is provided
   - Verify sampling factor is between 0.0 and 1.0
   - Check that processed data is available

### Debug Information

The system provides comprehensive logging:
- File upload status
- Processing progress
- Curation parameters
- Error details and stack traces

Check the backend console for detailed logs during operation. 