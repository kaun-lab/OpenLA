# -*- coding: utf-8 -*-
"""
Created on Wed Feb 22 17:10:08 2017

@author: Nicholas Mei
"""

import sys
import os
import time
from functools import partial
import multiprocessing as mp
import numpy as np
import cv2
import json

#If we are using python 2.7 or under
if sys.version_info[0] < 3:
    import Tkinter as tk
    import tkFileDialog as filedialog
    import tkMessageBox as messagebox
      
#If we are using python 3.0 or above
elif sys.version_info[0] >= 3:
    import tkinter as tk
    import tkinter.filedialog as filedialog
    import tkinter.messagebox as messagebox
    
#import flyOp_analysis
    
class create_tool_tip(object):
    '''
    Create a tool tip for a given widget
    '''
    def __init__(self, widget, ttip_text='widget description'):
        self.widget = widget
        self.ttip_text = ttip_text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.close)
    def enter(self, event=None):
        x, y = (0,0)
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.ttip_text, padx=5,
                       background='#FFFFB2', relief='solid', borderwidth=1,
                       font=("ariel", "10", "normal"))
        label.pack()
    def close(self, event=None):
        if self.tw:
            self.tw.destroy()    
    
    

class Application(tk.Frame):    
    #============ Vars and intialization ===============
    def define_variables(self):
        self.factors = ["IAA", "IAA+EtOH"]
        self.factor_var = tk.StringVar(self.master)
        self.factor_var.set(self.factors[0])
    
    def dir_list_init(self, dir_list):
        if sys.platform == 'win32' or sys.platform == "darwin":
            desktop_path = os.path.abspath(os.path.expanduser("~/Desktop/"))
            
            if dir_list.size() > 0:
                dir_list.delete(0,tk.END)
            dir_list.insert(0, desktop_path)
    
    #============ work horse functions =================
    def choose_dir(self, root):
        dir_path = filedialog.askdirectory(parent=root, title='Select the directory where you wish to activity assay data to:', mustexist=True)
        return dir_path
        
    def choose_file(self, root, text):
        file_path = filedialog.askopenfilename(parent=root, title=text)
        return file_path
        
    def get_preview_img(self):
        cam = cv2.VideoCapture(0)       
        preview_img = None
        for x in range(30):
            ret, preview_img = cam.read()        
        cam.release()
        
        return preview_img

        
    #================= Handler functions ========================   
    def on_win_close(self):
        self.master.destroy()
        self.master.quit()        
        
    def handle_dir_choose(self, root, dir_list):       
        dir_path = self.choose_dir(root)
        
        if dir_list.size() > 0:
            dir_list.delete(0,tk.END)
        dir_list.insert(0, dir_path)   
    
    #================= GUI widgets ========================
    def create_widgets(self):
        
        #---------------------- Main Frame -----------------------------
        top_frame = tk.Frame(self.master)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=15, pady=5)
        
            #+++++++++++++++++ Choose Experiments to Analyze ++++++++++++++++
        choose_expt_btn = tk.Button(top_frame, text="Choose expt DIR",
                                    pady=2, command=None)
                                    
        choose_expt_tooltxt = "Choose a directory containing 'ALL' your experiment results"
        create_tool_tip(choose_expt_btn, choose_expt_tooltxt)
        
        choose_expt_btn.pack(side=tk.LEFT)
       
            #+++++++++++++++++ Select a factor to add data to +++++++++++++
        select_factor_option = tk.OptionMenu(top_frame, self.factor_var,
                                             *self.factors, command=None) 
                                             
        select_factor_option.pack(side=tk.RIGHT)
        
            #+++++++++++++++++ Remove currently selected factor ++++++++++
        delete_factor_btn = tk.Button(top_frame, text="Delete current factor",
                                      pady=2, command=None)      
        
        delete_factor_btn.pack(side=tk.RIGHT)
        
            #+++++++++++++++++ Create new factor +++++++++++++++++++++++++
        create_factor_btn = tk.Button(top_frame, text="Create new factor", 
                                      pady=2, command=None)
        
        create_factor_btn.pack(side=tk.RIGHT)
        
        #---------------------- Data and Factor Frame --------------------
        mid_frame = tk.Frame(self.master)
        mid_frame.pack(side=tk.TOP, fill=tk.X, padx=15, pady=5)
        
            #----------------- Scroll list for found expt files -------------
        expts_scrollbar = tk.Scrollbar(mid_frame)
        expts_listbox = tk.Listbox(mid_frame, width=80, yscrollcommand=expts_scrollbar.set)
        
        expts_listbox.pack(side=tk.LEFT, fill=tk.BOTH)
        expts_scrollbar.pack(side=tk.LEFT, fill=tk.Y)        
        expts_scrollbar.config(command=expts_listbox.yview)
        
            #------------------ add/remove frame button frame -------------        
        spacer_frame = tk.Frame(mid_frame)
        spacer_frame.pack(side=tk.LEFT, fill=tk.X)
        
                #+++++++++++++++++++ add data to factor button ++++++++++++
        add_to_factor_btn = tk.Button(spacer_frame, text="Add\n--->",
                                      pady=2, command=None)
        add_to_factor_btn.pack(fill=tk.X)
        
                #+++++++++++ remove data from factor button +++++++++++++++
        rem_from_factor_btn = tk.Button(spacer_frame, text="Remove\n<---",
                                      pady=2, command=None)
        rem_from_factor_btn.pack(fill=tk.X)
        
            #----------------- Scroll list for factors -------------
        factor_scrollbar = tk.Scrollbar(mid_frame)
        
        factor_listbox = tk.Listbox(mid_frame, width=80, yscrollcommand=factor_scrollbar.set)
        factor_listbox.pack(side=tk.LEFT, fill=tk.BOTH)
        factor_scrollbar.pack(side=tk.LEFT, fill=tk.Y) 

        factor_scrollbar.config(command=factor_listbox.yview)
        
        
