from pydantic import BaseModel, Field
from typing import List
from langchain_openai import ChatOpenAI
from app.tools.rest_countries import fetch_country
from app.utils.cache import cache_get, cache_set
from app.utils.logger import get_logger
import os

logger = get_logger(__name__)

# Dynamically route to OpenRouter, vLLM, Groq, or fallback to standard OpenAI
base_url = os.getenv("BASE_URL")
llm_kwargs = {"model": os.getenv("LLM_MODEL", "gpt-4o-mini"), "temperature": 0}

if base_url:
    llm_kwargs["base_url"] = base_url

llm = ChatOpenAI(**llm_kwargs)

DEFAULT_FIELDS = ["capital", "population"]

class IntentExtraction(BaseModel):
    country: str = Field(description="The name of the country identified in the user's query.")
    fields: List[str] = Field(
        description="List of requested fields. Allowed fields: capital, population, currency, region, languages.",
        default_factory=lambda: DEFAULT_FIELDS
    )

structured_llm = llm.with_structured_output(IntentExtraction)

def extract_intent(state):
    try:
        res = structured_llm.invoke(state["query"])
        fields = res.fields if res.fields else DEFAULT_FIELDS

        return {
            **state,
            "country": res.country,
            "fields": fields
        }
    except Exception as e:
        return {**state, "error": f"I couldn't understand which country you are asking about. Error: {str(e)}"}

def validate(state):
    if not state.get("country"):
        return {**state, "error": "Country not detected"}
    return state

async def call_api(state):
    try:
        if state.get("error"):
            return state
            
        cache_key = f"{state['country']}"

        cached = cache_get(cache_key)
        if cached:
            logger.info("Cache hit")
            return {**state, "api_response": cached}

        data = await fetch_country(state["country"])

        cache_set(cache_key, data)

        return {**state, "api_response": data}

    except ValueError as e:
        # Graceful handling for known client errors like 404
        return {**state, "error": str(e)}
    except Exception as e:
        return {**state, "error": f"API failure: {str(e)}"}

def process_data(state):
    if state.get("error"):
        return state

    data = state["api_response"]
    fields = state["fields"]

    result = {}

    if "capital" in fields:
        result["capital"] = data.get("capital", ["N/A"])[0]

    if "population" in fields:
        result["population"] = data.get("population")

    if "currency" in fields:
        currencies = data.get("currencies", {})
        result["currency"] = list(currencies.keys())[0] if currencies else "N/A"

    if "region" in fields:
        result["region"] = data.get("region")

    if "languages" in fields:
        langs = data.get("languages", {})
        result["languages"] = list(langs.values())

    return {**state, "api_response": result}

async def synthesize(state):
    if state.get("error"):
        return {
            **state,
            "final_answer": f"{state['error']}"
        }

    answer = f"Here is the information for {state['country']}:\n"

    for k, v in state["api_response"].items():
        if isinstance(v, list):
            v = ", ".join(v)
        answer += f"- {k.capitalize()}: {v}\n"

    return {**state, "final_answer": answer}
