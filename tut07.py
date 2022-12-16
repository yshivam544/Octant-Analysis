from openpyxl import load_workbook
import os
from datetime import datetime
from platform import python_version

from _tut07.formatting import format_output_file
from _tut07.utils import importFile
from _tut07.data_processing import generate_output

def save_to_file(output, filename):
	data = output["data"].copy()

	# replaces column headings with 'blank_' in them to empty strings
	new_column_headings = [(col if 'blank_' not in str(col) else '') for col in data.columns]
	
	# inserts the column headings as a row at top
	data.loc[-1] = new_column_headings
	data.index += 1
	data = data.sort_index()

	# writes dataframe to output file
	try:
		data.to_excel(filename, index=False, header=False)

		wb = load_workbook(filename)
		ws = wb.active

		format_output_file(ws, shapes=output["shapes"], nOctants=output["octants"])

		wb.save(filename)

	except Exception as e:
		print(e)
		print(f"There was a problem while writing the output file \"{filename}\".\nExiting...")
		return

	print(f"Generated \"{filename}\".")

def octant_analysis_single(mod, filename, inputFolder, outputFolder, append_mode=0):
	octant_name_id_mapping = {
		"1": "Internal outward interaction",
		"-1":"External outward interaction",
		"2":"External Ejection",
		"-2":"Internal Ejection",
		"3":"External inward interaction",
		"-3":"Internal inward interaction",
		"4":"Internal sweep",
		"-4":"External sweep"
	}

	# create the output folder if it doesn't already exist
	if outputFolder.lstrip("./") not in os.listdir("."):
		os.mkdir("./output")

	print(f"Processing \"{filename}\"...")

	file = importFile(os.path.join(inputFolder, filename))
	output = generate_output(file, mod, octant_name_id_mapping)

	outputFilename = filename.rstrip(".xlsx")
	
	if append_mode == 0:
		outputFilename += f"_octant_analysis_mod_{mod}"
	elif append_mode == 1:
		dt = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
		outputFilename += f"_{mod}_{dt}"

	outputFilename += ".xlsx"

	save_to_file(output, os.path.join(outputFolder, outputFilename))

	return outputFilename

def octant_analysis(mod=5000, append_mode=0, inputFolder="./input", outputFolder="./output"):
	# check if input folder exists
	if inputFolder.lstrip("./") not in os.listdir("./"):
		print(f"\"{inputFolder.lstrip('./')}\" folder not found.\nExiting...")
		return

	# get all input filepaths
	inputFiles = [f for f in os.listdir(inputFolder) if ".xlsx" in f]
	inputFiles.sort()

	for filename in inputFiles:
		octant_analysis_single(mod, filename, inputFolder, outputFolder, append_mode)

##Read all the excel files in a batch format from the input/ folder. Only xlsx to be allowed
##Save all the excel files in a the output/ folder. Only xlsx to be allowed
## output filename = input_filename[_octant_analysis_mod_5000].xlsx , ie, append _octant_analysis_mod_5000 to the original filename. 

if __name__ == "__main__":
	start_time = datetime.now()

	ver = python_version()

	if ver == "3.8.10":
		print("Correct Version Installed")
	else:
		print("Please install 3.8.10. Instruction are present in the GitHub Repo/Webmail. Url: https://pastebin.com/nvibxmjw")

	mod=5000
	octant_analysis(mod)

	#This shall be the last lines of the code.
	end_time = datetime.now()
	print('Duration of Program Execution: {}'.format(end_time - start_time))
