import json
import grpc
from protobuf import *

protos, services = grpc.protos_and_services("master_to_secondary.proto")

SERVICE_CONFIG = json.dumps(
    {
        "methodConfig": [
            {
                "name": [
                    {"service": "master_to_secondary.MasterService"},
                ],
                "retryPolicy": {
                    "maxAttempts": 5,
                    "initialBackoff": "0.3s",
                    "maxBackoff": "10s",
                    "backoffMultiplier": 3,
                    "retryableStatusCodes": ["UNAVAILABLE"],

                },
            }
        ]
    }
)
options = [
    ("grpc.service_config", SERVICE_CONFIG),
]
