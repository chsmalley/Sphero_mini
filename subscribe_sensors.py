import sys
import zmq
import random
import time


if __name__ == '__main__':
    port = "5556"
    topic = 10000

    # Socket to talk to server
    context = zmq.Context()
    socket = context.socket(zmq.SUB)

    print("Collecting updates from weather server...")
    socket.connect("tcp://localhost:%s" % port)
    # Subscribe to zipcode, default is NYC, 10001
    topicfilter = "10000"
    socket.setsockopt_string(zmq.SUBSCRIBE, topicfilter)

    while True:
        try:
            string = socket.recv()
            topic, messagedata = string.split()
            print("{} {}".format(topic, messagedata))
        except KeyboardInterrupt:
            break
    print("program complete")
