from mindee import ClientV2, InferenceParameters
import os
from dotenv import load_dotenv

load_dotenv()

CAR_DOC_MODEL_ID = "f60dc7dd-afc9-4c0e-8043-08f988bcd03f"
API_KEY = os.getenv("MINDEE_TOKEN")

def process_car_doc(pdf_path: str):
    client = ClientV2(API_KEY)
    input_source = client.source_from_path(pdf_path)
    params = InferenceParameters(model_id=CAR_DOC_MODEL_ID, rag=False)
    response = client.enqueue_and_get_inference(input_source, params)
    fields = response._raw_http['inference']['result']['fields']
    return {
        "vin_code": fields.get("vin_code", {}).get("value", ""),
        "registration_number": fields.get("registration_number", {}).get("value", ""),
        "car_brand": fields.get("car_brand", {}).get("value", ""),
        "car_model": fields.get("car_model", {}).get("value", ""),
        "color": fields.get("color", {}).get("value", ""),
        "year_of_manufacture": fields.get("year_of_manufacture", {}).get("value", ""),
        "engine_type": fields.get("engine_type", {}).get("value", ""),
        # Add more fields as needed
    }