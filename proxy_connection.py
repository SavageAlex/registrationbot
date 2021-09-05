import time
import socket


server = "proxy.voip.plus"
port = 8080
knocking_ports = [15236, 12236]

def port_knocking(server, ports):
    print("Knocking")

    for port in ports:
        print(f'Knocking to port: {server}: {port}')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        with sock:
            sock.settimeout(0)
            sock.connect_ex((server, port)) # don't need do connect
            # sock.send(PASSPHRASE.encode('hex'))
            time.sleep(0.2)


def check_proxy_connection(server=server, port=port, knocking_ports=knocking_ports):
    # Knocking server's IP address
    host = (server, port)
    port_opened = False
    i=0
    while not port_opened:

        print("Check connection")
        a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        with a_socket:
            print(f'While loop, host: {host}')
            a_socket.settimeout(0.5)
            result_of_check = a_socket.connect_ex(host)
            print("checked")
            if result_of_check == 0:
                print("Port is open")
                port_opened = True
                return port_opened
            else:
                print("Port is closed")
                if i>0:
                    print("\nWaiting 10s\n")
                    time.sleep(10)
                port_knocking(server, knocking_ports)
            i+=1