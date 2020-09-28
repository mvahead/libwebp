#!/usr/bin/python
#
# ORBCOMM
#
# Aug 2016 by: Marcelo Varanda
# ORBCOMM All rights reserved
#
#
# requires:  intelHex module
#            to install use: c:\Python27\Scripts\pip.exe install intelhex (or whatever you pip is)
#            more details check: https://github.com/bialix/intelhex

import sys
import intelhex
import os

#from docutils.nodes import header

MAX_BIN_SIZE = 1024 * 1024 * 2 # limit in 2Mbytes for now


FILE_HEADER = """
/******************************
 *
 * Auto generated file by gen_c_image.py
 *
 * !!! DO NOT EDIT THIS FILE !!!
 *
 * original file: $original$
 *
 ******************************/
 
#define $name$Ver "$version$"

#define $name$Block $block$

#define $name$Address "$$address$"

#define $name$ImageSize $size$;
 
const char $name$Image [$size$] = {
  """

baseaddr = 0
image_name = ""
  
def get_version_from_filename(filename):
  #expected format: "s140.host.002.001.0002.hex"
  #              or "s140_nrf52_6.1.1_softdevice.hex"
  #              or "n52840.bl.002.001.0002.hex"
  # output format: "S140.HOST.002.001.0002"
  return "?"

def get_bytes_from_file(filename):
  try:
    d = open(filename, "rb").read()
  except IOError as e:
    print (e)
    sys.exit(2)
  return d
  
def get_bytes_from_hex_file(filename):
  global baseaddr
  try:
    ih = intelhex.IntelHex(filename)
  except intelhex.HexRecordError as e:
    print (e)
    sys.exit(2)
  except IOError as e:
    print (e)
    sys.exit(2)
  if image_name != "BleBoot":
    if ih.maxaddr() - ih.minaddr() > MAX_BIN_SIZE:
      print("protection: Hex file would exceed limit MAX_BIN_SIZE. Change it if indeed required.")
      print("min addr = " + hex(ih.minaddr()) )
      print("max addr = " + hex(ih.maxaddr()) )    
      sys.exit(2)
  baseaddr = ih.minaddr()
  temp_filename = os.path.splitext(filename)[0] + ".$$$"
  if image_name != "BleBoot":
    intelhex.hex2bin(filename, temp_filename)
  else:
    s = ih.segments() #get segments as bootloader ROM is the first segment
    intelhex.hex2bin(filename, temp_filename, s[0][0], s[0][1] - 1)

  ret = open(temp_filename, "rb").read()
  os.remove(temp_filename)
  return ret
  
def usage():
  print("Usage:\r\n   gen_c_image -i inputfile -o outputfile [-app | -firmware | -boot] -v version <-hex>")

def char2hex(c):
  if sys.version_info[0] < 3:
    return hex(ord(c))
  else:
    return hex(c)
    
def main():
  global baseaddr
  global image_name
  input_name = None
  output_name = None
  image_name = None

  hex_flag = False
  version = "?"

  i = 1
  
  if len(sys.argv) < 7:
    print("requires at least 8 parameters")
    usage()
    sys.exit(2)
    
  nargs = len(sys.argv)
  while i < nargs:
    arg = sys.argv[i]
    if arg in ("h", "-h", "-help", "--help", "?"):
      usage()
      sys.exit(2)

    elif arg == "-i":
      if (i + 1) < nargs:
        input_name = sys.argv[i+1]
        i = i + 2
        continue
      else:
        print ("expected name after -i option")
        sys.exit(2)
      
    elif arg == "-o":
      if (i + 1) < nargs:
        output_name = sys.argv[i+1]
        i = i + 2
        continue
      else:
        print ("expected name after -o option")
        sys.exit(2)
      
    elif arg == "-v":
      if (i + 1) < nargs:
        version = sys.argv[i+1]
        i = i + 2
        continue
      else:
        print ("expected version string after -v option")
        sys.exit(2)
      
    elif arg == "-hex":
      hex_flag = True
      
    elif arg == "-app":
      if image_name != None:
        print("-app: image type already set\r\n")
        sys.exit(2)
      image_name = "BleApp"
      block = "1"
      
    elif arg == "-firmware":
      if image_name != None:
        print("-firmware: image type already set\r\n")
        sys.exit(2)
      image_name = "BleFirmware"
      block = "0"
      
    elif arg == "-boot":
      if image_name != None:
        print("-boot: image type already set\r\n")
        sys.exit(2)
      image_name = "BleBoot"
      block = "2"
      
    else:
      print("parameter " + arg + " not valid")
      usage()
      sys.exit(2)

    i = i+1

  if input_name == None:
    print("input not provided")
    usage()
    return

  if output_name == None:
    print("output not provided")
    usage()
    return

  if image_name == None:
    print("image_name not provided")
    usage()
    return

  if image_name == None:
    print("version not provided")
    usage()
    return

  print("input: " + input_name)
  print("output: " + output_name)
  print("name: " + image_name)
  print("hex: " + str(hex_flag))
  print("version:" + version)
  
  if hex_flag == True:
    dt_i = get_bytes_from_hex_file(input_name)
  else:
    dt_i = get_bytes_from_file(input_name)
  
  
  
  #dt_o = FILE_HEADER
  
  dt_o = FILE_HEADER.replace("$original$", input_name)
  dt_o = dt_o.replace("$name$", image_name)
  dt_o = dt_o.replace("$size$", str(len(dt_i)))
  dt_o = dt_o.replace("$address$", hex(baseaddr)[2:])
  dt_o = dt_o.replace("$version$", version)
  dt_o = dt_o.replace("$block$", block)    
  block = 1 #default is App
      
  counter = 16
  
  for i in range(len(dt_i)):
    dt_o = dt_o + char2hex(dt_i[i]) + ", "
    counter = counter - 1
    if counter == 0:
      counter = 16
      dt_o = dt_o + '\r\n  '
  dt_o = dt_o + '\r\n};\r\n'
  # print(dt_o)
  
  hf = open(output_name, "w")
  hf.write(dt_o)
  hf.close()

if __name__ == "__main__":
  print("\nFile to C byte array converter v0.01")
  main()
  print("\n")
