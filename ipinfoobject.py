from base import dict_add_source_prefix
from datetime import datetime, timezone
from netaddr import IPNetwork
import threading
import requests
import json
from datetime import datetime, timezone
import time
import os
import queue
from base import get_cidr_from_user_input
from base import parse_all_cidrs_from_file
from base import es_get_distinct_ips


class IpInfoObject:

    def __init__(self):
        """Return an IpInfoObject initialised with API key"""
        self.url = 'http://ipinfo.dutchsec.nl/submit'
        self.headers = {'Content-Type': 'text/plain', 'Accept': 'text/json'}

    @staticmethod
    def to_es_convert(self, input_dict):
        """Return dict ready to be sent to Logstash."""

        # rename location elements
        input_dict['location'] = {}
        try:
            input_dict['location']['country'] = input_dict['geo']['country']['name']
        except KeyError:
            pass
        try:
            input_dict['location']['country_code'] = input_dict['geo']['country']['iso_code']
        except KeyError:
            pass
        del input_dict['geo']['country']
        try:
            input_dict['location']['city'] = input_dict['geo']['city']
        except KeyError:
            pass

        # rename latitude and longitude for geoip
        try:
            input_dict['location']['geo'] = {}
            input_dict['location']['geo']['lat'] = input_dict['geo']['location']['latitude']
            input_dict['location']['geo']['lon'] = input_dict['geo']['location']['longitude']
        except KeyError:
            pass
        del input_dict['geo']['location']
        try:
            if not input_dict['geo']:
                del input_dict['geo']
        except KeyError:
            pass

        # prefix non-nested fields with 'ipinfo'
        input_dict = dict_add_source_prefix(input_dict, 'ipinfo')
        return input_dict

    @staticmethod
    def cidr_to_ipinfo(cidr_input, path_output_file):
        """Makes IpInfo request for every given IP and writes to given outputfile"""

        @staticmethod
        class GetIpInfoThread(threading.Thread):
            """Thread which does one GET request at a time"""
            def __init__(self, q):
                threading.Thread.__init__(self)
                self.q = q
                self.data = ''

            def run(self):
                global done_counter
                global connection_err_counter
                global timeout_err_counter
                while not exitFlag:
                    queueLock.acquire()
                    if not workQueue.empty():
                        self.data = self.q.get()
                        queueLock.release()
                        got_valid_response = False
                        while not got_valid_response:
                            try:
                                resp = requests.post(self.url, headers=self.headers, data=str(self.data), timeout=20)
                                resp_json = json.loads(resp.text)
                                resp_json['timestamp'] = str(datetime.now(timezone.utc).isoformat())
                                result_list.append(json.dumps(resp_json))
                                got_valid_response = True
                                with done_counter_lock:
                                    done_counter += 1
                            except requests.exceptions.ConnectionError:
                                with connection_err_lock:
                                    connection_err_counter += 1
                            except requests.exceptions.ReadTimeout:
                                with timeout_err_lock:
                                    timeout_err_counter += 1
                            finally:
                                print('\r' + str(done_counter) + ' done, ' + str(
                                    connection_err_counter) + ' connection errors, '
                                      + str(timeout_err_counter) + ' timeouts', end='')
                    else:
                        queueLock.release()
                    time.sleep(1)

        done_counter = 0
        done_counter_lock = threading.Lock()
        connection_err_counter = 0
        connection_err_lock = threading.Lock()
        timeout_err_counter = 0
        timeout_err_lock = threading.Lock()
        exitFlag = 0
        queueLock = threading.Lock()
        workQueue = queue.Queue(0)
        threads = []
        global exitFlag
        nr_threads = 0
        if cidr_input.size < 16:
            nr_threads = cidr_input.size
        else:
            nr_threads = 16
        if type(cidr_input) is IPNetwork:
            print('CIDR ' + str(cidr_input) + ' (' + str(cidr_input.size) + ' total)')
        start_time = time.time()

        for num in range(1, nr_threads + 1):
            thread = GetIpInfoThread(workQueue)
            thread.start()
            threads.append(thread)

        # Fill the queue
        with queueLock:
            for ip in cidr_input:
                workQueue.put(ip)

        # Wait for queue to empty
        while not workQueue.empty():
            pass

        # Notify threads it's time to exit
        exitFlag = 1

        # Wait for all GetIpInfoThreads to complete
        for t in threads:
            t.join()
        print('')

        # Print useful statistics
        print(str((connection_err_counter + timeout_err_counter)) + ' times retried an IP')
        print(str(round((time.time() - start_time))) + ' seconds needed for getting all responses')

        # Write all responses to file
        with open(path_output_file, 'a') as output_file:
            # Writing newline if file is not empty
            if os.stat(path_output_file).st_size != 0:
                output_file.write('\n')

            output_file.write('\n'.join(result_list))
        print('\r' + str(len(result_list)) + ' results written in ' + path_output_file, end='')

    @staticmethod
    def get_input_choice(self):
        """Returns input_choice represented as integer"""
        items = {'1': 'console_input', '2': 'cidr_file_input', '3': 'elasticsearch_input'}
        input_choice = '0'
        while input_choice not in items:
            input_choice = input("Console input[1], CIDR file input[2] or Elasticsearch input[3]?")
        return int(input_choice)



