from utils.summarizer import generate_summary

TEXT = """
Machine learning is a branch of artificial intelligence. It allows computers
to learn patterns from data and make predictions or decisions without being
explicitly programmed for every situation. Common applications include image
recognition, recommendation systems, and natural language processing.
"""

print("Generating summary with Gemini...\n")

try:
    summary = generate_summary(TEXT)
    print("Summary:\n")
    for i, point in enumerate(summary, 1):
        print("{}. {}".format(i, point))
except Exception as e:
    print("ERROR:", e)
