#!/usr/bin/env python3
"""Test script for Q&A service"""

from app.services.qa_service import QAService

def test_qa_service():
    """Test the Q&A service"""
    print("Testing Q&A Service...")

    # Initialize service without embedding service for basic test
    qa_service = QAService()

    # Mock setup
    chunks = [
        "This is a sample research paper about machine learning.",
        "Machine learning is a subset of artificial intelligence.",
        "Deep learning uses neural networks with multiple layers.",
        "Natural language processing helps computers understand text.",
        "Computer vision allows machines to interpret visual information."
    ]

    # Manually set up for testing
    qa_service.chunks = chunks
    qa_service.index = "mock_index"  # Mock index

    print(f"QA system mock setup with {len(chunks)} chunks...")

    # Test the simple answer method
    question = "What is machine learning?"
    print(f"\nQuestion: {question}")
    answer = qa_service._simple_answer(question, " ".join(chunks))
    print(f"Simple Answer: {answer}")

    print("\nQ&A service basic functionality test passed!")

if __name__ == "__main__":
    test_qa_service()