import requests
import os 
from datetime import datetime
import re
# import sys
# import getopt
import PySimpleGUI as sg

import PIL.Image
import io
import base64

import pyperclip

import time
############### Init variables ###############

FlickrFileNames = True 
  # False means file names of each photo will be with numbers, as in Flickr database states
  # True means title of the photo from main page, useful for further debugging or to find author of the photo
Debugging = 2 #0,1(default),2
  # 0 means that the output of below cell will output only final info
  # 1 means info of each downlaoded photo will be progressively displayed
  # 2 means all debbuging will also be saved in txt file called debugging.txt
DownloadFiles = True
  # Download photos yes or no
  # Helpful in case of Debugging 



exported_file = 'exported_urls.txt'
input_urls = 'input_urls.txt'
output_folder_name = 'gathered'


statisctics = [0,0] #[success, error]
nr_of_photo = 1


if FlickrFileNames:
    custom_file_names = set()


# SharingVariable = []
# SharingVariable =
# [
#     ["Namestringi", "Linkstringi", Checkedbool],
#     ["Namestringi", "Linkstringi", Checkedbool],
#     ["Namestringi", "Linkstringi", Checkedbool],
#     ["Namestringi", "Linkstringi", Checkedbool],
# ]
# SharingVariable = {} #dictionary

def ddownloader(direct_url, printt, titled_name = -1):
  global outputted_file,statisctics,nr_of_photo,SharingVariable
  r = requests.get(direct_url)
  if titled_name == -1:
    file_name = direct_url[direct_url.rfind('/')+1:]
  else:
    file_name = titled_name
  with open(file_name,'wb') as f:
    f.write(r.content)
  outputted_file.write(direct_url+'\n')
  statisctics[0] += 1
  nr_of_photo += 1
  printstring = f"\tFile {file_name} saved!\n"
  SharingVariable[file_name] = direct_url  #SharingVariable.append([file_name,direct_url, 0])

  if printt == 1:
    print(printstring)
    window['_LOGS_OUT_'].update(f"{window['_LOGS_OUT_'].get()}\n{printstring}\n")
    window['_LOGS_OUT_'].set_vscroll_position(1)
  elif printt == 2:
    print(printstring)
    window['_LOGS_OUT_'].update(f"{window['_LOGS_OUT_'].get()}\n{printstring}\n")
    window['_LOGS_OUT_'].set_vscroll_position(1)
    return printstring
  
def convert_to_bytes(file_or_bytes, resize=None):
    '''
    Will convert into bytes and optionally resize an image that is a file or a base64 bytes object.
    Turns into  PNG format in the process so that can be displayed by tkinter
    :param file_or_bytes: either a string filename or a bytes base64 image object
    :type file_or_bytes:  (Union[str, bytes])
    :param resize:  optional new size
    :type resize: (Tuple[int, int] or None)
    :return: (bytes) a byte-string object
    :rtype: (bytes)
    '''
    if isinstance(file_or_bytes, str):
        img = PIL.Image.open(file_or_bytes)
    else:
        try:
            img = PIL.Image.open(io.BytesIO(base64.b64decode(file_or_bytes)))
        except Exception as e:
            dataBytesIO = io.BytesIO(file_or_bytes)
            img = PIL.Image.open(dataBytesIO)

    cur_width, cur_height = img.size
    if resize:
        new_width, new_height = resize
        scale = min(new_height/cur_height, new_width/cur_width)
        img = img.resize((int(cur_width*scale), int(cur_height*scale)), PIL.Image.ANTIALIAS)
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    del img
    return bio.getvalue()

sg.theme('DarkGrey14')
# sg.set_options(font=font)

tab1_layout1 = [
                [
                sg.Multiline("Links\neach in new line", font = ("Arial", 10), text_color='red', size=(50,20), enable_events=True, key="_IN_URLS_"),
                ]
                ] 
tab1_layout2 = [
                # [sg.HorizontalSeparator(color = '24292e',pad=((0,0), (30,30)))],
                [sg.Push(), sg.Button("Analyze", enable_events = True, key = "_ANA_B_"),sg.Push()],
                [sg.Multiline(f"Analyzed info will\nappear here.",size=(50,5), enable_events=True, font = ("Arial", 11), text_color='magenta', key="_ANA_OUT_")],
                [sg.Push(),sg.Button("Download", enable_events = True, key = "_DOWN_B_"), sg.Push()],
                [sg.Push(),sg.Button("Clear Logs", enable_events = True, key = "_CLLOGS_B_"), sg.Push()]
                ]
