import sys
import os
import json
from dotenv import load_dotenv

# Add project root directory to python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.graph import build_ecommerce_graph
from src.retriever import GraphRetriever
from src.llm import parse_intent, execute_retrieval, generate_grounded_answer

load_dotenv()

SAMPLE_QUESTIONS = [
    "Which products are supplied by Amazon?",
    "Which products belong to Apple?",
    "Which products from Apple are supplied by Amazon?",
    "Which orders were placed by Rahul?",
    "Which products are contained in order ORD001?",
    "How many banana values are present in the Knowledge Graph?",
    "Which products are supplied by Walmart?"
]


def process_question(retriever: GraphRetriever, question: str):
    """
    Executes the full pipeline for a natural language question:
    Question -> LLM intent parsing -> Graph retrieval -> Grounded LLM answer.
    """
    print("\n" + "=" * 60)
    print(f"QUESTION: {question}")
    print("=" * 60)
    
    # 1. LLM / Intent Parser
    intent_data = parse_intent(question)
    print("\n[1] STRUCTURED RETRIEVAL REQUEST (INTENT):")
    print(json.dumps(intent_data, indent=2))
    
    # 2. Graph Retrieval
    retrieved_data = execute_retrieval(retriever, intent_data)
    print("\n[2] RETRIEVED GRAPH DATA:")
    print(json.dumps(retrieved_data, indent=2))
    
    # 3. Grounded Final Answer Generation
    final_answer = generate_grounded_answer(question, retrieved_data)
    print("\n[3] FINAL GROUNDED ANSWER:")
    print(final_answer)
    print("=" * 60 + "\n")
    
    return {
        "question": question,
        "intent": intent_data,
        "retrieved_data": retrieved_data,
        "answer": final_answer
    }


def main():
    print("==================================================")
    print("  E-COMMERCE KNOWLEDGE GRAPH AI RETRIEVAL SYSTEM  ")
    print("==================================================")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("\n[WARNING] GEMINI_API_KEY is not set in environment or .env file.")
        print("          The system will run using deterministic local rule-based intent parsing and grounding.")
        print("          To enable full Gemini LLM features, copy .env.example to .env and set GEMINI_API_KEY.\n")
    else:
        print("\n[INFO] Gemini API key detected. Full LLM integration active.\n")
        
    print("Initializing Knowledge Graph from CSV dataset...")
    graph = build_ecommerce_graph()
    retriever = GraphRetriever(graph)
    print(f"Knowledge Graph initialized successfully: {len(graph.nodes)} nodes, {len(graph.edges)} edges.\n")
    
    # Check command-line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].strip()
        if arg == "--sample" or arg == "--demo":
            print("--- Running Sample Questions Demo ---\n")
            for q in SAMPLE_QUESTIONS:
                process_question(retriever, q)
            return
        else:
            # Question passed via command line
            question = " ".join(sys.argv[1:]).strip()
            process_question(retriever, question)
            return

    # Interactive CLI Loop
    print("Commands:")
    print("  - Type any question (e.g., 'Which products belong to Apple?')")
    print("  - Type 'sample' to run all 7 sample questions")
    print("  - Type 'exit' or 'quit' to exit\n")
    
    while True:
        try:
            user_input = input("Enter your question: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            if user_input.lower() in ["sample", "demo"]:
                for q in SAMPLE_QUESTIONS:
                    process_question(retriever, q)
                continue
                
            process_question(retriever, user_input)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break


if __name__ == "__main__":
    main()
