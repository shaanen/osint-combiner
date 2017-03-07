import datetime


class TimeTracker:

    start_time = datetime.datetime.now()

    def __init__(self):
        self.start_time = datetime.datetime.now()
        self.print_start_time()

    def get_start_time(self):
        return self.start_time

    def print_start_time(self):
        print('Start: ' + str(self.get_start_time().strftime("%Y-%m-%d %H:%M:%S")))

    @staticmethod
    def __get_time_difference(start, end):
        elapsed_time = end - start
        return divmod(elapsed_time.days * 86400 + elapsed_time.seconds, 60)

    def print_elapsed_time(self):
        now = datetime.datetime.now()
        elapsed_time = self.__get_time_difference(self.start_time, now)
        print('Elapsed: %d minutes, %d seconds' % (elapsed_time[0], elapsed_time[1]))

    def print_statistics(self):
        now = datetime.datetime.now()
        elapsed_time = self.__get_time_difference(self.start_time, now)
        self.print_start_time()
        print('Now: ' + str(now.strftime("%Y-%m-%d %H:%M:%S")))
        print('Elapsed: %d minutes, %d seconds' % (elapsed_time[0], elapsed_time[1]))


