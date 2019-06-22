import simpy
import random

from utils import Job, Task, Machine
from simulator import JobShopSimulator

data1 = [
    (0, [(1, 3), (2, 2), (3, 3)]),  # 8 橘
    (0, [(1, 2), (3, 1), (2, 4)]),  # 7 綠
    (0, [(2, 4), (3, 5)])  # 9 紅
]

data2 = [
    (0, [(1, 5)]),
    (1, [(1, 7)]),
    (2, [(1, 6)])
]

datas = []
for _ in range(5):
    job = (random.randint(1, 5), [])

    for _ in range(3):
        job[1].append((random.randint(1, 3),
                       random.randint(1, 5)))
    datas.append(job)

data = datas

if __name__ == '__main__':
    # Task(machine_id, duration, order)
    jobs = [Job(id=i + 1, arrival_time=row[0])
            for i, row in enumerate(data)]

    for i, row in enumerate(data):
        for col in row[1]:
            jobs[i].add_task(Task(machine_id=col[0], duration=col[1]))

    def simulate(jobs, rule):
        simulator = JobShopSimulator(
            env=simpy.Environment(), jobs=jobs, rule=rule)
        simulator.run(until=50)
        simulator.plot()

    simulate(jobs, 'FIFO')
    simulate(jobs, 'LIFO')
    simulate(jobs, 'SPT')
