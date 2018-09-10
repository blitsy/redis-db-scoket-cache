import SocketServer
import redis
import json

# Init Redis
try:

    r = redis.StrictRedis(
        host='localhost',
        port=6379,
        db=1
    )

    print "Connected to Redis!"

except Exception as e:

    print("ERROR :( - Could not connect to Redis: " + str(e))
    raise Exception


# Gets the lane from tote stored in Redis
def get_tote_lane(tote):

    # Split the TOTE to get its ID
    temp = tote.split('-')

    # Print tote ID
    print "Tote ID: " + str(temp[1])

    # Get the redis entry for this tote and print
    redis_entry = r.get(str(temp[1]))
    print "Redis Entry: " + str(redis_entry)

    # If no record, return 10
    if redis_entry is None:

        print "No redis entry for TOTE-" + str(temp[1])
        return 10

    # Parse the redis response
    json_res = json.loads(redis_entry)

    # Get the lane from the redis response and print
    lane = json_res['lane']
    print "TOTE assigned to putwall #: " + str(lane)

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
                print "{} wrote:".format(self.client_address[0])
                print self.data

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

                except Exception as e:

                    message = "Invalid message received from client.  Expecting nnn,TOTE-nnnn. Error:" + str(e)
                    self.request.sendall(message)

        except Exception as e:

            print str(e)


if __name__ == "__main__":

    # Set the host and port
    HOST, PORT = "", 9000

    # Create the server
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate server and run indefinitely
    server.serve_forever()
