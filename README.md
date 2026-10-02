# E-Commerce Knowledge Graph & AI Retrieval System

A minimal Python-based Knowledge Graph and AI Retrieval System built using **NetworkX**, **pandas**, and the **Google Gemini API** (`google-genai`). The system models e-commerce entities, converts natural language questions into structured graph queries, retrieves factual graph data, and uses an LLM to generate strictly grounded natural-language answers.

---

## 1. Project Overview

This project builds a simple, locally runnable Knowledge Graph representing an e-commerce domain. The system allows users to ask natural-language questions from the command line. An LLM (Google Gemini) parses the user's intent into a controlled JSON query. Python validates the intent and retrieves factual node/edge data from the NetworkX graph. Finally, Gemini generates a response based **ONLY** on the retrieved data, preventing hallucinations.

---

## 2. Architecture

```
User Question (Natural Language CLI)
              │
              ▼
   [1] LLM Intent Parser (src/llm.py)
       └─ Converts question to Structured JSON Request
              │
              ▼
   [2] Validation & Graph Querying (src/retriever.py)
       └─ Traverses NetworkX MultiDiGraph (src/graph.py)
              │
              ▼
   [3] Retrieved Factual Graph Data
              │
              ▼
   [4] LLM Grounded Answer Generator (src/llm.py)
       └─ Generates final answer strictly using retrieved data
              │
              ▼
   Final Answer Displayed in CLI
```

---

## 3. Knowledge Graph Entities

The Knowledge Graph represents **6 distinct entity types**:

| Entity | Description | CSV Data File |
| :--- | :--- | :--- |
| **Products** | E-commerce products (e.g., iPhone 15 Pro, MacBook Air M3) | `data/products.csv` |
| **Brands** | Manufacturers/Brands (e.g., Apple, Samsung, Sony) | `data/brands.csv` |
| **Categories** | Product categories (e.g., Electronics, Audio, Groceries) | `data/categories.csv` |
| **Vendors** | Suppliers/Sellers (e.g., Amazon, Best Buy, Fresh Market) | `data/vendors.csv` |
| **Customers** | Registered buyers (e.g., Rahul, Anita, John Doe) | `data/customers.csv` |
| **Orders** | Transactions placed by customers | `data/orders.csv` |

---

## 4. Graph Relationships

Relationships between entities are represented as directed edges in NetworkX (`MultiDiGraph`):

- `Customer` `──PLACED──>` `Order`
- `Order` `──CONTAINS──>` `Product`
- `Product` `──BELONGS_TO_BRAND──>` `Brand`
- `Product` `──IN_CATEGORY──>` `Category`
- `Vendor` `──SUPPLIES──>` `Product`

---

## 5. Retrieval Flow

The retrieval layer (`src/retriever.py`) exposes modular methods to traverse graph nodes and edges:
- `get_products_by_brand(brand)`: Retrieves products connected via `BELONGS_TO_BRAND`.
- `get_products_by_vendor(vendor)`: Retrieves products connected via `SUPPLIES`.
- `get_products_by_brand_and_vendor(brand, vendor)`: Computes graph intersection of brand and vendor products.
- `get_orders_by_customer(customer)`: Traverses `PLACED` edges from customer to order nodes.
- `get_products_by_order(order)`: Traverses `CONTAINS` edges from order to product nodes.
- `get_banana_values()`: Scans the graph for all 5 `banana` value/node entries.
- `get_products_by_category(category)`: Traverses `IN_CATEGORY` edges.
- `search_graph_by_keyword(keyword)`: General fallback lookup across graph node attributes.

---

## 6. LLM Integration

The Google Gemini API (`google-genai`) is used in a two-stage controlled architecture:

1. **Intent Parsing**: Converts natural language into controlled JSON:
   ```json
   {
     "intent": "products_by_brand_and_vendor",
     "parameters": {
       "brand": "Apple",
       "vendor": "Amazon"
     }
   }
   ```
2. **Controlled Execution**: The Python system validates the JSON against allowed retriever functions. **No arbitrary Python code, Cypher queries, or shell commands are executed.**

---

## 7. Grounding & Anti-Hallucination Approach

To ensure answers are based **ONLY** on retrieved data, the final LLM prompt includes strict grounding constraints:

> *"Answer the question using ONLY the supplied retrieved graph data. Do not use outside knowledge. If the retrieved data does not contain the answer, state that the information is not available in the Knowledge Graph."*

If an entity does not exist in the graph (e.g., vendor *"Walmart"*), the system returns an empty/not-found status, and the final answer states:  
`"The information is not available in the Knowledge Graph."`

---

## 8. Banana Requirement Implementation

