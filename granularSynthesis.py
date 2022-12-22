"""
MADELINE JANECEK, BRENDAN PARK
DECEMEBER 2022
COSC 4P98 PROJECT
Implementation of granular synthesis w/ GUI

"""

import math                         # for things like sine and PI
from enum import Enum               # to help organize parameters (envelope types, random distributions)
import random                       # for random grain selection and parameter variations
from scipy.stats import truncnorm   # for random grain selection with normal distribution
from tqdm import tqdm               # for loading bar

class Envelope(Enum):
    TRAPEZIUM = 1
    TRIANGLE = 2
    BELL = 3
    UNTOUCHED = 4
    COMPLEX = 5

class Selection(Enum):
    RANDOM = 1
    NORMAL = 2

"""
    Extracts a sample table from a given .txt file
"""
def read_sample_table(filename):
    result = []
    data = open(filename, 'r')
    d = data.readline()
    while d:
        if not d.strip() == '':
            result.append(float(d.strip()))
        d = data.readline()
    data.close()
    return result

"""
    Writes a sample into a new .txt file
"""
def write_sample(sample, filename):
    with open(filename, 'w') as f:
        for s in sample:
            f.write(str(s))
            f.write('\n')
    f.close()
    print(filename, "generated and saved")

"""
    Takes a grain and envelopes it using a simple linear cutoff
        in_grain: array of samples that make up the grain
        sustain: what percentage of the grain should be at its original amplitude
                 default 50% means that the first 50/2=25% of the grain is modified 
                 to 'grow' into the full amplitude, and the last 50/2=25% of the 
                 grain is modified to 'shrink' back to 0
                 note: unless type is TRAPEZUIM, this is ignored
"""
def envelope(in_grain, type=Envelope.TRAPEZIUM):
    grain = in_grain.copy()
    size = len(grain)
    if type == Envelope.UNTOUCHED:
        return grain
    elif type == Envelope.TRAPEZIUM:
        sustain=0.75
        samps = math.floor(size*(1-sustain)/2)
        for x in range(samps):
            grain[x] = grain[x]*(x/samps)
            grain[size-x-1] = grain[size-x-1]*(x/samps)
    elif type == Envelope.TRIANGLE:
        for x in range(int(size/2)):
            grain[x] = grain[x]*(2*x/size)
            grain[size-x-1] = grain[size-x-1]*(2*x/size)
    elif type == Envelope.BELL:
        for x in range(size):
            cutoff = math.sin(math.pi*x/size)
            grain[x] = grain[x]*cutoff
    elif type == Envelope.COMPLEX:
        for x in range(size):
            bell_cutoff = math.sin(math.pi*x/size)
            sine_cutoff = math.sin(3*math.pi*x/size)
            grain[x] = grain[x]*min(bell_cutoff, abs(sine_cutoff))
    return grain

"""
    Gets the given index from a sample table using linear interpolation
        sample: the sample table
        index: the index from which you want your sample (can be a non-integer value)
"""
def get_index(sample, index):
    if int(index) == index:
        return sample[int(index)]
    else:
        lower = int(index)
        higher = (lower+1)%len(sample)
        diff = index - lower
        value = sample[lower] + diff*(sample[higher]-sample[lower])
        return value

"""
    Takes a grain and changes its pitch by a given factor
        in_grain: array of samples that make up the grain
        pitch_change: the change in pitch. 
                    If = 1, no change
                    If < 1, fewer samples resulting in higher pitch
                    If > 1, more samples resulting in lower pitch
        pitch_var: small variations in the pitch change (percentage)
                    must be >= 0 and < 1
                    if pitch_change = 1, and pitch_var = 0.1, then
                    the pitch change c may be:
                            1-(1*0.1) <= c <= 1+(1*0.1)
                            0.9 <= c <= 1.1
"""
def change_pitch(in_grain, pitch_change, pitch_var = 0):
    if pitch_var < 0:
        raise ValueError("Variation must be >= 0")
    var_min = pitch_change-pitch_var
    if var_min <= 0:
        var_min = 0.01

    new_num = int(len(in_grain)*random.uniform(var_min, pitch_change+pitch_var))
    step_size = len(in_grain)/new_num
    step = 0
    grain = []
    for x in range(new_num):
        grain.append(get_index(in_grain, step))
        step += step_size
    return grain

