import pandas as pd
from _tut07.utils import get_octant_order, df_concat_horizontally, df_concat_vertically

def find_octant(u, v, w):
	# finds octant by comparing u,v,w values
	# assuming a value of 0 as +ve
	octant = None

	if(u >= 0 and v >= 0):
		octant = 1
	elif(u < 0 and v >= 0):
		octant = 2
	elif(u < 0 and v < 0):
		octant = 3
	elif(u >= 0 and v < 0):
		octant = 4

	if(w >= 0):
		return octant
	else:
		return -octant

def preprocess(df):
	# drop rows containing any empty cells
	df.dropna(axis='index', inplace=True)
	# reset the indexing as dropping rows does not update the indices
	df.reset_index(drop=True, inplace=True)

	# finding mean of U, V and W columns
	u_avg = round(df['U'].mean(), 3) # --> float value rounded to 3 decimals
	v_avg = round(df['V'].mean(), 3) # --> float value rounded to 3 decimals
	w_avg = round(df['W'].mean(), 3) # --> float value rounded to 3 decimals

	# adding avg values to the dataframe in seperate columns
	df['U Avg'] = pd.Series([u_avg], dtype="float64")
	df['V Avg'] = pd.Series([v_avg], dtype="float64")
	df['W Avg'] = pd.Series([w_avg], dtype="float64")

	# subtracting means from U, V and W values to get the working set values
	u_dash = round(df['U'] - u_avg, 3) # --> pd.Series object
	v_dash = round(df['V'] - v_avg, 3) # --> pd.Series object
	w_dash = round(df['W'] - w_avg, 3) # --> pd.Series object

	# putting the obtained values into the dataframe in seperate columns
	df['U\'=U - U avg'] = u_dash
	df['V\'=V - V avg'] = v_dash
	df['W\'=W - W avg'] = w_dash

	# adds a new column 'Octant' with octant assigned to each data row
	df['Octant'] = df.apply(
		lambda row: find_octant(
			row['U\'=U - U avg'],
			row['V\'=V - V avg'],
			row['W\'=W - W avg']
		),
		axis='columns'
	)

	return df.reset_index(drop=True)

def get_octant_counts(df, octant_order):
	octants = df['Octant']

	counts = pd.Series([0 for x in octant_order], index = octant_order, dtype="int64")
	value_counts = octants.value_counts()
	for index in value_counts.index:
		counts[index] = value_counts[index]

	return counts

def generate_data_oc(data, mod):
	octant_order = get_octant_order(data['Octant'])

	# creating octant count table structure
	df = pd.DataFrame()
	df["blank_oc1"] = pd.Series(["Mod " + str(mod)]) # --> column 0
	df["Octant ID"] = pd.Series(["Overall Count"]) # --> column 1
		
	# getting overall octant counts
	overall_counts = get_octant_counts(data, octant_order)
	for index in overall_counts.index:
		df.at[0, index] = overall_counts[index] # filling octant counts
		
	# octant counts in mod ranges
	range_start = 0
	range_end = -1
	row = len(df)
		
	while(range_end < len(data) - 1):
		range_start = range_end + 1
		range_end = min(range_start + mod - 1, len(data) - 1)

		df.at[row, "Octant ID"] = "{0:d}-{1:d}".format(range_start, range_end) # creating row for mod range
		df.iloc[row, 2:] = get_octant_counts(data.iloc[range_start:range_end + 1], octant_order) # filling octant counts for mod range

		row += 1

	return df

def generate_data_rank_a(data, mapping):
	df = pd.DataFrame()

	# creating structure for octant count rank table
	octant_order = pd.Index(data.columns[2:], dtype="int64")
	for octant in octant_order:
		df["Rank Octant " + str(octant)] = pd.Series([], dtype="int64")
	df["Rank 1 Octant ID"] = pd.Series([], dtype="int64")
	df["Rank 1 Octant Name"] = pd.Series([None] * len(data.index), dtype="string")

	n = len(octant_order)

	for i in range(len(data)):		
		count_order = [x for x in range(n)]
		# sorts the column numbers according to the value of count at that column (descending order)
		count_order.sort(reverse=True, key=lambda a: data.iloc[i, 2 + a])

		# loops through count_order by index j
		# now j-th element in count_order is the octant number index having rank = j + 1
		for j in range(n):
			df.at[i, "Rank Octant " + str(octant_order[count_order[j]])] = j + 1
		
		rank1_id = octant_order[count_order[0]]
		df.at[i, "Rank 1 Octant ID"] = rank1_id
		df.at[i, "Rank 1 Octant Name"] = mapping[str(rank1_id)]

	return df

