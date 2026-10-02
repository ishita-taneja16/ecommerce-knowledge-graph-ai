import json
import os
import sys

# Ensure root in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.graph import build_ecommerce_graph
from src.retriever import GraphRetriever
from src.llm import parse_intent, execute_retrieval, generate_grounded_answer
from src.main import SAMPLE_QUESTIONS

def generate_sample_results_md():
    graph = build_ecommerce_graph()
    retriever = GraphRetriever(graph)
    
    md_content = []
    md_content.append("# Sample Questions and Retrieval Results")
    md_content.append("")
    md_content.append("This document contains the actual execution output of sample natural-language queries against the E-Commerce Knowledge Graph system.")
    md_content.append("")
    
    questions = [
        "Which products are supplied by Amazon?",
        "Which products belong to Apple?",
        "Which products from Apple are supplied by Amazon?",
        "Which orders were placed by Rahul?",
        "Which products are contained in order ORD001?",
        "How many banana values are present in the Knowledge Graph?",
        "Which products are supplied by Walmart?"
    ]
    
    for idx, q in enumerate(questions, 1):
        intent_data = parse_intent(q)
        retrieved_data = execute_retrieval(retriever, intent_data)
        answer = generate_grounded_answer(q, retrieved_data)
        
        md_content.append(f"## Question {idx}: {q}")
        md_content.append("")
        md_content.append("### 1. Structured Retrieval Request (LLM Intent)")
        md_content.append("```json")
        md_content.append(json.dumps(intent_data, indent=2))
        md_content.append("```")
        md_content.append("")
        md_content.append("### 2. Retrieved Knowledge Graph Data")
        md_content.append("```json")
        md_content.append(json.dumps(retrieved_data, indent=2))
        md_content.append("```")
        md_content.append("")
        md_content.append("### 3. Final Grounded Natural Language Answer")
        md_content.append(f"> **Answer:** {answer}")
        md_content.append("")
        md_content.append("---")
        md_content.append("")

    results_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
    os.makedirs(results_dir, exist_ok=True)
    file_path = os.path.join(results_dir, "sample_results.md")
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_content))
        
    print(f"Sample results successfully generated and written to: {file_path}")

if __name__ == "__main__":
    generate_sample_results_md()
