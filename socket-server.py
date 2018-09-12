import SocketServer
import redis
import json
import logging
import time

# Init Logging
logging.basicConfig(filename='server_out.log', level=logging.DEBUG)


# Logging function
def write_log(message):

    ts = time.gmtime()
    time_readable = time.strftime("%c", ts)

    log_message = time_readable + ": " + message

    logging.info(log_message)

    print (log_message)


# Init Redis
try:

    r = redis.StrictRedis(
        host='localhost',
        port=6379,
        db=1
    )

    write_log("Connected to Redis!")

except Exception as e:

    write_log("ERROR :( - Could not connect to Redis: " + str(e))
    raise Exception


# Gets the lane from tote stored in Redis
def get_tote_lane(tote):

    # Respond with lane 10 for no scan message
    if tote == "?????????":

        return 10

    # Split the TOTE to get its ID
    temp = tote.split('-')

    # Print tote ID
    write_log("Tote ID: " + str(temp[1]))

    # Get the redis entry for this tote and print
    redis_entry = r.get(str(temp[1]))
    write_log("Redis Entry: " + str(redis_entry))

    # If no record, return 10
    if redis_entry is None:

        write_log("No redis entry for TOTE-" + str(temp[1]))
        return 10

    # Parse the redis response
    json_res = json.loads(redis_entry)

    # Get the lane from the redis response and print
    lane = json_res['lane']
    write_log("TOTE assigned to putwall #: " + str(lane))

    if lane is None:

        # No lane entry for this tote, return 10
        return 10

    else:

        # Lane is set, return lane
        return lane


class MyTCPHandler(SocketServer.BaseRequestHandler):

    """
    Request handler for server

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):

        try:

            while True:

                # Get message from the client
                self.data = self.request.recv(1024).strip()

                # Print the host and message
                write_log("{} sent:".format(self.client_address[0]))
                write_log(self.data)

                try:

                    # If message is not the heartbeat:
                    if self.data != "HB":

                        # Split out the message by ,
                        temp = self.data.split(',')

                        # Get the lane assigned to tote
                        lane = get_tote_lane(temp[1])

                        # Construct return message
                        message = temp[0] + "," + str(lane)
                        self.request.sendall(message)

                        write_log("Responded with: " + message)

                except Exception as e:

                    message = "000,10"
                    self.request.sendall(message)

        except Exception as e:

            write_log(str(e))


if __name__ == "__main__":

    # Set the host and port
    HOST, PORT = "0.0.0.0", 9000

    # Create the server
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate server and run indefinitely
    server.serve_forever()
