from operator import itemgetter
import matplotlib.pyplot as plt
from scipy.io import wavfile as wav
import matplotlib.mlab as mlab

import hashlib
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

#from termcolor import colored
from scipy.ndimage.filters import maximum_filter
from scipy.ndimage.morphology import (generate_binary_structure, iterate_structure, binary_erosion)
from operator import itemgetter


rate, data1 = wav.read('Group4_Song1_Full.wav')
data = list(map(itemgetter(0), data1))
print(len(data),data[100000:100010])
# plt.specgram(data,NFFT=4096,Fs=44100,window=mlab.window_hanning,noverlap=int(4096 * 0.5))
# plt.show()

# a = ("John", "Charles", "Mike")
# b = ("Jenny", "Christy", "Monica", "Vicky")
# y=zip(a,b)
# coco=list(zip(a,b))
# print(list(y))
# print(len(coco))
# x = [(27, 283), (27, 424), (27, 468), (27, 557), (27, 617), (27, 860), (27, 973), (27, 1065), (27, 1183), (27, 1255)]
# print(x,len(x))

# initializing string
str1 = "GeeksforGeeks"
  
# encoding GeeksforGeeks using encode()
# then sending to SHA1()
result = hashlib.sha1(str1.encode())

# printing the equivalent hexadecimal value.
print("The hexadecimal equivalent of SHA1 is : ")
print(result.hexdigest())
def create_generator():
    mylist = range(3)
    for i in mylist:
        print(i)
        yield i*i
mygenerator = create_generator() # create a generator
print(mygenerator) # mygenerator is an object!
# for i in mygenerator:
#     print(i)

IDX_FREQ_I = 0
IDX_TIME_J = 1

# Sampling rate, related to the Nyquist conditions, which affects
# the range frequencies we can detect.
DEFAULT_FS = 44100

# Size of the FFT window, affects frequency granularity
DEFAULT_WINDOW_SIZE = 4096

# Ratio by which each sequential window overlaps the last and the
# next window. Higher overlap will allow a higher granularity of offset
# matching, but potentially more fingerprints.
DEFAULT_OVERLAP_RATIO = 0.5

# Degree to which a fingerprint can be paired with its neighbors --
# higher will cause more fingerprints, but potentially better accuracy.
DEFAULT_FAN_VALUE = 15

# Minimum amplitude in spectrogram in order to be considered a peak.
# This can be raised to reduce number of fingerprints, but can negatively
# affect accuracy.
DEFAULT_AMP_MIN = 10

# Number of cells around an amplitude peak in the spectrogram in order
# for Dejavu to consider it a spectral peak. Higher values mean less
# fingerprints and faster matching, but can potentially affect accuracy.
PEAK_NEIGHBORHOOD_SIZE = 20

# Thresholds on how close or far fingerprints can be in time in order =200
# to be paired as a fingerprint. If your max is too low, higher values of
# DEFAULT_FAN_VALUE may not perform as expected.
MIN_HASH_TIME_DELTA = 0
MAX_HASH_TIME_DELTA = 20

# If True, will sort peaks temporally for fingerprinting;
# not sorting will cut down number of fingerprints, but potentially
# affect performance.
PEAK_SORT = True

# Number of bits to throw away from the front of the SHA1 hash in the
# fingerprint calculation. The more you throw away, the less storage, but
# potentially higher collisions and misclassifications when identifying songs.
FINGERPRINT_REDUCTION = 20

