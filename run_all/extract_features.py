import argparse
import os
import sys
import shutil as st
from lib import utils


def extract_features(wav_filename, output_path, start_extract, end_extract):
    # defines
    temp_input_filename = utils.generate_tmp_filename('input')
    temp_label_filename = utils.generate_tmp_filename('labels')
    temp_features_filename = utils.generate_tmp_filename('features')
    temp_wav16_filename = utils.generate_tmp_filename('wav')

    # validation
    if not os.path.exists(wav_filename):
        print >> sys.stderr, 'Error: input path %s does not exists.' % wav_filename
        return

    # loop over all the files in the input dir
    if wav_filename.endswith('.wav'):
        try:
            # convert to 16K 16bit
            cmd = 'sox %s -r 16000 -b 16 %s' % (wav_filename, temp_wav16_filename)
            utils.easy_call(cmd)

            onset = (float(start_extract) + float(end_extract)) / 2
            offset = (float(start_extract) + float(end_extract)) / 2

            # =================== ACOUSTIC FEATURES =================== #
            # # write labels
            # label_file = wav_filename.replace('.wav', label_suffix)
            # fid = open(label_file, 'w')
            # fid.write('1 2\n')
            # fid.write('%s %s %s\n' % (str(1), str(1), str(1)))
            # fid.close()

            # creating the files
            input_file = open(temp_features_filename, 'wb')  # open the input file for the feature extraction
            features_file = open(temp_input_filename, 'wb')  # open file for the feature list path
            labels_file = open(temp_label_filename, 'wb')  # open file for the labels

            # write the data
            input_file.write(
                    '"' + temp_wav16_filename + '" ' + str('%.8f' % float(start_extract)) + ' ' + str(
                            float(end_extract)) + ' ' + str(
                            '%.8f' % float(onset)) + ' ' + str('%.8f' % float(offset)))
            features_file.write(output_path.replace('.wav', '.txt'))

            input_file.close()
            features_file.close()
            labels_file.close()

            command = "./sbin/VotFrontEnd2 %s %s %s" % (input_file.name, features_file.name, labels_file.name)
            utils.easy_call(command)

            # remove leftovers
            os.remove(temp_input_filename)
            os.remove(temp_label_filename)
            os.remove(temp_features_filename)
            os.remove(temp_wav16_filename)
        except:
            print wav_filename


if __name__ == "__main__":
    # -------------MENU-------------- #
    # command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("audio_path", help="The path to the audio file")
    parser.add_argument("output_path", help="The path to save the features")
    parser.add_argument("start_extract", help="The time-stamp to start extracting features")
    parser.add_argument("end_extract", help="The time-stamp to end extracting features")
    args = parser.parse_args()

    # main function
    extract_features(args.audio_path, args.output_path, args.start_extract, args.end_extract)
