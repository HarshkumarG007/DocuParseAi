import pytest
import torch
from src.ml.layoutlm_model import DocumentParserModel
from PIL import Image

def test_model_initialization():
    model = DocumentParserModel()
    assert model is not None

def test_model_inference():
    model = DocumentParserModel()
    if not model.is_loaded:
        pytest.skip("Model could not be loaded, skipping inference test.")
        
    img = Image.new('RGB', (800, 800), color='white')
    words = ["Total", "$100.00"]
    # Provide boxes in 0-1000 normalized format as expected
    boxes = [[10, 10, 50, 20], [60, 10, 120, 20]]
    
    results = model.predict(img, words, boxes)
    assert isinstance(results, list)
    
    for res in results:
        assert "field_type" in res
        assert "confidence" in res
        assert "bbox_json" in res
