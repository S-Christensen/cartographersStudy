import random
import gameStart

def evaluate(strategy):
    score = 0
    # TODO Simulate the game and calculate score based on strategy
    # ...
    return score

# Generate initial population
def generate_population(size, constraints):
    population = []
    for _ in range(size):
        strategy = [random.uniform(0.15, 0.85) for _ in range(constraints)]
        population.append(strategy)
    return population

def select_parents(population, scores, num_parents):
    parents = [population[i] for i in sorted(range(len(scores)), key=lambda x: scores[x], reverse=True)[:num_parents]]
    return parents

def crossover(parents, num_offspring):
    offspring = []
    for _ in range(num_offspring):
        parent1, parent2 = random.sample(parents, 2)
        child = [(a + b) / 2 for a, b in zip(parent1, parent2)]
        offspring.append(child)
    return offspring

def mutate(offspring, mutation_rate=0.01):
    for child in offspring:
        if random.random() < mutation_rate:
            index = random.randint(0, len(child) - 1)
            child[index] = random.uniform(0.15, 0.85)
    return offspring

def genetic_algorithm(pop_size, constraints, generations, mutation_rate):
    population = generate_population(pop_size, constraints)
    for _ in range(generations):
        scores = [evaluate(strategy) for strategy in population]
        parents = select_parents(population, scores, pop_size // 2)
        offspring = crossover(parents, pop_size - len(parents))
        offspring = mutate(offspring, mutation_rate)
        population = parents + offspring
    best_strategy = max(population, key=evaluate)
    return best_strategy

# Parameters
population_size = 100
num_constraints = 6
num_generations = 50
mutation_rate = 0.01

optimal_strategy = genetic_algorithm(population_size, num_constraints, num_generations, mutation_rate)
print("Optimal Strategy:", optimal_strategy)
