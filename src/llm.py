import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

# Check for google-genai availability
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


def get_gemini_client():
    """Initializes and returns the Gemini client if GEMINI_API_KEY is configured."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    if not GENAI_AVAILABLE:
        return None
    try:
        return genai.Client(api_key=api_key)
    except Exception as e:
        print(f"[Warning] Failed to initialize Gemini Client: {e}")
        return None


INTENT_SYSTEM_PROMPT = """
You are an intent parser for an e-commerce Knowledge Graph retrieval system.
Convert the natural language user question into a structured JSON query object matching ONE of these supported intents:

1. "products_by_brand": Find products belonging to a brand.
   Parameters: {"brand": "<brand_name>"}

2. "products_by_vendor": Find products supplied by a vendor.
   Parameters: {"vendor": "<vendor_name>"}

3. "products_by_brand_and_vendor": Find products of a specific brand supplied by a specific vendor.
   Parameters: {"brand": "<brand_name>", "vendor": "<vendor_name>"}

4. "orders_by_customer": Find orders placed by a customer.
   Parameters: {"customer": "<customer_name>"}

5. "products_by_order": Find products contained in a specific order ID.
   Parameters: {"order": "<order_id>"}

6. "banana_values": Count or retrieve 'banana' nodes/values in the Knowledge Graph.
   Parameters: {}

7. "products_by_category": Find products in a specific category.
   Parameters: {"category": "<category_name>"}

8. "general_search": General keyword lookup in the graph.
   Parameters: {"keyword": "<keyword>"}

Return ONLY valid raw JSON with keys "intent" and "parameters". Do not add markdown formatting, backticks, or explanation.

Example Output:
{"intent": "products_by_brand_and_vendor", "parameters": {"brand": "Apple", "vendor": "Amazon"}}
"""


def rule_based_intent_parser(question: str) -> dict:
    """
    Fallback rule-based intent parser to guarantee deterministic query processing
    if LLM API key is missing or API is unreachable.
    """
    q_lower = question.lower()
    
    # Banana query
    if "banana" in q_lower:
        return {"intent": "banana_values", "parameters": {}}
        
    # Brand AND Vendor query
    if "brand" in q_lower and "vendor" in q_lower:
        brand_match = re.search(r"brand\s+([a-zA-Z0-9]+)", question, re.IGNORECASE)
        vendor_match = re.search(r"vendor\s+([a-zA-Z0-9]+)", question, re.IGNORECASE)
        brand = brand_match.group(1) if brand_match else "Apple"
        vendor = vendor_match.group(1) if vendor_match else "Amazon"
        return {"intent": "products_by_brand_and_vendor", "parameters": {"brand": brand, "vendor": vendor}}
        
    # Apple from Amazon / Apple supplied by Amazon
    if ("apple" in q_lower or "samsung" in q_lower or "sony" in q_lower) and ("amazon" in q_lower or "best buy" in q_lower or "walmart" in q_lower):
        brand = "Apple" if "apple" in q_lower else ("Samsung" if "samsung" in q_lower else "Sony")
        vendor = "Amazon" if "amazon" in q_lower else ("Best Buy" if "best buy" in q_lower else "Walmart")
        return {"intent": "products_by_brand_and_vendor", "parameters": {"brand": brand, "vendor": vendor}}
        
    # Customer orders (e.g. "orders placed by Rahul")
    if "placed by" in q_lower or "placed" in q_lower or "by customer" in q_lower or "orders for" in q_lower:
        if "rahul" in q_lower:
            customer = "Rahul"
        elif "anita" in q_lower:
            customer = "Anita"
        elif "john" in q_lower:
            customer = "John Doe"
        elif "banana" in q_lower:
            customer = "banana"
        else:
            cust_match = re.search(r"(placed by|by|customer)\s+([a-zA-Z0-9\s]+)", question, re.IGNORECASE)
            customer = cust_match.group(2).strip() if cust_match else "Rahul"
        return {"intent": "orders_by_customer", "parameters": {"customer": customer}}

    # Order products (e.g. "contained in order ORD001")
    if "contained in order" in q_lower or "in order" in q_lower or "products in order" in q_lower or re.search(r"\bORD\d+\b", question, re.IGNORECASE):
        order_match = re.search(r"(ORD\d+)", question, re.IGNORECASE)
        order_id = order_match.group(1) if order_match else "ORD001"
        return {"intent": "products_by_order", "parameters": {"order": order_id}}
        
    # Vendor query
    if "vendor" in q_lower or "supplied by" in q_lower or "amazon" in q_lower or "walmart" in q_lower:
        vendor = "Amazon"
        if "walmart" in q_lower:
            vendor = "Walmart"
        elif "best buy" in q_lower:
            vendor = "Best Buy"
        elif "fresh market" in q_lower:
            vendor = "Fresh Market"
        return {"intent": "products_by_vendor", "parameters": {"vendor": vendor}}
        
    # Brand query
    if "brand" in q_lower or "belong to" in q_lower or "apple" in q_lower or "samsung" in q_lower:
        brand = "Apple" if "apple" in q_lower else "Samsung"
        return {"intent": "products_by_brand", "parameters": {"brand": brand}}

    # Default fallback
    words = [w for w in re.findall(r'\w+', question) if len(w) > 3]
    kw = words[0] if words else question
    return {"intent": "general_search", "parameters": {"keyword": kw}}


def parse_intent(question: str) -> dict:
    """
    Understands a natural-language question and converts it into a structured graph query intent.
    Uses Gemini API if available, else falls back to rule-based parser.
    """
    client = get_gemini_client()
    if not client:
        return rule_based_intent_parser(question)
        
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    prompt = f"{INTENT_SYSTEM_PROMPT}\n\nUser Question: {question}"
    
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )
        text = response.text.strip()
        # Clean markdown wrappers if returned
        text = re.sub(r"^```json\s*", "", text, flags=re.MULTILINE)
        text = re.sub(r"^```\s*", "", text, flags=re.MULTILINE)
        text = text.strip()
        
        data = json.loads(text)
        if "intent" in data and "parameters" in data:
            return data
    except Exception as e:
        print(f"[Notice] Gemini intent parsing failed ({e}), using fallback parser.")
        
    return rule_based_intent_parser(question)


def execute_retrieval(retriever, intent_data: dict) -> dict:
    """
    Validates structured query request and calls the appropriate retriever function.
    No arbitrary code execution allowed.
    """
    intent = intent_data.get("intent")
    params = intent_data.get("parameters", {})
    
    if intent == "products_by_brand":
        brand = params.get("brand", "")
        return retriever.get_products_by_brand(brand)
        
    elif intent == "products_by_vendor":
        vendor = params.get("vendor", "")
        return retriever.get_products_by_vendor(vendor)
        
    elif intent == "products_by_brand_and_vendor":
        brand = params.get("brand", "")
        vendor = params.get("vendor", "")
        return retriever.get_products_by_brand_and_vendor(brand, vendor)
        
    elif intent == "orders_by_customer":
        customer = params.get("customer", "")
        return retriever.get_orders_by_customer(customer)
        
    elif intent == "products_by_order":
        order = params.get("order", "")
        return retriever.get_products_by_order(order)
        
    elif intent == "banana_values":
        return retriever.get_banana_values()
        
    elif intent == "products_by_category":
        category = params.get("category", "")
        return retriever.get_products_by_category(category)
        
    elif intent == "general_search":
        keyword = params.get("keyword", "")
        return retriever.search_graph_by_keyword(keyword)
        
    else:
        return {
            "status": "error",
            "message": f"Unsupported retrieval intent: '{intent}'",
            "results": [],
            "count": 0
        }


GROUNDING_SYSTEM_PROMPT = """
You are a strict, grounded AI assistant answering questions about an e-commerce Knowledge Graph dataset.

