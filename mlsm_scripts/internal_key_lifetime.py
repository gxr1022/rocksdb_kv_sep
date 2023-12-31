import bisect
op_trace_file="/mnt/nvme0n1/mlsm/test_blob/with_gc/trace-human_readable_trace.txt"
compaction_trace_file="/mnt/nvme0n1/mlsm/test_blob/with_gc/compaction_human_readable_trace.txt"




op_keys_access_info = {}
op_keys_with_sequence_info = {}
compaction_keys_access_info = {}
with open(op_trace_file, 'r') as f, open(compaction_trace_file, 'r') as f_compaction:
    lines = f.readlines()
    compaction_lines = f_compaction.readlines()
    for line in compaction_lines:
        compaction_trace_infos = line.split()
        key = compaction_trace_infos[0]
        sequence_number = compaction_trace_infos[1]
        compaction_time = compaction_trace_infos[2]
        internal_key = key + "_" + sequence_number
        compaction_keys_access_info[internal_key] = {'compaction_time': int(compaction_time), 'insert_time': None, 'invalid_time': None, 'valid_duration': None, 'actual_lifetime': None }


    print("The number of keys in compaction trace: ", len(compaction_keys_access_info))


    for line in lines:
        trace_infos = line.split()
        type_id = trace_infos[1]
        if type_id == '1' or type_id == '2':
            key = trace_infos[0]
            access_time = trace_infos[4]
            sequence_number = trace_infos[5]
            key_with_seq = key + "_" + sequence_number
            if key_with_seq in compaction_keys_access_info:
                compaction_keys_access_info[key_with_seq]['insert_time'] = int(access_time)

            if key not in op_keys_access_info:
                op_keys_access_info[key] = []
            op_keys_access_info[key].append([int(sequence_number), int(access_time)])
            # if key_with_seq not in op_keys_with_sequence_info:
            #     op_keys_with_sequence_info[key_with_seq] = {'insert_time': int(access_time), 'compaction_time': None, }
            #     keys_access_info[key_with_seq] = {'insert_time': int(access_time), 'compaction_time': None, }

    print("The number of keys in op trace: ", len(op_keys_access_info))
    for key, access_infos in op_keys_access_info.items():
        # print('key: {}, access_infos: {}'.format(key, access_infos))
        # if len(access_infos) >= 3:
        #     print('key: {}, access_infos: {}'.format(key, access_infos))
        sorted(access_infos, key=lambda x: x[0])
        # if len(access_infos) >= 3:
        #     print('key: {}, access_infos: {}'.format(key, access_infos))
        #     exit()
        for i in range(len(access_infos) - 1):
            internal_key = key + "_" + str(access_infos[i][0])
            valid_duration = access_infos[i + 1][1] - access_infos[i][1]
            invalid_time = access_infos[i + 1][1]
            if internal_key in compaction_keys_access_info:
                assert(compaction_keys_access_info[internal_key]['insert_time'] == access_infos[i][1])
                assert(compaction_keys_access_info[internal_key]['invalid_time'] == None)
                compaction_keys_access_info[internal_key]['invalid_time'] = invalid_time
                compaction_keys_access_info[internal_key]['valid_duration'] = valid_duration
                actual_lifetime = compaction_keys_access_info[internal_key]['compaction_time'] - compaction_keys_access_info[internal_key]['insert_time']
                compaction_keys_access_info[internal_key]['actual_lifetime'] = actual_lifetime
            

valid_durations = []
actual_lifetimes = []
lifetime_gap = []
lifetime_ratios = []

for key, infos in compaction_keys_access_info.items():


    # assert(infos['valid_duration'] != None)
    if infos['valid_duration'] != None and infos['actual_lifetime'] != None:
        lifetime_gap.append(infos['actual_lifetime'] - infos['valid_duration'])
        # ratio = (infos['actual_lifetime']) / (infos['valid_duration'])
        ratio = (infos['valid_duration']) / (infos['actual_lifetime'])
        lifetime_ratios.append(ratio )

    if infos['valid_duration'] != None:
        valid_durations.append(infos['valid_duration'])

    if infos['actual_lifetime'] != None:
        actual_lifetimes.append(infos['actual_lifetime'])

