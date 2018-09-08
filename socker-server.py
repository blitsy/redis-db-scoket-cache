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

    # Get the redis entry for this tote
    redis_entry = r.get(str(temp[1]))

    # Parse the redis response
    json_res = json.loads(redis_entry)

    # Print redis entry
    print "Redis Entry: " + str(redis_entry)

    # Get the lane from the redis response and print
    lane = json_res['lane']
    print "TOTE assigned to putwall #: " + lane

    if lane is None:

        # No lane entry for this tote, send to lane 10
        res = 10

    else:

        # Lane is set, set return to lane
        res = lane

    # Retunr lane
    return res


class MyTCPHandler(SocketServer.BaseRequestHandler):

    """
    Request handler for server

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):

        # Get message from the client
        self.data = self.request.recv(1024).strip()

        # Print the host and message
        print "{} wrote:".format(self.client_address[0])
        print self.data

        try:

            # Split out the message by ,
            temp = self.data.split(',')

            # Get the lane assigned to tote
            lane = get_tote_lane(temp[1])

            # Construct return message
            message = temp[0] + "," + lane

        except Exception as e:

            message = "Invalid message received from client.  Expecting nnn,TOTE-nnnn" + str(e)

        # just send back the same data, but upper-cased
        self.request.sendall(message)


if __name__ == "__main__":

    # Set the host and port
    HOST, PORT = "0.0.0.0", 9999

    # Create the server
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate server and run indefinitely
    server.serve_forever()