tab1_layout = [
                [sg.T("Insert links into the window below.\nNext press Analyze to get info, or press Download to head straight to download.", font = ("Arial", 12), text_color='orange')],
                [sg.Radio('Input box', "source", default = True, tooltip = "Input box below", key="_SELECTED_SOURCE_MULTI_"), sg.Radio('File', "source", tooltip = "input_urls.txt", key="_SELECTED_SOURCE_FILE_"),sg.Push()],
                [sg.Column(tab1_layout1, key="_COL1_"), sg.Column(tab1_layout2,key="_COL2_")],
                [sg.Multiline(f"Logging... will happen after pressing 'Download' or 'Analyze' button", size=(50,10), enable_events=True, key="_LOGS_OUT_")],
                [sg.ProgressBar(0, orientation='h', size=(50,15), expand_x = True, key='_BAR_OUT_'), sg.T('NaN/NaN',enable_events=True, key='_TXT_OUT_')]
               ]
    



tab2_layout1 = [
            
            ]

tab2_layout2 = [
            [sg.Listbox(values=[], enable_events=True, expand_x = True, expand_y = True, size=(40,20), key='_FILE_LIST_')],
            ]

tab2layout1and2 = [
    [sg.Column(tab2_layout1,element_justification='top', expand_y = True, key = '_CHECKBOXS_COLUMN_'), sg.Column(tab2_layout2,expand_y = True, element_justification='top')],
    [sg.Push(),sg.Text('Resize to'), sg.In(500, size=(5,1), key='_RESIZE_W_'), sg.In(500, size=(5,1), key='_RESIZE_H_'),sg.Push(),sg.T("\tImage ->")]
]  
tab2_layout3 = [
                [sg.Image(key='_IMAGE_', )]
            ]

tab2_layout =  [[sg.Push(),sg.T('Here you can quickly share obtained pictures'),sg.Push()],
                [sg.Text('Folder'), sg.In(f"{os.getcwd()}/{output_folder_name}",size=(60,1), enable_events=True ,key='_IN_FOLDER_'), sg.FolderBrowse(initial_folder = f"{os.getcwd()}/{output_folder_name}", change_submits = True, key="_IN_BROWSE_SHARE_")],
                [sg.Column(tab2layout1and2, element_justification='top',expand_y = True), sg.Column(tab2_layout3, element_justification='c')],
                [sg.Button("Copy selected",enable_events=True, key="_COPY_SELECTED_"), sg.T("", key = "_COPIED_CONF_")]
               ] 

tab3_layout = [[sg.T('Debug')]]   

tab4_layout = [[sg.T('About')],
               [sg.T("Source for tab2 layout: \nhttps://www.pysimplegui.org/en/latest/cookbook/#recipe-convert_to_bytes-function-pil_IMAGE_viewer")],
               ]   

layout = [
    [
     sg.TabGroup([[sg.Tab('Download', tab1_layout, key = "_TAB1_"), 
                   sg.Tab('Share', tab2_layout, key = "_TAB2_"),
                   sg.Tab('Debug', tab3_layout, key = "_TAB3_"),
                   sg.Tab('About', tab4_layout, key = "_TAB4_"),
                   ]], expand_x=True, expand_y=True, tab_location = 'top', font = ("Arial", 15) ),
    ],
    [
        sg.Button("Exit", enable_events = True, key = "_EXIT_B_")

    ]
]

window = sg.Window("Flickr Image Downloader", layout,
                auto_size_text=True,
                auto_size_buttons=True,
                resizable=True,
                grab_anywhere=False,
                border_depth=2,
                finalize=True,
                size=[700,700],
                # element_justification='top',
                )
window.bind('<Configure>',"Event")

## download tab
window['_IN_URLS_'].expand(True,False)
window['_COL1_'].expand(True,True)
window['_COL2_'].expand(True,True)
window['_LOGS_OUT_'].expand(False, True)
window['_BAR_OUT_'].expand(True,False)
window['_TXT_OUT_'].expand(True,False)
window['_EXIT_B_'].expand(True,False)
window['_LOGS_OUT_'].expand(True, False)



