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
        print >> sys.stderr, "wav file %s does not exits" % wav_path
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


def predict_from_textgrid(wav_path, textgrid_path, tier, csv_outfile):
    tmp_feature_file = generate_tmp_filename('features')
    tmp_prob_file = generate_tmp_filename('prob')
    tmp_predict_file = generate_tmp_filename('prediction')
    # defines
    msc_2_sec = 0.001

    if not os.path.exists(wav_path):
        print >> sys.stderr, "wav file %s does not exits" % wav_path
        return
    length = utils.get_wav_file_length(wav_path)

    # read the whole input text grid
    textgrid = TextGrid()
    textgrid.read(textgrid_path)
    tier_names = textgrid.tierNames()

    tier_index = tier_names.index(tier)

    # print all its interval, which has some value in their description (mark)
    for (i, interval) in enumerate(textgrid[tier_index]):
        if re.search(r'\S', interval.mark()):
            # define processing window
            start_extract = textgrid[tier_index][i].xmin()
            end_extract = textgrid[tier_index][i].xmax()

    print '\n1) Extracting features and classifying ...'
    extract_features(wav_path, tmp_feature_file, start_extract, end_extract)

    print '\n2) Make predictions ...'
    run(tmp_feature_file, tmp_prob_file)

    print '\n3) Extract Durations ...'
    p = post_process(tmp_prob_file, tmp_predict_file)

    print '\n4) Writing TextGrid file to %s ...' % textgrid_path
    onset = -1
    offset = -1
    prevoiced = -1

    # prepare TextGrid
    vot_tier = IntervalTier(name='vot', xmin=0.0, xmax=float(length))
    if p[1] == -1:
        onset = p[0]
        offset = p[2]

        vot_tier.append(Interval(0, float(onset) * msc_2_sec + start_extract, ""))
        vot_tier.append(
            Interval(float(onset) * msc_2_sec + start_extract, float(offset) * msc_2_sec + start_extract, "DeepVOT"))
        vot_tier.append(Interval(float(offset) * msc_2_sec + start_extract, float(length), ""))
        # write textgrid
        textgrid.append(vot_tier)
        textgrid.write(textgrid_path)
    if p[1] != -1:
        prevoiced = p[0]
        onset = p[1]
        offset = p[2]

        vot_tier.append(Interval(0, float(prevoiced) * msc_2_sec + start_extract, ""))
        vot_tier.append(Interval(float(prevoiced) * msc_2_sec + start_extract, float(onset) * msc_2_sec + start_extract,
                                 "prevoicing"))
        vot_tier.append(
            Interval(float(onset) * msc_2_sec + start_extract, float(offset) * msc_2_sec + start_extract, "DeepVOT"))
        vot_tier.append(Interval(float(offset) * msc_2_sec + start_extract, float(length), ""))
        # write textgrid
        textgrid.append(vot_tier)
        textgrid.write(textgrid_path)

    # remove leftovers
    os.remove(tmp_feature_file)
    os.remove(tmp_prob_file)
    os.remove(tmp_predict_file)

    if csv_outfile:
        with open(csv_outfile, 'w') as f:
            f.write("FILE, PREVOICE TIME, START_TIME, END_TIME\n")
            f.write("%s, %f, %f, %f\n" % (wav_path, (float(prevoiced) * msc_2_sec + start_extract) * 10,
                                          (float(onset) * msc_2_sec + start_extract) * 10,
                                          (float(offset) * msc_2_sec + start_extract) * 10))


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
