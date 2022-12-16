import streamlit as st
import os
import pandas as pd
from datetime import datetime

from tut07 import octant_analysis_single

# header section
st.set_page_config(page_icon="🐰", page_title="Octant Analysis", layout="wide")

st.caption("<span style='float: right'>Pratyush Kumar (2001ME51) / Shivam Yadav (2001ME70)</span>", unsafe_allow_html=True)
st.title("Octant Analysis 🐰")

# --- SETUP ---------------------------------------------

screens = ['Upload files/folder', 'Enter mod value', 'Output']
temp_folder = "./__temp__"
output_folder = "./output"

def init_session_variable(name, val):
    if name not in st.session_state:
        st.session_state[name] = val

def empty_folder(filepath):
    if os.path.exists(filepath):
        for file in os.listdir(filepath):
            os.remove(os.path.join(filepath, file))

init_session_variable("selected_screen", 0)
init_session_variable("files", None)
init_session_variable("mod", None)
init_session_variable("processing", False)
init_session_variable("output", None)

# -------------------------------------------------------

def on_file_option_change():
    st.session_state.files = None

def on_files_next(files, folder, from_to):
    st.session_state.files = None

    if files is None and folder is None:
        # nothing uploaded
        return

    if files is not None:
        if len(files) == 0:
            return

        st.session_state.files = files
        st.session_state.selected_screen = from_to[1]

    if folder is not None:
        folder = folder.strip()

        if len(folder) > 0 and os.path.exists(folder) and os.path.isdir(folder):
            _files = []

            for file in sorted(os.listdir(folder)):
                if os.path.isfile(os.path.join(folder, file)) and '.xlsx' in file:
                    _files.append({
                        "data": pd.read_excel(os.path.join(folder, file), header=None, na_filter=None),
                        "name": file
                    })
            
            st.session_state.files = _files
            st.session_state.selected_screen = from_to[1]

def on_mod_next(mod, from_to):
    st.session_state.mod = mod
    st.session_state.processing = (st.session_state.files is not None and st.session_state.mod is not None)
    st.session_state.selected_screen = from_to[1]

def process_input_file(file, mod):
    f, filename = None, None

    if isinstance(file, dict):
        f = file["data"]
        filename = file["name"]
    else:
        f = pd.read_excel(file, header=None, na_filter=None)
        filename = file.name
    
    f.to_excel(os.path.join(temp_folder, filename), header=False, index=False)

    output_filename = octant_analysis_single(mod, filename, temp_folder, output_folder, 1)

    return output_filename

def reset_app():
    st.session_state.selected_screen = 0
    st.session_state.files = None
    st.session_state.mod = None
    st.session_state.processing = False
    st.session_state.output = None

# -------------------------------------------------------

cols = st.columns([1, 3])
# cols = st.columns([1, 3, 1])
# with cols[2]:
#     st.write(st.session_state.files)
#     st.write(st.session_state.mod)
#     st.write(st.session_state.output)

with cols[0]:
    for i, screen in enumerate(screens):
        if i < st.session_state.selected_screen or st.session_state.selected_screen == len(screens) - 1:
            bg_color = "#2bc48a"
            color = "white"
        elif i == st.session_state.selected_screen:
            bg_color = "#f0f2f6"
            color = "inherit"
        else:
            bg_color = "transparent"
            color = "inherit"

        st.write(f"<div style='padding: 1rem; margin-bottom: 0.5rem; color: {color}; background-color: {bg_color}; border-radius: 0.25rem;'>{screen}</div>", unsafe_allow_html=True)

# file upload screen
with cols[1]:
    if st.session_state.selected_screen == 0:
        option = st.selectbox(
            label="Select files/folder for processing",
            options=('Select files', 'Select folder'),
            index=0,
            label_visibility="collapsed",
            on_change=on_file_option_change
        )
        # st.write("Select files or folder to process")
        # tab_file, tab_folder = st.tabs(('Select files', 'Select folder'))
        
        # with tab_file:
        #     files = st.file_uploader("", type=["xlsx"], accept_multiple_files=True, label_visibility="collapsed")
        #     next_btn = st.button(label="Next", key=0, type="primary", on_click=on_files_next, args=(files, None, (0, 1)))
        
        # with tab_folder:
        #     folder = st.text_input("", placeholder="Enter path to input folder", label_visibility="collapsed")
        #     next_btn = st.button(label="Next", key=1, type="primary", on_click=on_files_next, args=(None, folder, (0, 1)))

        files, folder = None, None
        if option == 'Select files':
            files = st.file_uploader("Select files", type=["xlsx"], accept_multiple_files=True, label_visibility="collapsed")
        elif option == 'Select folder':
            folder = st.text_input("Enter path to input folder", placeholder="Enter path to input folder", label_visibility="collapsed")

        next_btn = st.button(label="Next", type="primary", on_click=on_files_next, args=(files, folder, (0, 1)))
        if next_btn and st.session_state.files is None:
            st.info("Select valid files/folder for processing")

# mod value screen
with cols[1]:
    if st.session_state.selected_screen == 1:
        mod = st.number_input(
            label="Enter mod value",
            min_value=1,
            value=5000
        )
        
        st.button("Start processing", type="primary", on_click=on_mod_next, args=(mod, (1, 2),))

with cols[1]:
    if st.session_state.selected_screen == 2:
        placeholder = st.empty()

        if st.session_state.processing:
            with st.spinner("Processing..."):
                curr_file = st.empty()
                
                if os.path.exists(temp_folder):
                    empty_folder(temp_folder)
                else:
                    os.mkdir(temp_folder)

                dt = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
                for file in st.session_state.files:
                    filename = file["name"] if isinstance(file, dict) else file.name

                    curr_file.caption(f"(Processing {filename})")

                    try:
                        output_filename = process_input_file(file, st.session_state.mod)
                        output = pd.read_excel(os.path.join(output_folder, output_filename), dtype='string', na_filter=False)

                    except Exception as e:
                        output_filename = filename
                        output = e

                    if st.session_state.output is None:
                        st.session_state.output = []
                        
                    st.session_state.output.append((filename, output_filename, output))

                    curr_file.empty()
            
            empty_folder(temp_folder)
            os.rmdir(temp_folder)

            st.session_state.processing = False
            st.session_state.files = None
            st.session_state.mod = None

        with placeholder.container():
            tabs = st.tabs([x[1] for x in st.session_state.output])

            for i in range(len(st.session_state.output)):
                with tabs[i]:
                    input_filename = st.session_state.output[i][0]
                    output_filename = st.session_state.output[i][1]
                    data = st.session_state.output[i][2]
                    
                    if type(data) == pd.DataFrame:
                        st.dataframe(data)

                        with open(os.path.join(output_folder, output_filename), 'rb') as f:
                            st.download_button("Save file as...", f, output_filename, mime="application/octet-stream")
                    else:
                        st.error(f"There was en error while processing \"{input_filename}\"", icon="⚠️")
                        st.write(data)
            
            st.button("Process more files...", type="primary", on_click=reset_app)