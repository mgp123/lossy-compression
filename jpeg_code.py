import argparse 
from jpeg.encoding import encode, decode

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='encode or decode an image',dest='method')
    parser.add_argument("path_in", help="path to input")
    parser.add_argument("path_out", help="path for saving output")
    parser.add_argument("--verbose", help="print encoding statistics", default = False, const=True, action='store_const')	

    # create the parser for the "bar" command
    parser_a = subparsers.add_parser('encode')
    parser_a.add_argument('--quant', type=int, default=-45, help="level of quantization applied to the image. Lower values indicate less quantization. Use integers ranging from -60 to 30 for good results")
    parser_a.add_argument('--sub_rows', type=int,  default = 2, help="chrominance subsampling in the direction of the rows")
    parser_a.add_argument('--sub_columns', type=int,  default = 2, help="chrominance subsampling in the direction of the columns")

    parser_b = subparsers.add_parser('decode')

    args = vars(parser.parse_args())


    method, path_in, path_out = args["method"], args["path_in"], args["path_out"]
    verbose = args["verbose"]


    if  method == "encode":
        subsample_rows = args["sub_rows"]
        subsample_columns = args["sub_columns"]
        quant_level = args["quant"]
        encode(
            path_in, path_out,
            db_2_quantization_multiplier=quant_level,
            subsample_coef_rows=subsample_rows,
            subsample_coef_columns=subsample_columns,
            verbose=verbose)
    else:
        decode(path_in, path_out, verbose=verbose)
