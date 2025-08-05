import os
import requests
from typing import Any, List, Mapping, Optional

from langchain_core.language_models.llms import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun


class CustomLLM(LLM):
    api_endpoint: str


    @property
    def _llm_type(self) -> str:
        return "custom"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        # if stop is not None:
        #     raise ValueError("stop kwargs are not permitted.")
        payload = {
                  "data": prompt
                }
        headers = {
          'Content-Type': 'application/json',
          'Authorization': "gd-d5b452d8-1c78-4010-9de1-72dde384090c-65effc5e1b2244c08d1239ee-test eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3MmRkZTM4NDA5MGMtOGVlZDA3ZWVmNDZmNDI4MmI4MWI1MDkwYjY0OTQ0N2ZrYXRvbmljIiwiZXhwIjozMzIzODAyNTc2MDgzM30.g5PAuett7y_YCOUp70d1Cp89N9DIzkNiPJJDCq1TmKQ"
        }
        
        response = requests.post(self.api_endpoint, json=payload, verify=False, headers = headers)
        if response.status_code >= 500:
            raise Exception(f"LLM Server: Error {response.status_code}")
        elif response.status_code >= 400:
            raise ValueError(f"LLM received an invalid payload/URL: {response.text}")
        elif response.status_code != 200:
            raise Exception(
                f"LLM returned an unexpected response with status "
                f"{response.status_code}: {response.text}"
            )
        return response.text
        

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {"api_endpoint": self.api_endpoint}
    

def katonic_completion():
    # logger.info(
    #     "------------------ Started LLM Completion ------------------"
    # )
    # api_endpoint = os.environ["CUSTOM_MODEL_API_ROUTE"]
    # api_endpoint = os.path.join(api_endpoint, "generate")
    
    api_endpoint = "https://dev.katonic.ai/65effc5e1b2244c08d1239ee/genai/gd-d5b452d8-1c78-4010-9de1-72dde384090c/api/v1/predict"

    katonic_llm = CustomLLM(api_endpoint= api_endpoint)
    return katonic_llm