def generate_data_rank_b(data, octants, mapping):
	df = pd.DataFrame()
	octant_order = get_octant_order(octants)
		
	df["Octant ID"] = pd.Series(octant_order, dtype="int64")
	df["Octant Name"] = pd.Series(map(lambda x: mapping[str(x)], octant_order), dtype="string")
	df["Count of Rank 1 Mod Values"] = 0
		
	rank1_mod_value_counts = data.loc[1:, "Rank 1 Octant ID"].value_counts()

	df = df.T
	for i in range(len(octant_order)):
		if(octant_order[i] in rank1_mod_value_counts.index):
			df.at["Count of Rank 1 Mod Values", i] = rank1_mod_value_counts.get(octant_order[i])

	return df.T

def get_mod_ranges(size, mod):
	# getting list of ranges based on mod value
	mod_ranges = []
	i = 0
	while i < size:
		range_start = i
		range_end = min(i + mod - 1, size - 1)

		mod_ranges.append((range_start, range_end))

		# new range_start for next range = range_end + 1
		i = range_end + 1

	return tuple(mod_ranges)

def get_transition_counts(df, octants, mod_range):
	# storing transition counts in the range as a nested dictionary
	transition_counts = {col:{row:0 for row in octants} for col in octants}

	for row in range(mod_range[0], mod_range[1] + 1):
		# if we reached the last row of entire dataset, then break the loop
		# because the last row cannot transition to anything else
		if row == len(df) - 1:
			break

		octant_from = df.at[row, 'Octant']
		octant_to = df.at[row + 1, 'Octant']

		transition_counts[octant_to][octant_from] += 1
		
	return pd.DataFrame(transition_counts)

def generate_transition_count_table(table_name, data, available_octants, mod_range=None):
	df = pd.DataFrame()
	
	df["blank_tc_0"] = pd.Series([pd.NA, pd.NA] + ["From"] + [pd.NA] * (len(available_octants) - 1), dtype="string")

	transition_counts = get_transition_counts(
		df=data,
		octants=available_octants,
		mod_range=mod_range if mod_range else (0, len(data) - 1)
	)

	df[table_name] = pd.Series(["{0}-{1}".format(*mod_range) if mod_range else "", "Octant ID", *transition_counts.index])
	for col in transition_counts.columns:
		df["blank_" + str(col)] = pd.Series([pd.NA, col, *transition_counts.loc[:, col]])
	
	df.iloc[0, 2] = "To"

	return df

def get_longest_subsequence_details_of(query, octants, time = pd.Series(dtype='int64')):
    longest_subsequence_length = 0
    longest_count = 0

    # time ranges where the longest subsequence occurs
    time_ranges = []
    
    # running length of a subsequence being iterated over
    start = 0
    length = 0
    for i in range(len(octants)):
        # if the subsequence gets broken
        if i > 0 and octants[i] != octants[i - 1]:
            # if the subsequence was the longest
            if length > longest_subsequence_length:
                # store its length in the variable
                longest_subsequence_length = length
                # and since its the first subsequence to be found that is the longest,
                # the count of the longest subsequence becomes 1
                longest_count = 1
                # and this will become the first time range in which this subsequence occurs
                if(not time.empty):
                    time_ranges = [(time[start], time[i - 1])]
            # if the subsequence length is same as the longest subsequence,
            # just increase the count
            # and add the time range to the list
            elif length == longest_subsequence_length:
                longest_count += 1
                if(not time.empty):
                    time_ranges.append((time[start], time[i - 1]))
            start = i

        # if we find the query item, length += 1
        # otherwise if we get a different item,
        # the subsequence is broken so set the running length to 0
        if octants[i] == query:
            length += 1
        else:
            length = 0
    
    return {'length': longest_subsequence_length, 'count': longest_count, 'time_ranges': time_ranges}

