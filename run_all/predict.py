
import argparse
import os
import sys
from extract_features import extract_features
from label2textgrid import create_text_grid
from lib import utils
from post_process import post_process
from run_backend import run
from lib.utils import *
from lib.textgrid import *

def predict(wav_path, textgrid_path, start_extract, end_extract):
    tmp_feature_file = generate_tmp_filename('features')
    tmp_prob_file = generate_tmp_filename('prob')
    tmp_predict_file = generate_tmp_filename('prediction')
    if not os.path.exists(wav_path):
        print >>sys.stderr, "wav file %s does not exits" % wav_path
        return
    length = utils.get_wav_file_length(wav_path)

    print '\n1) Extracting features and classifying ...'
    extract_features(wav_path, tmp_feature_file, start_extract, end_extract)
    run(tmp_feature_file, tmp_prob_file)
    print '\n3) Extract Durations ...'
    post_process(tmp_prob_file, tmp_predict_file)
    print '\n4) Writing TextGrid file to %s ...' % textgrid_path
    create_text_grid(tmp_predict_file, textgrid_path, length, float(start_extract))

    # remove leftovers
    os.remove(tmp_feature_file)
    os.remove(tmp_prob_file)
    os.remove(tmp_predict_file)


def predict_from_textgrid(wav_path, textgrid_path):
    tmp_feature_file = generate_tmp_filename('features')
    tmp_prob_file = generate_tmp_filename('prob')
    tmp_predict_file = generate_tmp_filename('prediction')
    if not os.path.exists(wav_path):
        print >>sys.stderr, "wav file %s does not exits" % wav_path
        return
    length = utils.get_wav_file_length(wav_path)

    # read the whole input text grid
    textgrid = TextGrid()
    textgrid.read(textgrid_path)
    tier_names = textgrid.tierNames()

    window_xmin = list()
    window_xmax = list()
    window_mark = list()
    tier_index = tier_names.index("word")
    # print all its interval, which has some value in their description (mark)
    for (i, interval) in enumerate(textgrid[tier_index]):
        if re.search(r'\S', interval.mark()):
            # define processing window
            window_xmin.append(max(textgrid.xmin(), textgrid[tier_index][i].xmin() - 0.1))
            window_xmax.append(min((textgrid[tier_index][i].xmin() + 0.1, textgrid.xmax())))
            window_mark.append(i)

    # prepare TextGrid
    window_tier = IntervalTier(name='window', xmin=textgrid.xmin(), xmax=textgrid.xmax())
    window_tier.append(Interval(textgrid.xmin(), window_xmin[0], ''))
    for i in xrange(0, len(window_xmin)-1):
        window_tier.append(Interval(window_xmin[i], window_xmax[i], window_mark[i]))
        window_tier.append(Interval(window_xmax[i], window_xmin[i+1], ''))
    window_tier.append(Interval(window_xmin[-1], window_xmax[-1], window_mark[-1]))
    window_tier.append(Interval(window_xmax[-1], textgrid.xmax(), ''))

    # write textgrid
    textgrid.append(window_tier)
    textgrid.write(textgrid_filename)



    print '\n1) Extracting features and classifying ...'
    extract_features(wav_path, tmp_feature_file, start_extract, end_extract)
    run(tmp_feature_file, tmp_prob_file)
    print '\n3) Extract Durations ...'
    post_process(tmp_prob_file, tmp_predict_file)
    print '\n4) Writing TextGrid file to %s ...' % textgrid_path
    create_text_grid(tmp_predict_file, textgrid_path, length, float(start_extract))

    # remove leftovers
    os.remove(tmp_feature_file)
    os.remove(tmp_prob_file)
    os.remove(tmp_predict_file)


if __name__ == "__main__":
    # -------------MENU-------------- #
    # command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("wav_path", help="The path to the wav file")
    parser.add_argument("textgrid_path", help="The path to save new text-grid file")
    parser.add_argument("--start_extract", default=0.0, help="The time-stamp to start extracting features")
    parser.add_argument("--end_extract", default=-1.0, help="The time-stamp to end extracting features")
    parser.add_argument("--windows_tier", default="window", help="optional tier name for search window")
    args = parser.parse_args()

    # main function
    if args.start_extract > 0 and args.end_extract > 0:
        predict(args.wav_path, args.textgrid_path, args.start_extract, args.end_extract)
    else:
        predict_from_textgrid(args.wav_path, args.textgrid_path, args.windows_tier)