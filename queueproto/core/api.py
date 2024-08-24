from random import random
import time
from typing import Callable, Optional

from core.definitions import ApiResponse, Error


# Simulate work of sending an API request and waiting for response
def simulate_request(
    data_callback: Optional[Callable], to_wait: float = 0.5, allow_failure: bool = False, failure_percentage: int = 5
) -> ApiResponse:
    time.sleep(to_wait)

    success_response = ApiResponse(
        status_code=200,
        response=data_callback() if data_callback is not None else None,
    )

    if not allow_failure:
        return success_response

    if random() < failure_percentage / 100:
        # failure response
        return ApiResponse(
            status_code=400,
            response=Error(message="Invalid data provided"),
        )
    
    return success_response

