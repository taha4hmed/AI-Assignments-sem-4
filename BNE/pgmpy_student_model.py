from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination

# 1. Define the network structure (DAG)
student_model = DiscreteBayesianNetwork([
    ('Difficulty', 'Grade'),
    ('Intelligence', 'Grade'),
    ('Intelligence', 'SAT'),
    ('Grade', 'Letter')
])

# 2. Define the CPDs
# Difficulty: 0=Easy, 1=Hard
cpd_d = TabularCPD(variable='Difficulty', variable_card=2, values=[[0.6], [0.4]])

# Intelligence: 0=Low, 1=High (70% chance of High)
cpd_i = TabularCPD(variable='Intelligence', variable_card=2, values=[[0.3], [0.7]])

# SAT: 0=Low, 1=High
# Evidence: Intelligence
cpd_s = TabularCPD(variable='SAT', variable_card=2,
                   values=[[0.8, 0.2],  # SAT=Low
                           [0.2, 0.8]], # SAT=High
                   evidence=['Intelligence'], evidence_card=[2])

# Grade: 0=A, 1=B, 2=C
# Evidence: Intelligence, Difficulty
# Values ordered as:
# I=0,D=0 | I=0,D=1 | I=1,D=0 | I=1,D=1
cpd_g = TabularCPD(variable='Grade', variable_card=3,
                   values=[[0.3, 0.1, 0.8, 0.5],  # Grade=A
                           [0.4, 0.3, 0.15, 0.3], # Grade=B
                           [0.3, 0.6, 0.05, 0.2]],# Grade=C
                   evidence=['Intelligence', 'Difficulty'], evidence_card=[2, 2])

# Letter: 0=Bad, 1=Good
# Evidence: Grade
cpd_l = TabularCPD(variable='Letter', variable_card=2,
                   values=[[0.1, 0.4, 0.99],  # Letter=Bad
                           [0.9, 0.6, 0.01]], # Letter=Good
                   evidence=['Grade'], evidence_card=[3])

# 3. Add CPDs to the model
student_model.add_cpds(cpd_d, cpd_i, cpd_s, cpd_g, cpd_l)

# 4. Validate the model
assert student_model.check_model()

# 5. Perform Inference
infer = VariableElimination(student_model)
print("Query: Probability of getting a good recommendation Letter (Letter=1)")
print("Given: Class Difficulty is High (Difficulty=1) and SAT score is Low (SAT=0)")

# Query for Letter given Difficulty=1 (Hard) and SAT=0 (Low)
result = infer.query(variables=['Letter'], evidence={'Difficulty': 1, 'SAT': 0})
print("\nInference Result:")
print(result)
