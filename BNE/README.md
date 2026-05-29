# Bayesian Network Explorer

Welcome to the Bayesian Network Explorer! If you've ever wondered how artificial intelligence can reason with uncertainty, make predictions with incomplete information, or simply figure out why things happen, you're in the right place. 

This repository is designed to teach a complete beginner how Bayesian Networks work in an intuitive and fun way.

## What is a Bayesian Network?

Imagine you're a detective trying to figure out if it rained last night. You look outside and see that the grass is wet. You might think, "Aha! It rained!" 
But wait, what if someone just left the sprinklers on? Both rain and sprinklers can make the grass wet. And if it's cloudy, it's more likely to rain and less likely that someone turned on their sprinklers. 

A **Bayesian Network** is just a map of these "what-causes-what" relationships, combined with the odds (probabilities) of each thing happening. It helps computers think like our detective, updating their beliefs as new clues (evidence) come in. 

## Structure vs. Parameters

A Bayesian Network has two main parts:

1. **The Structure**: This is the visual map of how things influence each other. In our detective story, an arrow points from "Rain" to "Wet Grass" because rain causes the grass to get wet. It doesn't mean it *will* rain, just that *if* it rains, the grass cares about it.
2. **The Parameters**: These are the actual numbers. For example, "If it rains, there's a 95% chance the grass gets wet." It tells the network exactly how strong the influences are.

## The "Student" Testcase: A Walkthrough

In this repository, we build the classic "Student" model. Imagine a student taking a class. We want to predict if they will get a **Good Letter** of recommendation.

### The Setup
Here's what influences what:
- The **Difficulty** of the class and the student's **Intelligence** both determine the student's **Grade**.
- The student's **Intelligence** also influences their **CGPA** score.
- The **Grade** the student gets determines the quality of the recommendation **Letter**.

Even though **Intelligence** doesn't point directly to the **Letter**, knowing how smart the student is changes what we expect their grade to be, which in turn changes our expectation for the letter!

### The Magic of Inference
In our Python scripts, we ask the network a tricky question: 
> *"What is the probability of the student getting a Good Letter if we know the class Difficulty is High, and their CGPA score is Low?"*

Here is how the network thinks:
1. **Low CGPA** tells the network: "Hmm, it's highly likely this student's Intelligence is Low."
2. **High Difficulty** and (likely) **Low Intelligence** tell the network: "Oh boy, this student is very likely to get a bad Grade (like a C)."
3. Finally, a bad Grade tells the network: "There is a very low chance of getting a Good Letter."

Even though CGPA score and the Recommendation Letter have no direct connection (no arrow between them), observing the CGPA score dramatically changes our belief about the Letter. This ripple effect is the superpower of Bayesian Networks!

## How to Run the Code

We have implemented the exact same model using two different popular Python libraries (`pgmpy` and `pyAgrum`) to prove they yield the same mathematical truth.

### 1. Install Requirements
Make sure you have Python installed. Open your terminal or command prompt and run:
```bash
pip install -r requirements.txt
```

### 2. Run the `pgmpy` model
```bash
python pgmpy_student_model.py
```

### 3. Run the `pyAgrum` model
```bash
python pyagrum_student_model.py
```

