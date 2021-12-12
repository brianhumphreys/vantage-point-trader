class MetaTask1(type):
    def __init__(cls, name, bases, clsdict):
        if 'run' in clsdict:
            print(clsdict['run'])
            def new_run(self):
                print('before 1')
                getattr['run'](self)
                print('after 1')

            new_run(cls)
            # try:
            #     decorated = clsdict['run']
            setattr(cls, 'run', new_run)
            print(clsdict['run'])

class MetaTask2(MetaTask1):
    def __init__(cls, name, bases, clsdict):
        super(MetaTask2, cls).__init__(name, bases, clsdict)
        print()
        if 'run' in clsdict:
            print(clsdict['run'])
            def new_run(self):
                print('before 2')
                clsdict['run'](self)
                print('after 2')

            new_run(cls)
            setattr(cls, 'run', new_run)
            print(clsdict['run'])

class Task1(object, metaclass=MetaTask1):
    # For Python2: remove metaclass=MetaTask above and uncomment below:
    # __metaclass__ = MetaTask
    pass

class Task2(object, metaclass=MetaTask2):
    # For Python2: remove metaclass=MetaTask above and uncomment below:
    # __metaclass__ = MetaTask
    pass


class MyTask(Task2):
    def run(self):
        print('shit')
        #successful override!
        pass

task = MyTask()
# task.run()