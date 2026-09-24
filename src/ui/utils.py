import requests
from typing import Optional, List, Dict, Any

API_BASE_URL = "http://localhost:8000/api/v1"

def upload_document(uploaded_file) -> Dict[str, Any]:
    """Upload a document file to the backend API."""
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
    response = requests.post(f"{API_BASE_URL}/documents/upload", files=files, timeout=60)
    if response.status_code == 201:
        return response.json()
    raise RuntimeError(f"Upload failed ({response.status_code}): {response.text}")

def fetch_documents(limit: int = 100) -> List[Dict[str, Any]]:
    """Retrieve list of processed documents from backend."""
    response = requests.get(f"{API_BASE_URL}/documents?limit={limit}", timeout=10)
    if response.status_code == 200:
        return response.json()
    return []

def fetch_document(document_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve a single document record by ID."""
    response = requests.get(f"{API_BASE_URL}/documents/{document_id}", timeout=10)
    if response.status_code == 200:
        return response.json()
    return None

def submit_correction(document_id: str, field_type: str, original_value: str, corrected_value: str) -> bool:
    """Submit a field correction to the backend."""
    payload = {
        "field_type": field_type,
        "original_value": original_value,
        "corrected_value": corrected_value
    }
    response = requests.post(f"{API_BASE_URL}/documents/{document_id}/correct", json=payload, timeout=10)
    return response.status_code == 200