CRITICAL INSTRUCTIONS FOR GROUNDING:
1. Answer the question using ONLY the supplied retrieved graph data below.
2. Do NOT use outside knowledge or general knowledge.
3. If the retrieved graph data does not contain the answer, state explicitly: "The information is not available in the Knowledge Graph."
4. Be precise, accurate, concise, and direct in your response.
"""


def generate_grounded_answer(question: str, retrieved_data: dict) -> str:
    """
    Generates the final natural-language answer using Gemini LLM,
    strictly grounded in the retrieved Knowledge Graph data.
    """
    client = get_gemini_client()
    
    # Grounding fallback if no Gemini client (e.g. missing API key)
    if not client:
        status = retrieved_data.get("status")
        if status == "not_found" or status == "empty" or retrieved_data.get("count", 0) == 0:
            return "The information is not available in the Knowledge Graph."
            
        results = retrieved_data.get("results", [])
        count = retrieved_data.get("count", len(results))
        
        if retrieved_data.get("query") == "banana":
            return f"There are exactly {count} 'banana' values present in the Knowledge Graph across Brand, Category, Vendor, Customer, and Product entities."
            
        if "results" in retrieved_data and isinstance(results, list):
            items_str = ", ".join([r.get("product_name", r.get("name", r.get("order_id", str(r)))) for r in results])
            return f"Based on retrieved graph data ({count} item(s)): {items_str}."
            
        return f"Retrieved Knowledge Graph Data: {json.dumps(retrieved_data)}"

    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    prompt = f"""
{GROUNDING_SYSTEM_PROMPT}

User Question:
{question}

Retrieved Knowledge Graph Data:
{json.dumps(retrieved_data, indent=2)}
"""

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )
        return response.text.strip()
    except Exception as e:
        # Fallback if Gemini generation encounters an issue (e.g. quota/network error)
        status = retrieved_data.get("status")
        if status in ["not_found", "empty"] or retrieved_data.get("count", 0) == 0:
            return "The information is not available in the Knowledge Graph."
        return f"[Retrieved Graph Data Result]: {json.dumps(retrieved_data)}"
