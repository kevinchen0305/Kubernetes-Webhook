from fastapi import FastAPI, Body
from os import environ
from models import Patch
import logging
import base64
import json

app = FastAPI()

webhook = logging.getLogger(__name__)
uvicorn_logger = logging.getLogger("uvicorn")
uvicorn_logger.removeHandler(uvicorn_logger.handlers[0])  # Turn off uvicorn duplicate log
webhook.setLevel(logging.INFO)
logging.basicConfig(format="[%(asctime)s] %(levelname)s: %(message)s")

pool = environ.get("NODE_POOL")
if not pool:
    webhook.error("The required environment variable 'NODE_POOL' isn't set. Exiting...")
    exit(1)


def patch(node_pool: str) -> base64:
    label, value = node_pool.replace(" ", "").split(":")
    webhook.info(f"Got '{node_pool}' as nodeSelector label, patching...")

    # change from https://github.com/k-mitevski/kubernetes-mutating-webhook
    patch_operations = [Patch(op="add", path="/spec/template/spec/containers/0/envFrom", value=[]).dict()]
    webhook.info(patch_operations)
    patch_operations.append(Patch(op="add", path="/spec/template/spec/containers/0/envFrom/-", value={"configMapRef": {"name": "demo-config"}}).dict())
    webhook.info(patch_operations)

    return base64.b64encode(json.dumps(patch_operations).encode())


def admission_review(uid: str, message: str) -> dict:
    return {
        "apiVersion": "admission.k8s.io/v1",
        "kind": "AdmissionReview",
        "response": {
            "uid": uid,
            "allowed": True,
            "patchType": "JSONPatch",
            "status": {"message": message},
            "patch": patch(pool).decode(),
        },
    }


@app.post("/mutate")
def mutate_request(request: dict = Body(...)):
    uid = request["request"]["uid"]
    selector = request["request"]["object"]["spec"]["template"]["spec"]
    object_in = request["request"]["object"]

    webhook.info(f'Applying nodeSelector for {object_in["kind"]}/{object_in["metadata"]["name"]}.')

    return admission_review(
        uid,
        "Successfully added nodeSelector.",
    )
