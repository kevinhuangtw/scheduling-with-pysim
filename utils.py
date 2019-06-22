class Job:
    def __init__(self, id, arrival_time=0):
        self.id = id
        self.tasks = []
        self.arrival_time = arrival_time

    def add_task(self, task):
        task.job = self
        if len(self.tasks) > 0:
            task.pre_task = self.tasks[-1]
        self.tasks.append(task)

    def add_tasks_to_machine(self, machines):
        for task in self.tasks:
            machines[task.machine_id].tasks.append(task)


class Task:
    def __init__(self, machine_id, duration, order=None):
        self.machine_id = machine_id
        self.duration = duration
        self.order = order
        self.job = None

        self.start = None
        self.end = None
        self.done = None  # self.env.event()
        self.pre_task = None

    def get_remain_time(self):
        for i, _task in enumerate(self.job.tasks):
            if self is _task:
                return sum([t.duration for t in self.job.tasks[i:]])
        else:
            return None

    def __str__(self):
        return '(job{} machine{} duration:{})'.format(
            self.job.id, self.machine_id, self.duration)


class Selector:
    def __init__(self, tasks):
        self.tasks = tasks

    def get_tasks_available(self):
        available = []
        for task in self.tasks:
            if task.pre_task is not None:
                if task.pre_task.done.triggered:  # 前個已經做完
                    available.append(task)
            else:  # 第一個task(不用等)
                available.append(task)
        return available

    def FIFO(self, tasks):
        return tasks[0]

    def SPT(self, tasks):
        task = min(tasks, key=lambda x: x.get_remain_time())
        return task

    def LIFO(self, tasks):
        return tasks[-1]

    def get_task(self, rule):
        tasks = self.get_tasks_available()

        if tasks:
            return getattr(self, rule)(tasks)
        else:
            return None


class Machine:
    def __init__(self, id, env, rule):
        self.id = id
        self.env = env
        self.tasks = []
        self.rule = rule

    def process(self):
        while True:
            selector = Selector(self.tasks)
            task = selector.get_task(self.rule)

            if task is not None:
                task.start = self.env.now
                yield self.env.timeout(task.duration)
                task.end = self.env.now
                task.done.succeed()
                self.tasks.remove(task)

                print('{}~{} machine{} 完成 job{}'.format(
                    self.env.now - task.duration,
                    self.env.now, task.machine_id, task.job.id))
            else:
                yield self.env.timeout(1)
