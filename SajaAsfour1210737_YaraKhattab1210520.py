#saja asfour 1210737  sec 4
#yara khattab 1210520 sec 2
import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

#this function to  get the inputs from user 
def getInputFromUser():
    num_of_job = int(input("Enter the number of jobs: "))
    num_of_machine = int(input("Enter the number of machines: "))
    
    #array to hold the operations of each jobs 
    jobs = []
    for num in range(num_of_job):
        operations_input = input(f"Enter operations for job {num} in the format [(machine, time), ...]: ")

        # Convert string input to list of tuples
        operations = eval(operations_input)  
        #add the operations to jobs array
        jobs.append(operations)
    
    return jobs, num_of_machine

class JobShopGA:
    
    # create a special method automatically called when an object is created from a JobShopGA class.
    def __init__(obj, jobs, num_of_machine, population_size=50, generations=100, mutation_rate=0.1):
        obj.jobs = jobs
        obj.num_of_machine = num_of_machine
        obj.population_size = population_size
        obj.generations = generations
        obj.mutation_rate = mutation_rate

    def initialize_population(obj):
        #this array to hold the chromosome 
        population = []
        # we use _ becouse we dont want to use the loop counter inside the loop
        #This loop iterates obj.population_size times, creating a new chromosome for each iteration.
        for _ in range(obj.population_size):

            #creates a list containing the indices of the jobs in which the jobs will initially be processed.
            chromosome = list(range(len(obj.jobs)))
            #shuffles the indices within the chromosome list to create a random order of jobs. 
            random.shuffle(chromosome)
            #Once the chromosome is created and shuffled, it is added to the population list
            population.append(chromosome)

        #After all chromosomes have been created and added to the population list
        # the method returns the populated list of chromosomes
        return population

    # in this function we find the max makespan which is the total time required to complete all jobs in the schedule
    def fitness(obj, chromosome):
        #Initializes a list to track the completion time for each machine and set each index to zero.
        machine_times = [0] * obj.num_of_machine
        #Initializes a list to track the completion time for each job  and set each index to zero
        job_times = [0] * len(obj.jobs)
        
        #Iterates over the jobs in the order specified by the chromosome
        for job_index in chromosome:
            #Iterates through the operations of the current job
            for machine, time in obj.jobs[job_index]:
                #Calculates the start time for the current operation
                #It's the max of the time when the machine will be free and the time when the job is ready for its next operation
                start_time = max(machine_times[machine], job_times[job_index])
                machine_times[machine] = start_time + time
                job_times[job_index] = machine_times[machine]

        return max(machine_times)
    
    #this methode is for choosing chromosomes from the population to be parents for the next generation
    def selection(obj, population, fitnesses):
        #Calculates the total fitness of the entire population
        total_fitness = sum(fitnesses)
        #Calculates the selection probabilities for each chromosome in the population
        selection_probs = [f / total_fitness for f in fitnesses]
        return population[np.random.choice(len(population), p=selection_probs)]
    
    # this method  is for combining genetic material from two parent chromosomes to produce a 2 child chromosome
    def crossover(obj, parent1, parent2):

        #Generates a random integer representing the crossover point
        crossoverStart = random.randint(1, len(parent1) - 1)
        # Initializes an empty childs chromosome with the same length as the parent chromosomes
        child1 = [-1] * len(parent1)
        child2=  [-1] * len(parent2)
        # Copies genetic material from parent1 up to the crossover point into the child1 chromosome
        child1[:crossoverStart] = parent1[:crossoverStart]
        # Copies genetic material from parent2 up to the crossover point into the child2 chromosome
        child2[:crossoverStart] = parent2[:crossoverStart]
        position = crossoverStart
        #The remaining genes in the child1 chromosome are filled by iterating over the genes in parent2
        for job in parent2:
            if job not in child1:
                child1[position] = job
                position += 1
        position = crossoverStart
        #The remaining genes in the child2 chromosome are filled by iterating over the genes in parent1
        for job in parent1:
            if job not in child2:
                child2[position] = job
                position += 1
        return child1 ,child2

    def mutate(obj, chromosome):
        if random.random() < obj.mutation_rate:
            index1, index2 = random.sample(range(len(chromosome)), 2)
            chromosome[index1], chromosome[index2] = chromosome[index2], chromosome[index1]

    def run(obj):
        population = obj.initialize_population()
        best_fitness = float('inf')
        best_schedule = None

        for generation in range(obj.generations):
            fitnesses = [obj.fitness(chromosome) for chromosome in population]
            #this to hold childern as a new generation 
            new_population = []
            #The loop runs obj.population_size // 2 times to ensure that 
            #the total number of offspring produced equals the population size
            for _ in range(obj.population_size // 2):
                parent1 = obj.selection(population, fitnesses)
                parent2 = obj.selection(population, fitnesses)
                child1, child2 = obj.crossover(parent1, parent2)
                obj.mutate(child1)
                new_population.append(child1)
                obj.mutate(child2)
                new_population.append(child2)
            population = new_population
            min_makespan = min(fitnesses)
            if min_makespan < best_fitness:
                best_fitness = min_makespan
                best_schedule = population[fitnesses.index(min_makespan)]

        return best_schedule, best_fitness
    
    #method used to visualize the schedule of jobs on machines using a Gantt chart
    def create_gantt_chart(obj, schedule):
        machine_times = [0] * obj.num_of_machine
        job_times = [0] * len(obj.jobs)
        #Initializes an empty list to store the details of each task (operation) for later visualization
        Operations = []

        #Iterates through the jobs in the order specified by the schedule (chromosome)
        for Job in schedule: 
            #Iterates through the operations of each job
            for machine, time in obj.jobs[Job]:
                #Determines the start time for the current operation
                start_time = max(machine_times[machine], job_times[Job])
                machine_times[machine] = start_time + time
                job_times[Job] = machine_times[machine]
                #Records the details of the operation for later visualization
                Operations.append((machine, start_time, time, Job))

        #Creates a new figure and a subplot for the Gantt chart
        fig, gnt = plt.subplots()
        #Sets the vertical limits of the chart, with each machine having a separate row
        gnt.set_ylim(0, 10 * obj.num_of_machine)
        #Sets the horizontal limits of the chart, extending slightly beyond the total makespan
        gnt.set_xlim(0, max(machine_times) + 10)
        # Labels the x-axis as "Time"
        gnt.set_xlabel('Time')
        #Labels the y-axis as "Machines"
        gnt.set_ylabel('Machines')

        #Sets the y-ticks to correspond to each machine
        gnt.set_yticks([i * 10 + 5 for i in range(obj.num_of_machine)])
        #Labels each row with the corresponding machine number
        gnt.set_yticklabels([f'Machine {i}' for i in range(obj.num_of_machine)])

        #Iterates through the recorded Operations.
        for task in Operations:
            machine, start, duration, job = task
            # Adds a bar to the Gantt chart for each task
            #using a unique color for each job, The bar represents the duration of the task on the specified machine
            gnt.broken_barh([(start, duration)], (machine * 10, 9), facecolors=(f"C{job % 10}"))

        #Creates legend patches for each job, assigning unique colors
        patches = [mpatches.Patch(color=f"C{i % 10}", label=f'Job {i}') for i in range(len(obj.jobs))]
        #Adds the legend to the chart
        plt.legend(handles=patches)
        #Displays the Gantt chart
        plt.show()

# Main program
jobs, num_machines = getInputFromUser()
GA = JobShopGA(jobs, num_machines) #instance from JobshopGA class
best_schedule, best_makespan = GA.run()
GA.create_gantt_chart(best_schedule)
