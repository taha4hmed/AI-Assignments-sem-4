# Introduction to Knowledge Graphs

## What is a Knowledge Graph?
Imagine you have a big corkboard where you pin pictures of your friends, your favorite companies, and your hobbies. To show how everything connects, you draw lines between the pictures. For example, a line from Alice to Bob might say "knows", and a line from Alice to a company might say "works at". 

A **Knowledge Graph** is the digital version of this corkboard! It's a way to organize information by focusing on **things (entities)** and how they are **connected (relationships)**. 

### Why are they useful?
- They help computers understand the context of data, just like humans do.
- They power search engines, recommendation systems, and smart assistants.
- They make complex relationships easy to visualize and explore.

## How Our Code Works
We have a python script called `KGB.py` that builds a mini Knowledge Graph from scratch. Here is what it does step-by-step:

1. **Defining the Entities (The Things)**: We create a list of people and companies (e.g., Alice, Bob, OpenAI, Microsoft, GitHub).
2. **Defining the Relationships (The Connections)**: We establish how they interact. For instance, Alice "works_at" OpenAI, and Microsoft "acquired" GitHub.
3. **Building the Graph**: The code links the entities and relationships together into a structured network.
4. **Showing the Results**:
   - It prints out text summaries (who is connected to whom).
   - It saves a static image (`output/graph_visualization.png`) so you can see a picture of the network.
   - It builds an interactive web page (`output/interactive_graph.html`) where you can zoom in, drag nodes around, and explore the connections yourself!

## How to Run It
1. Make sure you have the required libraries installed (`networkx`, `pandas`, `matplotlib`, `pyvis`).
2. Run the script: 
   ```bash
   python KGB.py
   ```
3. Check the `output/` folder for your cool graphs!
