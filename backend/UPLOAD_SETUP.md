# File Upload with Verifier Agent Setup

This document explains the file upload functionality that integrates with the verifier agent to upload files to IPFS and return CIDs.

## Overview

The upload system consists of:
- **Upload API** (`/upload` endpoints) - Handles file uploads and status tracking
- **Verifier Agent** - Processes files and uploads them to IPFS
- **Lighthouse Service** - IPFS integration for file storage

## API Endpoints

### 1. Upload File
```
POST /upload/
```

**Parameters:**
- `file`: File to upload (multipart/form-data)
- `upload_type`: Type of upload (sustainability_document, carbon_footprint, certification, proof_of_impact)
- `user_wallet`: User's wallet address
- `metadata`: Optional JSON metadata

**Response:**
```json
{
  "upload_id": "uuid",
  "status": "processing",
  "message": "File uploaded successfully, processing via verifier agent",
  "filename": "example.json",
  "upload_type": "sustainability_document"
}
```

### 2. Check Upload Status
```
GET /upload/{upload_id}/status
```

**Response:**
```json
{
  "upload_id": "uuid",
  "status": "completed",
  "filename": "example.json",
  "upload_type": "sustainability_document",
  "created_at": "2024-01-15T10:30:00",
  "file_size": 1024,
  "cid": "QmMock...",
  "gateway_url": "https://gateway.lighthouse.storage/ipfs/QmMock...",
  "completed_at": "2024-01-15T10:30:05"
}
```

### 3. Get CID
```
GET /upload/{upload_id}/cid
```

**Response:**
```json
{
  "upload_id": "uuid",
  "cid": "QmMock...",
  "gateway_url": "https://gateway.lighthouse.storage/ipfs/QmMock...",
  "filename": "example.json",
  "upload_type": "sustainability_document",
  "completed_at": "2024-01-15T10:30:05"
}
```

## How It Works

1. **File Upload**: Client uploads file via POST `/upload/`
2. **Agent Processing**: File is sent to verifier agent for processing
3. **IPFS Upload**: Agent uploads file to IPFS via Lighthouse service
4. **CID Return**: Agent returns CID and gateway URL
5. **Status Tracking**: Client can check status and retrieve CID

## Supported File Types

- `image/jpeg`
- `image/png`
- `application/pdf`
- `text/csv`
- `application/json`

## Upload Types

- `sustainability_document`
- `carbon_footprint`
- `certification`
- `proof_of_impact`

## Testing

Run the test script to verify the upload functionality:

```bash
cd backend
python test_upload.py
```

The test script will:
1. Create a test JSON file with sustainability data
2. Upload it via the API
3. Check the upload status
4. Retrieve the CID
5. Clean up test files

## Configuration

Make sure to set the following environment variables:

```bash
LIGHTHOUSE_API_KEY=your_lighthouse_api_key
```

## Agent Integration

The verifier agent is automatically included in the Bureau when the application starts. It handles:
- File processing and validation
- IPFS upload via Lighthouse
- CID generation and return
- Error handling and status updates

## Error Handling

The system handles various error scenarios:
- Invalid file types
- Missing required parameters
- Network errors during IPFS upload
- Agent communication failures

All errors are logged and returned with appropriate HTTP status codes.
