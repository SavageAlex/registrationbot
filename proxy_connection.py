import time
import socket
import logging

server = "proxy.voip.plus"
port = 8080
knocking_ports = [15236, 12236]

def port_knocking(server, ports):
    logging.info("Knocking")

    for port in ports:
        logging.info(f'Knocking to port: {server}: {port}')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        with sock:
            sock.settimeout(0)
            sock.connect_ex((server, port)) # don't need do connect
            # sock.send(PASSPHRASE.encode('hex'))
            time.sleep(0.2)


def check_proxy_connection(server=server, port=port, knocking_ports=knocking_ports, logging_level=logging.DEBUG):
    logging.basicConfig(level=logging_level, filename='data.log', filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
    # Knocking server's IP address
    host = (server, port)
    port_opened = False
    i=0
    while not port_opened:

        logging.info("Check connection")
        a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        with a_socket:
            logging.info(f'While loop, host: {host}')
            a_socket.settimeout(0.5)
            result_of_check = a_socket.connect_ex(host)
            logging.info("checked")
            if result_of_check == 0:
                logging.info("Port is open")
                port_opened = True
                return port_opened
            else:
                logging.info("Port is closed")
                if i>0:
                    logging.info("\nWaiting 10s\n")
                    time.sleep(10)
                port_knocking(server, knocking_ports)
            i+=1