# print('lifetime ratio: ', lifetime_ratios)
print('len of lifetime ratio: ', len(lifetime_ratios))
sort_lifetime_ratio = sorted(lifetime_ratios)
print('last 10 of sort lifetime ratio: ', sort_lifetime_ratio[-200:-100])
index= bisect.bisect_left(sort_lifetime_ratio, 100)
print(' number of lifetime ratio > 100:{} , ratio is {} '.format(len(sort_lifetime_ratio) - index, index/len(sort_lifetime_ratio) )) 
print(' number of lifetime ratio > 10:{} , ratio is {} '.format(len(sort_lifetime_ratio) - bisect.bisect_left(sort_lifetime_ratio, 10), bisect.bisect_left(sort_lifetime_ratio, 10)/len(sort_lifetime_ratio) ))
valid_duration_file = "/mnt/nvme0n1/mlsm/test_blob/with_gc/valid_duration.txt"
actual_lifetime_file = "/mnt/nvme0n1/mlsm/test_blob/with_gc/actual_lifetime.txt"
lifetime_gap_file = "/mnt/nvme0n1/mlsm/test_blob/with_gc/lifetime_gap.txt"

with open(valid_duration_file, 'w') as f:
    for valid_duration in valid_durations:
        f.write(str(valid_duration) + "\n")

with open(actual_lifetime_file, 'w') as f:
    for actual_lifetime in actual_lifetimes:
        f.write(str(actual_lifetime) + "\n")

with open(lifetime_gap_file, 'w') as f:
    for gap in lifetime_gap:
        f.write(str(gap) + "\n")

print("len of valid_duration: {}, len of actual_lifetime: {}, len of lifetime_gap: {}".format(len(valid_durations), len(actual_lifetimes), len(lifetime_gap)))
import matplotlib.pyplot as plt
import numpy as np



valid_durations_x = np.sort(valid_durations)
valid_durations_y = 1. * np.arange(len(valid_durations)) / (len(valid_durations) - 1)

actual_lifetimes_x = np.sort(actual_lifetimes)
actual_lifetimes_y = 1. * np.arange(len(actual_lifetimes)) / (len(actual_lifetimes) - 1)

lifetime_gap_x = np.sort(lifetime_gap)
lifetime_gap_y = 1. * np.arange(len(lifetime_gap)) / (len(lifetime_gap) - 1)

plt.plot(valid_durations_x, valid_durations_y, label='valid_durations')
plt.plot(actual_lifetimes_x, actual_lifetimes_y, label='actual_lifetimes')
plt.plot(lifetime_gap_x, lifetime_gap_y, label='lifetime_gap')
plt.legend()
plt.savefig('compaction_lifetime.png')

plt.figure()
plt.hist([valid_durations, actual_lifetimes, lifetime_gap], bins=20, label=['valid_durations', 'actual_lifetimes', 'lifetime_gap'], histtype='bar')
# plt.hist(valid_durations, bins=100, label='valid_durations')
# plt.hist(actual_lifetimes, bins=100, label='actual_lifetimes')
# plt.hist(lifetime_gap, bins=100, label='lifetime_gap')
plt.legend()
plt.savefig('compaction_lifetime_hist.png')

plt.figure()
lifetime_ratios_x = np.sort(lifetime_ratios)
lifetime_ratios_y = 1. * np.arange(len(lifetime_ratios)) / (len(lifetime_ratios) - 1)
plt.hist(lifetime_ratios, bins=20,  label='lifetime_ratios' , density=True) 
# plt.plot(lifetime_ratios_x, lifetime_ratios_y, label='lifetime_ratios')
plt.legend()
plt.savefig('compaction_lifetime_ratios_valid_to_actual.png')



# output_file = "/mnt/nvme0n1/mlsm/test_blob/with_gc/internal_key_lifetime.txt"
# with open(output_file, 'w') as f:

