## share tab
window['_FILE_LIST_'].expand(False, True)

timecopied = 0
# i = 1
while True:
    event, values = window.read()
    if event == "_EXIT_B_" or event == sg.WIN_CLOSED:
        break

    if time.time() - timecopied > 2:
        window['_COPIED_CONF_'].update("")
        # print("Copy time: " + str(timecopied) + "\tCurrent time: "+ str(time.time()) + "\tDifference: " + str(time.time() - timecopied))

# Tab2 Share

    if event == '_IN_FOLDER_':                         # Folder name was filled in, make a list of files in the folder
        folder = values['_IN_FOLDER_']
        try:
            file_list = os.listdir(folder)         # get list of files in folder
        except:
            file_list = []
        fnames = [f for f in file_list if os.path.isfile(
            os.path.join(folder, f)) and f.lower().endswith((".png", ".jpg", "jpeg", ".tiff", ".bmp"))]
        window['_FILE_LIST_'].update(fnames)
        addedlayout = []                 # Create an empty list for the user's picks to be appended to 
        for option in fnames:     # Loop through the user's picks, adding the checked choices to a new layout
            addedlayout.append([sg.Check(option, key=f'_{option}PICK')])
        addedlayout.append([sg.VPush()])    
        window.extend_layout(window['_CHECKBOXS_COLUMN_'], addedlayout) # Extend the -CHECK_PICK- column with the new layout
        window['_FILE_LIST_'].expand(True, True)
        window.refresh()

    elif event == '_FILE_LIST_':    # A file was chosen from the listbox
        try:
            filename = os.path.join(values['_IN_FOLDER_'], values['_FILE_LIST_'][0])
            if values['_RESIZE_W_'] and values['_RESIZE_H_']:
                new_size = int(values['_RESIZE_W_']), int(values['_RESIZE_H_'])
            else:
                new_size = None
            window['_IMAGE_'].update(data=convert_to_bytes(filename, resize=new_size))
        except Exception as E:
            print(f'** Error {E} **')
            pass        # something weird happened making the full filename
    if event == '_COPY_SELECTED_':
        justChecked = [element[1:-4] for element in values if values[element]==True and 'PICK' in element ] #values[-4:] == 'PICK']
        print(f"Selected images: {justChecked}")
        try:
            SharingVariable
            clipboard = ''
            for i in range(len(justChecked)):
                try:
                    clipboard += f'{SharingVariable[justChecked[i]]}\n'  
                except KeyError:
                    print(f"No image source found for: {justChecked[i]}")

            pyperclip.copy(clipboard)
            print("Clipboard content:\n" + clipboard)
            window['_COPIED_CONF_'].set_size((25,1))
            window['_COPIED_CONF_'].update("Copied!")
            timecopied = time.time()
            window['_COPY_SELECTED_'].update("Copy selected")
        except NameError:
            error_message = "Error: Source file for downloaded images not available.\nPlease download images first, then not closing app Share them.\nOtherwise please check debugging.txt"
            print(error_message)
            window['_COPIED_CONF_'].set_size((55,3))
            window['_COPY_SELECTED_'].update("Copy selected Try again")
            window['_COPIED_CONF_'].update(error_message)
            
