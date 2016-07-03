
import argparse
import os
import sys
from extract_features import extract_features
from label2textgrid import create_text_grid
from lib import utils
from post_process import post_process
from run_backend import run
from lib.utils import *


def predict(input_path, output_path, start_extract, end_extract):
    tmp_feature_file = generate_tmp_filename('features')
    tmp_prob_file = generate_tmp_filename('prob')
    tmp_predict_file = generate_tmp_filename('prediction')
    if not os.path.exists(input_path):
        print >>sys.stderr, "wav file %s does not exits" % input_path
        return
    length = utils.get_wav_file_length(input_path)

    print '\n1) Extracting features and classifying ...'
    extract_features(input_path, tmp_feature_file, start_extract, end_extract)
    run(tmp_feature_file, tmp_prob_file)
    print '\n3) Extract Durations ...'
    post_process(tmp_prob_file, tmp_predict_file)
    print '\n4) Writing TextGrid file to %s ...' % output_path
    create_text_grid(tmp_predict_file, output_path, length, float(start_extract))

    # remove leftovers
    os.remove(tmp_feature_file)
    os.remove(tmp_prob_file)
    os.remove(tmp_predict_file)



if __name__ == "__main__":
    # -------------MENU-------------- #
    # command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("input_path", help="The path to the wav file")
    parser.add_argument("output_path", help="The path to save new text-grid file")
    parser.add_argument("start_extract", help="The time-stamp to start extracting features")
    parser.add_argument("end_extract", help="The time-stamp to end extracting features")
    args = parser.parse_args()

    # main function
    predict(args.input_path, args.output_path, args.start_extract, args.end_extract)
