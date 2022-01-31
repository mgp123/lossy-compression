import argparse 
from huffman_codes.encoding import encode, decode

if __name__ == "__main__":

    ap = argparse.ArgumentParser()
    ap.add_argument("method", choices=["encode", "decode"], help="encode or decode an image")
    ap.add_argument("path_in", help="path to input")
    ap.add_argument("path_out", help="path for saving output")
    ap.add_argument("--verbose", help="print encoding statistics", default = False, const=True, action='store_const')	

    args = vars(ap.parse_args())

    method, path_in, path_out = args["method"], args["path_in"], args["path_out"]
    verbose = args["verbose"]

    if  method == "encode":
        encode(path_in, path_out, verbose=verbose)
    else:
        decode(path_in, path_out, verbose=verbose)
