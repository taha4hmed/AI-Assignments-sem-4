import pyagrum as gum

# 1. Create the Bayesian Network
bn = gum.BayesNet('Student')

# 2. Add variables
# Difficulty: 0=Easy, 1=Hard
bn.add(gum.LabelizedVariable('Difficulty', 'Difficulty', ['Easy', 'Hard']))
# Intelligence: 0=Low, 1=High
bn.add(gum.LabelizedVariable('Intelligence', 'Intelligence', ['Low', 'High']))
# SAT: 0=Low, 1=High
bn.add(gum.LabelizedVariable('SAT', 'SAT', ['Low', 'High']))
# Grade: 0=A, 1=B, 2=C
bn.add(gum.LabelizedVariable('Grade', 'Grade', ['A', 'B', 'C']))
# Letter: 0=Bad, 1=Good
bn.add(gum.LabelizedVariable('Letter', 'Letter', ['Bad', 'Good']))

# 3. Add edges
bn.addArc('Difficulty', 'Grade')
bn.addArc('Intelligence', 'Grade')
bn.addArc('Intelligence', 'SAT')
bn.addArc('Grade', 'Letter')

# 4. Define CPDs
bn.cpt('Difficulty').fillWith([0.6, 0.4])
bn.cpt('Intelligence').fillWith([0.3, 0.7])

# SAT given Intelligence
# I=Low
bn.cpt('SAT')[{'Intelligence': 'Low'}] = [0.8, 0.2]
# I=High
bn.cpt('SAT')[{'Intelligence': 'High'}] = [0.2, 0.8]

# Grade given Intelligence, Difficulty
# I=Low, D=Easy
bn.cpt('Grade')[{'Intelligence': 'Low', 'Difficulty': 'Easy'}] = [0.3, 0.4, 0.3]
# I=Low, D=Hard
bn.cpt('Grade')[{'Intelligence': 'Low', 'Difficulty': 'Hard'}] = [0.1, 0.3, 0.6]
# I=High, D=Easy
bn.cpt('Grade')[{'Intelligence': 'High', 'Difficulty': 'Easy'}] = [0.8, 0.15, 0.05]
# I=High, D=Hard
bn.cpt('Grade')[{'Intelligence': 'High', 'Difficulty': 'Hard'}] = [0.5, 0.3, 0.2]

# Letter given Grade
# Grade=A
bn.cpt('Letter')[{'Grade': 'A'}] = [0.1, 0.9]
# Grade=B
bn.cpt('Letter')[{'Grade': 'B'}] = [0.4, 0.6]
# Grade=C
bn.cpt('Letter')[{'Grade': 'C'}] = [0.99, 0.01]

# 5. Perform Inference
ie = gum.VariableElimination(bn)
# Evidence: Difficulty=Hard, SAT=Low
ie.setEvidence({'Difficulty': 'Hard', 'SAT': 'Low'})
ie.makeInference()

print("Query: Probability of getting a good recommendation Letter (Letter='Good')")
print("Given: Class Difficulty is High ('Hard') and SAT score is Low ('Low')")

print("\nInference Result:")
print(ie.posterior('Letter'))