The word `"banana"` is embedded as graph data **EXACTLY 5 TIMES** across 5 distinct entities:

1. **Brand**: Node `brand:B005` (name: `banana`)
2. **Category**: Node `category:C004` (name: `banana`)
3. **Vendor**: Node `vendor:V004` (name: `banana`)
4. **Customer**: Node `customer:CU004` (name: `banana`)
5. **Product**: Node `product:P007` (name: `banana`)

Calling `retriever.get_banana_values()` scans all node attributes in NetworkX and returns:
- `count`: `5`
- `results`: List of all 5 banana entities with their entity types and IDs.

Question: *"How many banana values are present in the Knowledge Graph?"*  
Answer: Returns `5` along with detailed graph retrieval proof.

---

## 9. Project Structure

```
ecommerce-knowledge-graph/
│
├── data/
│   ├── products.csv          # Product dataset
│   ├── brands.csv            # Brand dataset
│   ├── categories.csv        # Category dataset
│   ├── vendors.csv           # Vendor dataset
│   ├── customers.csv         # Customer dataset
│   └── orders.csv            # Order dataset
│
├── src/
│   ├── __init__.py           # Package initializer
│   ├── data_loader.py        # Loads CSV datasets using pandas
│   ├── graph.py              # Builds NetworkX MultiDiGraph
│   ├── retriever.py          # Traverses and queries NetworkX graph
│   ├── llm.py                # Gemini LLM intent parsing & grounded generation
│   ├── generate_results.py   # Utility to output sample_results.md
│   └── main.py               # Interactive Command Line Application
│
├── results/
│   └── sample_results.md     # Execution results for sample questions
│
├── .env.example              # Environment variable template
├── .gitignore                # Git ignore configuration
├── requirements.txt          # Python dependencies
└── README.md                 # Complete documentation
```

---

## 10. Prerequisites

- Python **3.10+** (or 3.x)
- Google Gemini API Key (optional for LLM features; local deterministic fallback active if omitted)

---

## 11. Installation

1. Clone or navigate to the repository directory:
   ```bash
   cd assignment
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

---

## 12. Environment Variable Setup

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and enter your Google Gemini API key:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   GEMINI_MODEL=gemini-2.5-flash
   ```

*(Note: If `GEMINI_API_KEY` is not provided, the application runs using deterministic rule-based intent parsing and grounded formatting).*

---

## 13. How to Run

### Interactive CLI Mode
To launch the interactive command line prompt:
```bash
python src/main.py
```
Example interactive session:
```text
Enter your question: Which products belong to Apple?
```

### Run Sample Demo Suite
To run all 7 sample questions automatically:
```bash
python src/main.py --sample
```

### Direct Single Question Command
Pass a question directly via command-line arguments:
```bash
python src/main.py "Which products from Apple are supplied by Amazon?"
```

---

## 14. Example Questions

1. *"Which products are supplied by Amazon?"*
2. *"Which products belong to Apple?"*
3. *"Which products from Apple are supplied by Amazon?"*
4. *"Which orders were placed by Rahul?"*
5. *"Which products are contained in order ORD001?"*
6. *"How many banana values are present in the Knowledge Graph?"*
7. *"Which products are supplied by Walmart?"* (Unanswerable / Out of Graph Test)

---

## 15. Example Results

Output from actual execution against the Knowledge Graph:

### Question: *"How many banana values are present in the Knowledge Graph?"*
- **Intent**: `{"intent": "banana_values", "parameters": {}}`
- **Retrieved Count**: `5`
- **Grounded Answer**: `"There are exactly 5 'banana' values present in the Knowledge Graph across Brand, Category, Vendor, Customer, and Product entities."`

### Question: *"Which products are supplied by Walmart?"*
- **Intent**: `{"intent": "products_by_vendor", "parameters": {"vendor": "Walmart"}}`
- **Retrieved Status**: `"not_found"`
- **Grounded Answer**: `"The information is not available in the Knowledge Graph."`

*Full detailed outputs for all sample questions can be found in [`results/sample_results.md`](results/sample_results.md).*

---

## 16. Testing Instructions

To verify graph setup, retriever functions, and banana counts programmatically:

1. **Run full sample demo**:
   ```bash
   python src/main.py --sample
   ```

2. **Run programmatic graph test script**:
   ```bash
   python -c "from src.graph import build_ecommerce_graph; from src.retriever import GraphRetriever; G = build_ecommerce_graph(); r = GraphRetriever(G); print('Nodes:', len(G.nodes)); print('Edges:', len(G.edges)); print('Banana count:', r.get_banana_values()['count'])"
   ```
   *Expected Output*: `Nodes: 29`, `Edges: 32`, `Banana count: 5`.
