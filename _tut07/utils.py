import pandas as pd

def importFile(filepath):
	try:
		file = pd.read_excel(filepath)
	except FileNotFoundError:
		print(f"Error: Input file \"{filepath.strip('.')}\" not found\nExiting...")
		return None
	except:
		print(f"There was an error while opening the file \"{filepath.lstrip('.')}\". Exiting...")
		return None
		
	return file

def df_concat_vertically(df_a, df_b, offsetX=0, offsetY=0):
	# concatenate df_a and df_b vertically using df_a column names
	# given: len(df_a.columns) >= len(df_b.columns)

	df_a = df_a.copy()
	df_b = df_b.copy()

	# add blank rows
	for i in range(1, offsetY + 1):
		df_b.loc[-(i + 1), :] = pd.Series([], dtype="int64")
	# add original column names as first row after gaps
	df_b.loc[-1, :] = [col if "blank_" not in col else pd.NA for col in df_b.columns]

	df_b.index += 1
	df_b.sort_index(inplace=True)

	# rename columns of df_b to those of df_a
	df_b.columns = df_a.columns[offsetX : offsetX + len(df_b.columns)]
		
	# join the two dataframes by columns
	df = pd.concat([df_a, df_b], axis="index", ignore_index=True)

	return df

def df_concat_horizontally(arr, offsetX = 0):
	if len(arr) == 0:
		return pd.DataFrame()
	elif len(arr) == 1:
		return arr[0]
	
	emptyDf = pd.DataFrame({("blank_concatH_" + str(x)): {0: pd.NA} for x in range(offsetX)})

	output = arr[0]

	for df in arr[1:]:
		output = pd.concat([output, emptyDf, df], axis="columns")
	
	return output

def get_octant_order(octants):
	# gets the 'Octant' column
	available_octants = list(octants.value_counts().index)

	# sort the list in reverse lexicographical order, ie, 1, -1, 2, -2, 3, -3, 4, -4
	available_octants.sort(key=lambda x: str(x)[::-1])

	return pd.Index(available_octants, dtype="int64")