#        #+++++++++++++++++++++++ Expt Duration +++++++++++++++++++++++++
#        expt_dur_frame = tk.Frame(top_frame)
#        expt_dur_frame.pack(side=tk.LEFT, fill=tk.X, pady=15)
#        
#        expt_dur_label  = tk.Label(expt_dur_frame, text="Experiment duration\nin seconds:")
#        expt_dur_entry = tk.Entry(expt_dur_frame, textvariable='', justify=tk.CENTER)
#        
#        expt_dur_label.pack(side=tk.TOP)
#        expt_dur_entry.pack(side=tk.TOP)
#        
#        #+++++++++++++++++++++++ Stim on time ++++++++++++++++++++++++++
#        stim_on_frame = tk.Frame(top_frame)
#        stim_on_frame.pack(side=tk.LEFT, fill=tk.X, pady=15, padx=30)
#        
#        stim_on_label = tk.Label(stim_on_frame, text="Time until stimulus\n onset in seconds:")
#        stim_on_entry  = tk.Entry(stim_on_frame, textvariable='', justify=tk.CENTER)
#        
#        stim_on_label.pack(side=tk.TOP)
#        stim_on_entry.pack(side=tk.TOP)
#        
#        #+++++++++++++++++++++++ Stim duration +++++++++++++++++++++++++
#        stim_dur_frame = tk.Frame(top_frame)
#        stim_dur_frame.pack(side=tk.RIGHT, fil=tk.X, pady=15)
#        
#        stim_dur_label = tk.Label(stim_dur_frame, 
#                                  text = "Stimulus duration\n in seconds:")
#        stim_dur_entry = tk.Entry(stim_dur_frame, textvariable='', 
#                                  justify=tk.CENTER)
#        
#        stim_dur_label.pack(side=tk.TOP)
#        stim_dur_entry.pack(side=tk.TOP)
#        
#        #--------------------- Arduino settings frame ------------------           
#        arduino_frame = tk.Frame(self.master, padx=30)
#        arduino_frame.pack(side=tk.TOP, fill= tk.X, padx=15)
#            
#            #++++++++++++++++++++++++ LED freq ++++++++++++++++++++++++++++
#        led_freq_frame = tk.Frame(arduino_frame)
#    
#        led_freq_label = tk.Label(led_freq_frame, 
#                                  text="Opto stim\nfrequency in Hz:")
#        led_freq_entry = tk.Entry(led_freq_frame, textvariable='', 
#                                  justify=tk.CENTER)    
#        
#            #++++++++++++++++++++++++ LED duration ++++++++++++++++++++++++++++
#        led_dur_frame = tk.Frame(arduino_frame)
#    
#        led_dur_label = tk.Label(led_dur_frame, 
#                                 text="Opto stim\npulse width in ms:")
#        led_dur_entry = tk.Entry(led_dur_frame, textvariable='', 
#                                 justify=tk.CENTER)
#        led_dur_tooltip_txt = "Specify the amount of time the LED is on for a given frequency.\n***BEWARE!*** Setting too high a pulse width may prevent\nflashing from achieving the desired frequency!"
#        create_tool_tip(led_dur_entry, led_dur_tooltip_txt)
#                    
#        #++++++++++++++++++++ packing LED dur ++++++++++++++++++++++++   
#        led_dur_frame.pack(side=tk.RIGHT,fill=tk.X, pady=15)                       
#        led_dur_label.pack(side=tk.TOP)
#        led_dur_entry.pack(side=tk.TOP)
#        
#        #++++++++++++++++++++ packing LED freq +++++++++++++++++++++++   
#        led_freq_frame.pack(side=tk.RIGHT,fill=tk.X, pady=15, padx=30)     
#        led_freq_label.pack(side=tk.TOP)
#        led_freq_entry.pack(side=tk.TOP)
#        
#        #------------------ other options Frame -----------------------
#        #write_video, write_csv, fps_cap
#        other_opt_frame = tk.Frame(self.master, padx=30, pady=15, 
#                                   borderwidth=1, relief=tk.SUNKEN)
#        other_opt_frame.pack(side=tk.TOP, padx=15, pady=15, fill=tk.X)
#        
#        write_vid_checkbox = tk.Checkbutton(other_opt_frame, 
#                                            text="Write .AVI video?", 
#                                            variable=self.write_vid)
#        write_vid_checkbox.var = self.write_vid 
#        write_vid_checkbox.pack(side=tk.LEFT)
#        
#        write_csv_checkbox = tk.Checkbutton(other_opt_frame, 
#                                            text="Write .CSV file?", 
#                                            variable=self.write_csv)
#        write_csv_checkbox.var = self.write_csv
#        write_csv_checkbox.pack(side=tk.LEFT, padx=50)
#        
#        #+++++++++++++++++++++++ fps cap frame +++++++++++++++++++++++++
#        fps_cap_frame = tk.Frame(other_opt_frame)
#        fps_cap_frame.pack(side=tk.RIGHT, fil=tk.X,  pady=10)
#        
#        fps_cap_label = tk.Label(fps_cap_frame, text = "FPS to enforce:")
#        fps_cap_entry = tk.Entry(fps_cap_frame, textvariable=self.fps_cap, 
#                                 justify=tk.CENTER)
#        fps_cap_tooltip_txt = "Set the max frames per second\n to collect video at. Make sure your\ncamera can support the specified FPS."
#        create_tool_tip(fps_cap_entry, fps_cap_tooltip_txt)
#        
#        fps_cap_label.pack(side=tk.TOP)
#        fps_cap_entry.pack(side=tk.TOP)
#            
#        #------------------- Bottom Frame ------------------------------
#        #Preview video, set ROIs, halt Experiment    
#        bottom_frame = tk.Frame(self.master, padx=15)
#        bottom_frame.pack(side=tk.TOP, fill=tk.X)
#        
#        preview_btn= tk.Button(bottom_frame, text="Preview video", pady=2, 
#                               command=self.handle_preview_camera)
#        preview_btn.pack(side=tk.LEFT, fill = tk.X, pady=15, expand=1)    
#                
#        stop_btn = tk.Button(bottom_frame, text="Stop current experiment (!)", 
#                             pady=2, command = self.handle_emergency_stop)
#        stop_btn.pack(side=tk.RIGHT, fill=tk.X, pady=15, expand=1)
#        stop_tooltip_txt = "Will immediately halt the\n currently running experiment!"
#        create_tool_tip(stop_btn, stop_tooltip_txt)
#
#        #----------------------- ROI frame ------------------------------
#        roi_frame = tk.Frame(self.master, padx=15, borderwidth=1, 
#                             relief=tk.SUNKEN)
#        roi_frame.pack(side=tk.TOP, fill=tk.X, padx=15, pady=10)
#        
#        save_roi_btn = tk.Button(roi_frame, text="Save ROIs", pady=2, 
#                                 command=self.save_rois)
#        save_roi_tooltip_txt = "ROIs will be saved as: FlyActivityAssay_ROIs.json\nin the same folder as this UI script."
#        create_tool_tip(save_roi_btn, save_roi_tooltip_txt)
#        
#        set_roi_btn = tk.Button(roi_frame, text="Set ROIs", pady=2, 
#                                command=partial(self.handle_set_rois, save_roi_btn))
#        set_roi_btn.pack(side=tk.LEFT, fill = tk.X,expand=1, pady=15)
#        roi_tooltip_txt = "Set the regions of interest\n to quantitate activity over.\nAfter setting ROIs, the option\n to save them will appear."
#        create_tool_tip(set_roi_btn, roi_tooltip_txt)
#        
#        load_roi_btn = tk.Button(roi_frame, text="Load ROIs", pady=2, 
#                                 command=partial(self.load_rois, self.master, "Please select the ROIs.json file you wish to load "))
#        load_roi_btn.pack(side=tk.RIGHT, fill=tk.X,expand=1, pady=15)
#         
#        #-------------------- Save Directory Frame label ---------------------
#        save_dir_frame = tk.Frame(self.master, padx=15)
#        save_dir_frame.pack(side=tk.TOP, fill=tk.X)
#        
#        save_gen_label = tk.Label(save_dir_frame, 
#                                  text="Directory to save assay analysis and output to:")
#        save_gen_label.pack(side=tk.LEFT)
#        
#        #------------------ Save directory frame -------------------------
#        dir_frame = tk.Frame(self.master, padx=15)
#        dir_frame.pack(side=tk.TOP, fill=tk.X)
#    
#        dir_list = tk.Listbox(dir_frame, width=50, height=1)
#        dir_list.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=5)
#        
#        self.dir_list_init(dir_list)
#    
#        choose_dir = tk.Button(dir_frame, text='Choose', pady=0, 
#                               command = partial(self.handle_dir_choose, self.master, dir_list))
#        choose_dir.pack(side=tk.RIGHT, pady=5)
#           
#        #------------------- Run Frame ---------------------------------
#        run_frame = tk.Frame(self.master, padx=15)
#        run_frame.pack(side=tk.TOP, fill=tk.X)
#        
#        run_btn = tk.Button(run_frame, text="Start activity assay!", pady=2, 
#                            command = partial(self.handle_run, dir_list))
#        run_btn.pack( fill=tk.X, pady=5)
        
    
    def __init__(self, master=None):
        tk.Frame.__init__(self, master) 
        self.master=master
        #Handle user closing program via window close
        self.master.protocol("WM_DELETE_WINDOW", self.on_win_close)
        self.define_variables()
        self.create_widgets()       

if __name__ == '__main__': 
    root = tk.Tk()
    root.title("Fly Open Bar Analysis - User Interface")
    app = Application(master=root)
    app.mainloop()