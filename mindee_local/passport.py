from mindee import ClientV2, InferenceParameters
import os
from dotenv import load_dotenv

load_dotenv()

PASSPORT_MODEL_ID = "15f656e9-0771-4885-92f6-f1b5aa39df3f"
API_KEY = os.getenv("MINDEE_TOKEN")

def process_passport(image_path: str):
    client = ClientV2(API_KEY)
    input_source = client.source_from_path(image_path)
    params = InferenceParameters(model_id=PASSPORT_MODEL_ID, rag=False)
    response = client.enqueue_and_get_inference(input_source, params)
    fields = response._raw_http['inference']['result']['fields']
    return {
        "surname": fields.get("surnames", {}).get("value", ""),
        "given_names": fields.get("given_names", {}).get("value", ""),
        # "birth_date": prediction.birth_date.value if hasattr(prediction, "birth_date") else "",
        # "document_number": prediction.document_number.value if hasattr(prediction, "document_number") else "",
        # Add more fields as needed
    }
