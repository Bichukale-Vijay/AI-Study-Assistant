import matplotlib.pyplot as plt
import os
import uuid

def generate_binary_search_diagram(array, mid_index):
    """
    Generates a simple visual diagram for Binary Search.
    """
    filename = f"static/images/{uuid.uuid4()}.png"
    plt.figure(figsize=(8,2))
    plt.bar(range(len(array)), array, color="lightblue")
    plt.bar(mid_index, array[mid_index], color="orange")  # Highlight mid
    plt.xlabel("Index")
    plt.ylabel("Value")
    plt.title("Binary Search Step")
    plt.savefig(filename)
    plt.close()
    return filename