import numpy as np
import matplotlib.pyplot as plt

from simpy_howard.demo.utils import Machine


class JobShopSimulator:
    def __init__(self, env, jobs, rule='FIFO'):
        self.env = env
        self.jobs = jobs
        self.machines = {}  # {id: Machine()}
        self.rule = rule
        self.init_machines(self.rule)

        # for m in self.machines.values():
        #     for t in m.tasks:
        #         print(str(t), end='')
        #     print()

    def init_machines(self, rule):
        for job in self.jobs:
            for task in job.tasks:
                task.done = self.env.event()

                self.machines.setdefault(
                    task.machine_id, Machine(
                        task.machine_id, self.env, rule=rule))

        # sort by orders
        # for machine in self.machines.values():
        #     machine.tasks.sort(key=lambda x: x.order)

    def jobs_arrive(self):
        jobs_remain = self.jobs.copy()

        while True:
            for job in reversed(jobs_remain):
                if job.arrival_time == self.env.now:
                    job.add_tasks_to_machine(self.machines)
                    jobs_remain.remove(job)

            yield self.env.timeout(1)

    def run(self, until):
        self.env.process(self.jobs_arrive())

        for machine in self.machines.values():
            self.env.process(machine.process())
        self.env.run(until)

    def plot(self):
        _barhs = {}
        y = ['machine' + str(i + 1) for i in range(len(self.machines))]
        plt.barh(y, [0] * len(self.machines))
        # https://matplotlib.org/3.1.0/gallery/color/named_colors.html

        for i, job in enumerate(self.jobs):
            y, x_start, x_width = [], [], []
            for task in job.tasks:
                y.append('machine' + str(task.machine_id))
                x_start.append(task.start)
                x_width.append(task.duration)
            _barh = plt.barh(y, x_width, left=x_start,
                             height=1, alpha=0.8)
            _barhs['job{} a:{}'.format(job.id, job.arrival_time)] = _barh

        plt.legend(handles=list(_barhs.values()),
                   labels=list(_barhs.keys()), loc='best')
        plt.title('({}) Max Span: {}'.format(
            self.rule, max([t.end for job in self.jobs for t in job.tasks])))
        plt.show()