def generate_data_ls(octants):
    # data_ls -> [ count and length data of longest octant subsequence ]

    unique_octants = get_octant_order(octants)

    # create new dataframe
    data_ls = pd.DataFrame()
    # adds a column 'Octant ID' containing list of unique octants present in the dataset
    data_ls['Octant ID'] = unique_octants

    # adds empty columns named 'Longest Subsquence Length' and 'Count'
    data_ls['Longest Subsquence Length'] = pd.Series([], dtype='int64')
    data_ls['Count'] = pd.Series([], dtype='int64')

    # find the lengths and counts of longest subsequences of each unique octant
    # and add in data_ls
    for i in range(len(unique_octants)):
        longest_subsequence = get_longest_subsequence_details_of(query=unique_octants[i], octants=octants)

        data_ls.at[i, 'Longest Subsquence Length'] = longest_subsequence['length']
        data_ls.at[i, 'Count'] = longest_subsequence['count']
    
    return data_ls

def generate_data_lst_for(query, octants, time):
    # data_lst -> [ count, length and time range data of longest octant subsequence ]

    # create new dataframe
    data_lst = pd.DataFrame()

    # get longest subsequence length, count and time ranges
    longest_subsequence = get_longest_subsequence_details_of(query, octants, time)

    # add new column 'Octant ID' with an addition header 'Time' at the end
    data_lst['Octant ID'] = pd.Series([query])
    data_lst['Longest Subsequence Length'] = pd.Series([longest_subsequence['length']])
    data_lst['Count'] = pd.Series([longest_subsequence['count']])

    data_lst.loc[len(data_lst.index)] = ['Time', 'From', 'To']

    for _from, _to in longest_subsequence['time_ranges']:
        data_lst.loc[len(data_lst.index)] = [None, _from, _to]

    return data_lst

def generate_output(df, mod, octant_name_id_mapping):
	data = preprocess(df) # data -> [ returns preprocessed data with average values and octant numbers ]
	data_oc = generate_data_oc(data, mod) # data_oc -> [ returns dataframe containing octant counts for mod ranges and overall data ]

	data_rank_a = generate_data_rank_a(data_oc, octant_name_id_mapping) # -> [ returns dataframe containing octant count rank details for mod ranges and overall ]
	data_rank_b = generate_data_rank_b(data_rank_a, data['Octant'], octant_name_id_mapping) # -> [ returns a dataframe contianing count of octants in "Rank 1 Octant ID" column of data_rank_a ]

	data_rank = df_concat_vertically(data_rank_a, data_rank_b, offsetX=(len(data_rank_a.columns) - len(data_rank_b.columns) - 1), offsetY=1)

	data_oc_rank = pd.concat([data_oc, data_rank], axis="columns")

	available_octants = get_octant_order(data['Octant'])

	data_tc = generate_transition_count_table(
		table_name="Overall Transition Count",
		data=data,
		available_octants=available_octants
	)
	
	for range_start, range_end in get_mod_ranges(len(data), mod):
		mod_transition_counts = generate_transition_count_table(
			table_name="Mod Transition Count",
			mod_range=(range_start, range_end),
			data=data,
			available_octants=available_octants
		)

		data_tc = df_concat_vertically(data_tc, mod_transition_counts, offsetX=0, offsetY=2)
	
	data_ls = generate_data_ls(data['Octant']) # data_ls -> [ count and length data of longest octant subsequence ]
	data_lst = pd.DataFrame() # data_lst -> [ count, length and time range data of longest octant subsequence ]

	for octant in available_octants:
		data_lst = pd.concat([data_lst, generate_data_lst_for(octant, data['Octant'], data['T'])], ignore_index=True, axis='index')

	output = df_concat_horizontally([data, data_oc_rank, data_tc, data_ls, data_lst], offsetX=1)

	return {
		"data": output,
		"octants": len(available_octants),
		"shapes": {
			"data": data.shape,
			"data_oc": data_oc.shape,
			"data_oc_rank": data_oc_rank.shape,
			"data_rank_b": data_rank_b.shape,
			"data_tc": data_tc.shape,
			"data_ls": data_ls.shape,
			"data_lst": data_lst.shape
		}
	}