"""
Returns a grain selected from the sample - NOT ENVELOPED
    sample: the sample table from which the grain is to be selected
    sample_dur: the number of samples in the grain
    middle: the middle of the cloud (only really matters if the selection type is NORMAL)
    min: the minimum sample in the cloud
    max: the maximum sample in the cloud (inclusive)
    dur_variation: how much the duration can vary (in percentage, default zero, 0 <= dur_variation < 1)
    type: the type of distribution used to selected the grain
"""
def get_grain(sample, middle, min, max, grain_dur, dur_variation=0, type=Selection.RANDOM):
    if dur_variation < 0:
        raise ValueError("Variation must be >= 0")
    start_point = -1
    var_min = grain_dur-(dur_variation*grain_dur)

    if var_min < 1:
        var_min = 1
    dur = int(random.uniform(var_min, grain_dur+(grain_dur*dur_variation)))

    if max >= len(sample):
        max = len(sample) -1

    if type == Selection.RANDOM:
        start_point = random.randint(min, max)
    elif type == Selection.NORMAL:
        sd = 1.5*dur
        start_point = int(truncnorm((min - middle) / sd, (max - min) / sd, loc=middle, scale=sd).rvs())

    grain = []
    for x in range(dur):
        while start_point >= len(sample):
            start_point = start_point-len(sample)
        grain.append(sample[start_point])
        start_point += 1
        
    return grain

"""
Function that actually performs the granular synthesis
    sample_table: the original sample from which the output is generated
    output_dur: duration of generated sound (in seconds)
    envelope_type: the type of envelope to apply to the grains (see Envelope for the different types)
    distribution_type: the type of distribution used to randomly select grains (see Selection for the different types)
    grain_dur: duration of grains (in milliseconds)
    grain_dur_var: by how much the grains' duration can vary (percentage, must be nonnegative)
    grain_rate: cloud density (grains/sec)
    grain_rate_var: by how much the cloud density may vary (percentage)
    grain_pitch: by how much the pitch of a grain changes (1 is no change, <1 is higher pitch, >1 is lower pitch)
    grain_pitch_var: by how much the grains' duration can vary (percentage, must be nonnegative)
    cloud_center, cloud_min, cloud_max: specify where the grains are selected from
    sample_rate: sample rate of the sample/output
"""
def synthesizeGranularly(sample_table, output_dur,
                        envelope_type, distribution_type,
                        grain_dur, grain_dur_var, 
                        grain_rate, grain_rate_var, 
                        grain_pitch, grain_pitch_var, 
                        cloud_center, cloud_min, cloud_max, 
                        sample_rate = 44100):
    output_size = int(sample_rate*output_dur)
    output = [0]*output_size
    grain_size = int(sample_rate*(grain_dur/1000))

    for x in tqdm(range(output_size)):
        density = grain_rate*random.uniform(grain_rate-(grain_rate*grain_rate_var), grain_rate+(grain_rate*grain_rate_var))
        prob = density/sample_rate
        chance = random.random()
        if chance < prob:
            grain = get_grain(sample_table, cloud_center, cloud_min, cloud_max, grain_size, grain_dur_var, distribution_type)
            grain = change_pitch(grain, grain_pitch, grain_pitch_var)
            grain = envelope(grain, envelope_type)
            if x+len(grain) < output_size:
                for y in range(len(grain)):
                    if abs(output[x+y] + grain[y]) > 1:
                        output[x+y] = 0.5*output[x+y] + 0.5*grain[y]
                    else:
                        output[x+y] += grain[y]
    return output

print("Reading Sample")
filename = "data\sine440.txt"    # CHANGE FOR DIFFERENT INPUT FILE
sample = read_sample_table(filename)
outputname = "data\example_output.txt"    # CHANGE FOR DIFFERENT OUTPUT FILE NAMES
duration = 1            # CHANGE FOR DIFFERENT OUTPUT DURATION
e = Envelope.COMPLEX  # CHANGE FOR DIFFERENT ENVELOPE TYPE (SEE ENVELOPE CLASS FOR OPTIONS)
s = Selection.NORMAL    # CHANGE RANDOM DISTRIBUTIONS (SEE SELECTION CLASS FOR OPTIONS)
g_duration = 50        # CHANGE BASE GRAIN DURATION
g_var = 0.5                 # CHANGE HOW MUCH GRAIN DURATION CAN VARY (PERCENTAGE, 0.5 = 50%)
g_rate = 5                  # CHANGE THE GRAIN GENERATION RATE
g_rvar = 0                  # CHANGE THE VARIATION IN GRAIN GENERATION (PERCENTAGE)
g_pitch = 0.5               # CHANGE HOW MUCH GRAIN PITCH CHANGES (PERCENTAGE 1 is same pitch, <1 higher pitch, >1 lower pitch)
g_pvar = 0.5                # CHANGE THE PITCH VARIATION (PERCENTAGE)
cloud_c = len(sample)/2     # CHANGE THE CLOUD CENTER
cloud_min = 0               # CHANGE THE CLOUD MIN
cloud_max = len(sample)     # CHANGE THE CLOUD MAX
sample_rate = 44100         # CHAnGE the SAMPLE RATE
print("Number of samples in wave table:", len(sample))
print("Starting granular synthesis")
result = synthesizeGranularly(sample, duration, e, s, g_duration, g_var, g_rate, g_rvar, g_pitch, g_pvar, cloud_c, cloud_min, cloud_max, sample_rate)
print("Saving sample")
write_sample(result, outputname)