# Tab1 Downlaod
    if event == "Event":
        multiline_size = window['_IN_URLS_'].get_size()
        # window['_IN_URLS_'].update(f"window size: {window.size[0]}x{window.size[1]}\nMultiline size: {multiline_size[0]}x{multiline_size[1]}")
        # window['_BAR_OUT_'].update(i)
        # window['_TXT_OUT_'].update(f"{i}/{100}")
        # i += 1

    if event == '_CLLOGS_B_':
        window['_LOGS_OUT_'].update("Nothing to show")
        window['_LOGS_OUT_'].set_vscroll_position(1)

    if event == '_ANA_B_': # pressed "Analyse" button
        if window['_SELECTED_SOURCE_MULTI_'].get():
            multi_input = window['_IN_URLS_'].get()
            input_urls_var = []
            for line in multi_input.splitlines():
                input_urls_var.append(line.strip())
                #input_urls_var.append(line[:-1].strip())

        elif window['_SELECTED_SOURCE_FILE_'].get():
            try:
                input_urls_var = open(input_urls, 'r')
            except FileNotFoundError:
                input_urls_var = open(input_urls, 'x')
                window['_LOGS_OUT_'].update("No input file found...\nscript is sad and angry because of you now")
                window['_LOGS_OUT_'].set_vscroll_position(1)
                print("No input file found, script is sad and angry because of you now")
            
            # window['_IN_URLS_'].update('')
            # out = ''
            # for line in input_urls_var:
            #     out += line
            # window['_IN_URLS_'].update(out)

        out = ''
        seen = set()
        duplicates_counter = 0
        links_count = 0
        for line in input_urls_var:
            if line.strip() in seen:
                duplicates_counter += 1
            else:
                seen.add(line.strip())
                links_count += 1
                out += line.strip() + "\n"
            
        window['_IN_URLS_'].update(out)
                                   
        try:
            outputted_file = open(exported_file, 'w')
        except FileNotFoundError:
            outputted_file = open(exported_file, 'x')  
        
        if Debugging == 2:
            debugging_file = 'debugging.txt'
            try:
                debug = open(debugging_file, 'w')
            except FileExistsError:
                debug = open(debugging_file, 'x')
        
        CURR_DIR = os.getcwd()
        #if folder program already is in is the output folder, do not do anything.
        if CURR_DIR.split("/")[-1] != output_folder_name: #WINDOWS ALERT
                
            try:
                os.mkdir(f'{CURR_DIR}/{output_folder_name}')
            except FileExistsError:
                pass
            os.chdir(f'{CURR_DIR}/{output_folder_name}')

        Debug_Message1 = f"Files will be saved: {os.getcwd()}"
        if Debugging == 1:
            print(Debug_Message1)
        elif Debugging == 2:
            print(Debug_Message1)
            debug.write(Debug_Message1)
        window['_LOGS_OUT_'].update(f"{window['_LOGS_OUT_'].get()}\n{Debug_Message1}\n")
        window['_LOGS_OUT_'].set_vscroll_position(1)
        
        Debug_Message2 = f"{duplicates_counter} duplicates were found and removed, photos to download: {links_count}\n"
        if Debugging > 0:
            print(Debug_Message2)
            window['_ANA_OUT_'].update(Debug_Message2)
        if Debugging == 2:
            debug.write(Debug_Message2 + "\n")

        window['_BAR_OUT_'].update(max = links_count, current_count = 0)
        window['_TXT_OUT_'].update(f"{0}/{links_count}")

        if window['_SELECTED_SOURCE_FILE_'].get():
            input_urls_var.close()

        outputted_file.close()
        if Debugging == 2:
            debug.close()

        os.chdir(CURR_DIR)

    if event == '_DOWN_B_':# pressed "Download" button
        SharingVariable = dict()
        if window['_SELECTED_SOURCE_MULTI_'].get():
            multi_input = window['_IN_URLS_'].get()
            input_urls_var = []
            for line in multi_input.splitlines():
                input_urls_var.append(line[:-1].strip())
        elif window['_SELECTED_SOURCE_FILE_'].get():
            try:
                input_urls_var = open(input_urls, 'r')
            except FileNotFoundError:
                input_urls_var = open(input_urls, 'x')
                window['_LOGS_OUT_'].update("No input file found...\nscript is sad and angry because of you now")
                window['_LOGS_OUT_'].set_vscroll_position(1)
                print("No input file found, script is sad and angry because of you now")
            
        seen = set()
        duplicates_counter = 0
        links_count = 0
        for line in input_urls_var:
            if line.strip() in seen:
                duplicates_counter += 1
            else:
                seen.add(line.strip())
                links_count += 1
        try:
            outputted_file = open(exported_file, 'w')
        except FileNotFoundError:
            outputted_file = open(exported_file, 'x')  
        
        if Debugging == 2:
            debugging_file = 'debugging.txt'
            try:
                debug = open(debugging_file, 'w')
            except FileExistsError:
                debug = open(debugging_file, 'x')
        
        CURR_DIR = os.getcwd()
        #if folder program already is in is the output folder, do not do anything.
        if CURR_DIR.split("/")[len(CURR_DIR.split("/"))-1] != output_folder_name: #WINDOWS ALERT  
            try:
                os.mkdir(f'{CURR_DIR}/{output_folder_name}')
            except FileExistsError:
                pass
            os.chdir(f'{CURR_DIR}/{output_folder_name}')

        Debug_Message1 = f"Files will be saved: {os.getcwd()}"
        if Debugging == 1:
            print(Debug_Message1)
        elif Debugging == 2:
            print(Debug_Message1)
            debug.write(Debug_Message1)
        window['_LOGS_OUT_'].update(f"{window['_LOGS_OUT_'].get()}\n{Debug_Message1}\n\n")
        window['_LOGS_OUT_'].set_vscroll_position(1)

        Debug_Message2 = f"{duplicates_counter} duplicates were found and removed, photos to download: {links_count}\n"
        if Debugging > 0:
            print(Debug_Message2)
            window['_ANA_OUT_'].update(Debug_Message2)
        if Debugging == 2:
            debug.write(Debug_Message2 + "\n")

        window['_BAR_OUT_'].update(max = links_count, current_count = 0)
        window['_TXT_OUT_'].update(f"{0}/{links_count}")

        statisctics = [0,0] #[success, error]
        nr_of_photo = 1

        for url in seen:

            window['_BAR_OUT_'].update(nr_of_photo-1)
            window['_TXT_OUT_'].update(f"{nr_of_photo}/{links_count}")

            url = url.replace('\n',"")
            Debug_Message3 = f"{nr_of_photo}: Gathering data for: {url}"
            if Debugging > 0:
                print(Debug_Message3)
            if Debugging == 2:
                debug.write(Debug_Message3)
            window['_LOGS_OUT_'].update(f"{window['_LOGS_OUT_'].get()}\n{Debug_Message3}\n")
            window['_LOGS_OUT_'].set_vscroll_position(1)

            if url.rfind("sizes") != -1: #check if photo link is in change sizes site
                url = url[0:url.rfind("sizes")]
                Debug_Message4 = "\tURL has been corrected"
                if Debugging > 0:
                    print(Debug_Message4)
                if Debugging == 2:
                    debug.write(Debug_Message4 + '\n')
                window['_LOGS_OUT_'].update(f"{window['_LOGS_OUT_'].get()}\n{Debug_Message4}\n")
                window['_LOGS_OUT_'].set_vscroll_position(1)
                
            html = requests.get(url).text
            output = []
            searchstring ='params: {"photoModel":'
            for line in iter(html.splitlines()):
                if searchstring in line:
                    output.append(line)
            try:
                output = output[0][13:]
            except IndexError:
                Debug_Message5 = "\tPhoto could not be obtained, wrong address probably"
                if Debugging > 0:
                    print(Debug_Message5)
                if Debugging == 2:
                    debug.write(Debug_Message5)
                window['_LOGS_OUT_'].update(f"{window['_LOGS_OUT_'].get()}\n{Debug_Message5}\n")
                window['_LOGS_OUT_'].set_vscroll_position(1)
                statisctics[1] += 1
                continue
            Debug_Message6 = "\tGathered source... continuing"
            if Debugging > 0:
                print(Debug_Message6)
            if Debugging == 2:
                debug.write(Debug_Message6 + "\n")
            window['_LOGS_OUT_'].update(f"{window['_LOGS_OUT_'].get()}\n{Debug_Message6}\n")
            window['_LOGS_OUT_'].set_vscroll_position(1)

            # yup, it is required
            false = False
            true = True
            null = -1
            outputdict = dict(eval(output))["photoModel"]['sizes']
            # outputdict = outputdict["photoModel"]['sizes']
            # print(outputdict)
            all_sizes = list(outputdict.keys()) 
            raw_url = outputdict[all_sizes[-1]]['src']
            direct_url = 'https://' + raw_url.replace('\/', '/')[2:]

            Debug_Message7 = f"\tAll image sizes available: {all_sizes}"
            Debug_Message8 = f"\tDirect url: {direct_url}"
            # Debug_Message8 = f"\tDirect url: {direct_url}, raw url for debugging: {raw_url}"
            if Debugging > 0:
                print(Debug_Message7)
                print(Debug_Message8)
            if Debugging == 2:
                debug.write(Debug_Message7)
                debug.write("\n" + Debug_Message8)

            window['_LOGS_OUT_'].update(f"{window['_LOGS_OUT_'].get()}\n{Debug_Message7}\n")
            window['_LOGS_OUT_'].set_vscroll_position(1)
            window['_LOGS_OUT_'].update(f"{window['_LOGS_OUT_'].get()}\n{Debug_Message8}\n\n")
            window['_LOGS_OUT_'].set_vscroll_position(1)

            if FlickrFileNames:
                try:
                    titled_name = html[html.find('<title>'):html.find('</title>')].replace("<title>", '')
                    # titled_name = titled_name[:titled_name.find(' |')].replace(' ','_').replace("'","").replace("(", '').replace(")",'').replace("-", "_")
                    titled_name = titled_name[:titled_name.find(' |')]
                    titled_name = re.sub('[^a-zA-Z0-9 \n\.]', '', titled_name).replace('.','').replace(' ','_')
                    if titled_name[:8] == 'Untitled':
                        titled_name = titled_name + "_" + str(datetime.now().strftime("%d%m%Y_%H%M%S%f"))
                    titled_name = f'{titled_name}_{str(all_sizes[-1])}{direct_url[direct_url.rfind("."):] }'
                    titled_name = re.sub(r'&#x\.\.;',r'_', titled_name) 
                except:
                    titled_name = f'NoCuteFilenameFound.{direct_url[direct_url.rfind("."):]}'
                
                #check if photo title was a duplicate 
                if titled_name in custom_file_names:
                    titled_name = titled_name[:titled_name.find(".")] + "_" + str(datetime.now().strftime("%d%m%Y_%H%M%S%f")) + titled_name[titled_name.find("."):]
                    custom_file_names.add(titled_name)
                else:
                    custom_file_names.add(titled_name)

                if Debugging == 0 and DownloadFiles:
                    ddownloader(direct_url, 0, titled_name)
                elif Debugging == 1:
                    Debug_Message9 = f"\tCustom filename: {titled_name}\n"
                    print(Debug_Message9)
                    window['_LOGS_OUT_'].update(f"{window['_LOGS_OUT_'].get()}\n{Debug_Message9}\n")
                    window['_LOGS_OUT_'].set_vscroll_position(1)

                    if DownloadFiles:
                        ddownloader(direct_url, 0, titled_name)
                elif Debugging == 2:
                    Debug_Message9 = f"\tCustom filename: {titled_name}\n"
                    print(Debug_Message9)
                    window['_LOGS_OUT_'].update(f"{window['_LOGS_OUT_'].get()}\n{Debug_Message9}\n\n")
                    window['_LOGS_OUT_'].set_vscroll_position(1)
                    if DownloadFiles:
                        ddownloader(direct_url, 0, titled_name)
                    debug.write(f"\n\tFile saved with a cute {titled_name} custom filename!\n\n") 
                    window['_LOGS_OUT_'].update(f"{window['_LOGS_OUT_'].get()}\n\tFile saved with a cute {titled_name} custom filename!\n\n")
                    window['_LOGS_OUT_'].set_vscroll_position(1) 

            else: #if no flickr file names
                if Debugging == 0 and DownloadFiles:
                    ddownloader(direct_url, 0)
                elif Debugging == 1 and DownloadFiles:
                    ddownloader(direct_url, 1)
                elif Debugging == 2 and DownloadFiles:
                    outputt = ddownloader(direct_url, 2)
                    debug.write(outputt + '\n')  

            

            window.refresh() 

        try:
            if sum(statisctics) != links_count:
                print("some files were not downloaded")
                window['_LOGS_OUT_'].update(f"{window['_LOGS_OUT_'].get()}\nsome files were not downloaded\n")
                window['_LOGS_OUT_'].set_vscroll_position(1)
            Debug_MessageN = f"Total files requested: {links_count} ({sum(statisctics)}), Success: {statisctics[0]}, Errors: {statisctics[1]}\nSuccess percentage: {statisctics[0]/sum(statisctics)*100:.2f}%"
            print(Debug_MessageN)
            window['_LOGS_OUT_'].update(f"{window['_LOGS_OUT_'].get()}\n{Debug_MessageN}\n")
            window['_LOGS_OUT_'].set_vscroll_position(1)
            window['_BAR_OUT_'].update(nr_of_photo)

            if Debugging == 2:
                debug.write(Debug_MessageN)
        except ZeroDivisionError:
            pass

        if window['_SELECTED_SOURCE_FILE_'].get():
            input_urls_var.close()
        outputted_file.close()
        if Debugging == 2:
            debug.close()

        os.chdir(CURR_DIR)
        del links_count
        del statisctics
        del nr_of_photo

window.close()