def fingerprint(channel_samples, Fs=DEFAULT_FS,
                wsize=DEFAULT_WINDOW_SIZE,
                wratio=DEFAULT_OVERLAP_RATIO,
                fan_value=DEFAULT_FAN_VALUE,
                amp_min=DEFAULT_AMP_MIN,
                plots=False):

    # show samples plot
    print("in fingerprint")
    if plots:
      plt.plot(channel_samples)
      plt.title('%d samples' % len(channel_samples))
      plt.xlabel('time (s)')
      plt.ylabel('amplitude (A)')
      plt.show()
      plt.gca().invert_yaxis()

    # FFT the channel, log transform output, find local maxima, then return
    # locally sensitive hashes.
    # FFT the signal and extract frequency components

    # plot the angle spectrum of segments within the signal in a colormap
    arr2D = mlab.specgram(
        channel_samples,
        NFFT=wsize,
        Fs=Fs,
        window=mlab.window_hanning,
        noverlap=int(wsize * wratio))[0]

    # show spectrogram plot
    if plots:
      plt.plot(arr2D)
      plt.title('FFT')
      plt.show()

    # apply log transform since specgram() returns linear array
    arr2D = 10 * np.log10(arr2D) # calculates the base 10 logarithm for all elements of arr2D
    arr2D[arr2D == -np.inf] = 0  # replace infs with zeros

    # find local maxima
    local_maxima = get_2D_peaks(arr2D, plot=plots, amp_min=amp_min)
    #print(list(local_maxima)[10:20],len(list(local_maxima)))
    
    print("before hashing")

    return generate_hashes(list(local_maxima), fan_value=fan_value)

def get_2D_peaks(arr2D, plot=False, amp_min=DEFAULT_AMP_MIN):
    # http://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.morphology.iterate_structure.html#scipy.ndimage.morphology.iterate_structure
    struct = generate_binary_structure(2, 1)
    neighborhood = iterate_structure(struct, PEAK_NEIGHBORHOOD_SIZE)

    # find local maxima using our fliter shape
    local_max = maximum_filter(arr2D, footprint=neighborhood) == arr2D
    background = (arr2D == 0)
    eroded_background = binary_erosion(background, structure=neighborhood, border_value=1)

    # Boolean mask of arr2D with True at peaks
    detected_peaks = local_max ^ eroded_background

    # extract peaks
    amps = arr2D[detected_peaks]
    j, i = np.where(detected_peaks)

    # filter peaks
    amps = amps.flatten()
    peaks = zip(i, j, amps)
    peaks_filtered = [x for x in peaks if x[2] > amp_min]  # freq, time, amp

    # get indices for frequency and time
    frequency_idx = [x[1] for x in peaks_filtered]
    time_idx = [x[0] for x in peaks_filtered]

    # scatter of the peaks
    if plot:
      fig, ax = plt.subplots()
      ax.imshow(arr2D)
      ax.scatter(time_idx, frequency_idx)
      ax.set_xlabel('Time')
      ax.set_ylabel('Frequency')
      ax.set_title("Spectrogram")
      plt.gca().invert_yaxis()
      plt.show()

    return zip(frequency_idx, time_idx)

# Hash list structure: sha1_hash[0:20] time_offset
# example: [(e05b341a9b77a51fd26, 32), ... ]
def generate_hashes(peaks, fan_value=DEFAULT_FAN_VALUE):
    if PEAK_SORT:
        peaks.sort(key=itemgetter(1))

    print("after hasing",len(peaks))
    # bruteforce all peaks
    for i in range(len(peaks)):
        #print("hi")

        for j in range(1, fan_value):
            #print("hi")

            if (i + j) < len(peaks):


                # take current & next peak frequency value
                freq1 = peaks[i][IDX_FREQ_I]
                freq2 = peaks[i + j][IDX_FREQ_I]

                # take current & next -peak time offset
                t1 = peaks[i][IDX_TIME_J]
                t2 = peaks[i + j][IDX_TIME_J]

                # get diff of time offsets
                t_delta = t2 - t1
                #print(t_delta)

                # check if delta is between min & max
                if t_delta >= MIN_HASH_TIME_DELTA and t_delta <= MAX_HASH_TIME_DELTA:
                    x=4
                    #print("in if")
                    h = hashlib.sha1(("%s|%s|%s" % (str(freq1), str(freq2), str(t_delta))).encode())
                    print(h.hexdigest())
                    #yield (h.hexdigest()[0:FINGERPRINT_REDUCTION], t1)

    return 1

#fingerprint(data,plots=True)