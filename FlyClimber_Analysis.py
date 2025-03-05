import csv, glob, numpy as np, matplotlib.pyplot as plt, tkinter as tk, statsmodels.api as sm, math, spm1d, os
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from scipy.signal import savgol_filter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg



class EntryApp:
    def __init__(self,root):
        #Define necessary lists/variables
        self.search_fields = []
        self.Legend_info = []
        self.count=1

        self.root = root

        self.root.title("Enter Search Fields")
        self.root.geometry("420x220")
        self.var = IntVar()
        self.Image_save = BooleanVar()

        self.Column_entries=[[Label(self.root,text="Gene Name:"),Entry(self.root),
                Label(self.root,text="Sex:"),Entry(self.root),
                Label(self.root,text="Repeat:"),Entry(self.root),
                Label(self.root,text="Fly Age (Days):"),Entry(self.root)],
                [Label(self.root,text="Gene Name:"),Entry(self.root),
                Label(self.root,text="Sex:"),Entry(self.root),
                Label(self.root,text="Repeat:"),Entry(self.root),
                Label(self.root,text="Fly Age (Days):"),Entry(self.root)]]
        
        #Positions field inputs in tkinter window
        for i,item in enumerate(self.Column_entries):
            if i==0:
                Label(self.root,text="Control").grid(row=0,column=i,padx=5)
            row = 1
            for object in item:
                object.grid(row=row,column=i,padx=5)
                row +=1


        self.Add_group = tk.Button(self.root, text="Add Group",command=self.Add_fields)
        self.Add_group.grid(row=9,column=0,padx=5)
        self.Remove_group = tk.Button(self.root, text="Remove Group",command=self.Remove_fields)
        self.Remove_group.grid(row=9,column=1,padx=5)
        self.Create_graph = tk.Button(self.root, text="Create Graph",command=self.Get_inputs)
        self.Create_graph.grid(row=9,column=2,padx=5)

    #Function to add new search field
    def Add_fields(self):
        self.count += 1

        #Calculating what line new field should be on
        self.line = self.count//8

        #Adds new set of fields to entries list
        self.Column_entries.append([Label(self.root,text="Gene Name:"),Entry(self.root),
                    Label(self.root,text="Sex:"),Entry(self.root),
                    Label(self.root,text="Repeat:"),Entry(self.root),
                    Label(self.root,text="Fly Age (Days):"),Entry(self.root)])
    
        if self.line > 0:
            self.Column_entries[-1].insert(0,Label(self.root,text="---------"))

        #Positioning new fields in tkinter window
        for i,item in enumerate(self.Column_entries[-1]):
            item.grid(row=i+1+(self.line*9),column=self.count%8,padx=5)
        if self.count >=3 and self.line==0:
            self.root.geometry(f'{140*(self.count+1)}x{200*self.line+220}')
        elif self.line > 0:
            self.root.geometry(f'1120x{200*self.line+220}')
        else:
            self.root.geometry('420x220')
    
        #Repositioning buttons in window
        self.Add_group.grid(row=(self.line+1)*9+1,column=0,padx=5)
        self.Remove_group.grid(row=(self.line+1)*9+1,column=1,padx=5)
        self.Create_graph.grid(row=(self.line+1)*9+1,column=2,padx=5)


    #Function to add new search field
    def Remove_fields(self):

        if self.count > 0:
            self.count-=1

            #Calculating how many rows of fields there should be
            self.line = self.count//8

            #Removing last set of search fields and resizing tkinter window
            for item in self.Column_entries[-1]:
                item.destroy()
            del self.Column_entries[-1]
            if self.count >=3 and self.line==0:
                self.root.geometry(f'{140*(self.count+1)}x{200*self.line+220}')
            elif self.line > 0:
                self.root.geometry(f'1120x{200*self.line+220}')
            else:
                self.root.geometry('420x220')

            #Repositioning buttons
            self.Add_group.grid(row=(self.line+1)*9+1,column=0,padx=5)
            self.Remove_group.grid(row=(self.line+1)*9+1,column=1,padx=5)
            self.Create_graph.grid(row=(self.line+1)*9+1,column=2,padx=5)


    #Function to obtain inputs
    def Get_inputs(self):
        
        #Removes headers from list before getting inputs
        for item in self.Column_entries[:]:
            if isinstance(item[0],Label) and item[0].cget("text")=="---------":
                del item[0]

        self.search_fields=[]
        self.Legend_info=[]

        for item in self.Column_entries:
            parameters = []
            filename = []

            #Formats each field input appropriately before adding to search fields
            for i,object in enumerate(item):
                if i%2==1:
                    input = str(object.get())
                    #Gene name
                    if i==1 and input!='':
                        filename.append(input)
                        input = input+'_'
                    #Sex    
                    if i==3 and input!='':
                        filename.append(input)
                    #Repeat
                    if i==5 and input!='':
                        input = 'rpt'+input
                        filename.append(input)
                    #Age
                    if i==7 and input!='':    
                        input = input+'days'
                        filename.append(input)
                    if input != '':
                        parameters.append(input)
            if len(parameters)>0:
                self.search_fields.append(parameters)
                self.Legend_info.append('_'.join(filename))

        self.root.quit()
        self.root.destroy()
    

    #Accessing search parameters and Legend info outside class
    def Get_variables(self):
        return self.search_fields, self.Legend_info


#Creating window for field inputs
root = tk.Tk()
app = EntryApp(root)
root.mainloop()

search_fields,Legend_info = app.Get_variables()

#Finds all csv files in folder
all_csv_files = glob.glob('*.csv')

#Tests whether filename has search paramaters
def csv_filter(filename,i):
    global search_fields
    for item in search_fields[i]:
        if item not in filename:
            return False
    return True


#Function to collect relevant data based on search fields
def Data_collect(all_csv_files,i):
    Data=[]
    #Creates a list of csv files containing all search parameters
    filtered = [x for x in all_csv_files if csv_filter(x,i)]

    #Cycles through each file one at a time
    for item in filtered:
        #Opens csv file
        with open(item, newline='') as csvfile:
            read = csv.reader(csvfile,delimiter=',')
            if len(Data)==0:
                for count,row in enumerate(read):
                    if count != 0 and len(row)>1:
                        values = [float(x) for x in row[1:]]
                        Data.append([np.median(values)])
                    if len(row)==1:
                        Data.append(Data[count-2][-1])
            else:
                for count,row in enumerate(read):
                    if count != 0 and len(row)>1:
                        values = [float(x) for x in row[1:]]
                        Data[count-1].append(np.median(values))
                    if len(row)==1:
                        Data[count-1].append(Data[count-2][-1])
    

    return Data


#Collects all data from search fields
All_Data = []
for i,item in enumerate(search_fields):
    All_Data.append(Data_collect(all_csv_files,i))

x_axis = []
filtered = [x for x in all_csv_files if csv_filter(x,0)]

with open(filtered[0],newline='') as csvfile:
    read = csv.reader(csvfile,delimiter=',')
    for count,row in enumerate(read):
        if count!=0:
            x_axis.append(float(row[0]))

#----------------------------------------------------

# Class for interactive graph

class LivePlotApp:
    def __init__(self, root, All_Data, Legend_info):
        self.root = root
        self.root.title("Graph Preview")
        self.root.state('zoomed')  # Open in full screen (maximized) mode

        # Initialize attributes
        self.window_length_value = tk.StringVar()
        self.poly_order_value = tk.StringVar()
        self.mean_lines = []
        self.boundary_lines = []
        self.ticks = [5,10,15,20,25,30]
        self.generate_stats = False
        self.directory = None
        self.filename = None

        # Moving data to class variables
        self.Final_Data = [np.array(x,dtype=float) for x in All_Data]
        self.x_axis = x_axis
        self.Legend_info = Legend_info
        self.colors = ['black', 'orange', 'green', 'red', 'purple', 'grey', 'blue', 'yellow', 'cyan', 'pink']  # Initial colors
        self.window_length = 11
        self.poly_order = 2

        # Create Matplotlib figure and axis
        self.fig, self.ax = plt.subplots()
        self.legend = None
        self.plot_data()

        # Create a Tkinter canvas to embed the Matplotlib plot
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Create a frame for sliders
        self.slider_frame = tk.Frame(self.root)
        self.slider_frame.pack(side=tk.TOP, fill=tk.X, pady=10)

        label_font = ('Arial', 14)  # Define the font size for labels

        # Create a Tkinter scale (slider) for window length adjustment
        self.window_length_label = tk.Label(self.slider_frame, text="Window Length:", font=label_font)
        self.window_length_label.pack(side=tk.LEFT, padx=5)
        self.window_length_scale = ttk.Scale(self.slider_frame, from_=3, to=len(self.x_axis), orient=tk.HORIZONTAL, command=self.update_plot)
        self.window_length_scale.pack(side=tk.LEFT, fill=tk.X, expand=1, padx=5)
        self.window_length_scale.set(int(len(self.x_axis)/10))  # Set initial value for window length

        # Create a Tkinter entry to display window length
        self.window_length_entry = tk.Entry(self.slider_frame, textvariable=self.window_length_value, state='readonly', width=5, font=label_font)
        self.window_length_entry.pack(side=tk.LEFT, padx=5)

        # Get the current window length from the scale (slider)
        self.window_length = int(float(self.window_length_scale.get()))

        # Create a Tkinter scale (slider) for polynomial order adjustment
        self.poly_order_label = tk.Label(self.slider_frame, text="Polynomial Order:", font=label_font)
        self.poly_order_label.pack(side=tk.LEFT, padx=5)
        self.poly_order_scale = ttk.Scale(self.slider_frame, from_=1, to=5, orient=tk.HORIZONTAL, command=self.update_plot)
        self.poly_order_scale.pack(side=tk.LEFT, fill=tk.X, expand=1, padx=5)
        self.poly_order_scale.set(2)  # Set initial value for polynomial order

        # Create a Tkinter entry to display polynomial order
        self.poly_order_value.set("2")  # Set initial value for StringVar
        self.poly_order_entry = tk.Entry(self.slider_frame, textvariable=self.poly_order_value, state='readonly', width=5, font=label_font)
        self.poly_order_entry.pack(side=tk.LEFT, padx=5)

        # Get the current polynomial order from the scale (slider)
        self.poly_order = int(float(self.poly_order_scale.get()))

        # Create entry boxes for color input
        self.color_frame = tk.Frame(self.root)
        self.color_frame.pack(side=tk.TOP, fill=tk.X, pady=10)

        self.color_entries = []
        for i in range(len(self.Final_Data)):
            if i>0 and i%6==0:
                self.color_frame = tk.Frame(self.root)
                self.color_frame.pack(side=tk.TOP,fill=tk.X,pady=10)

            tk.Label(self.color_frame, text=f"Line {i+1} Color:", font=label_font).pack(side=tk.LEFT, padx=5)
            color_entry = tk.Entry(self.color_frame,width=8,font=label_font)  
            color_entry.pack(side=tk.LEFT, padx=5)
            color_entry.insert(0, self.colors[i])
            self.color_entries.append(color_entry)

        # Create button to apply color changes
        self.apply_color_button = tk.Button(self.color_frame, text="Apply Colors", command=self.apply_colors, font=label_font)
        self.apply_color_button.pack(side=tk.LEFT, padx=5)

        # Create a button to open the legend editing window
        self.edit_legend_button = tk.Button(self.color_frame, text="Edit Legend", command=self.open_legend_window, font=label_font)
        self.edit_legend_button.pack(side=tk.LEFT, padx=5)

        #Create a button to edit the x axis step
        self.edit_x_axis_button = tk.Button(self.color_frame,text="Edit x-axis",command=self.open_axis_window,font=label_font)
        self.edit_x_axis_button.pack(side=tk.LEFT, padx=5)

        #Create an entry box for the alpha significance level
        tk.Label(self.color_frame, text=f"Alpha Significance:", font=label_font).pack(side=tk.LEFT, padx=5)
        self.alpha_sig_value = tk.StringVar(value='0.05')
        self.alpha_sig_entry = tk.Entry(self.color_frame,textvariable=self.alpha_sig_value,width=8,font=label_font)
        self.alpha_sig_entry.pack(side=tk.LEFT,padx=5)

        # Create a Close button and align it to the right
        self.close_frame = tk.Frame(self.root)
        self.close_frame.pack(side=tk.TOP, fill=tk.X, pady=10)
        self.close_button = tk.Button(self.close_frame,text="Close",command=self.on_close,font=label_font)
        self.close_button.pack(side=tk.RIGHT, padx=5)

        #Generate save button and align to the right
        self.save_button = tk.Button(self.close_frame, text="Save as", command=self.open_save_window, font=label_font)
        self.save_button.pack(side=tk.RIGHT,padx=5)

        # Create a generate stats button and align it to the right
        self.generate_stats_button = tk.Button(self.close_frame,text="Get Stats", command=self.get_stats,font=label_font)
        self.generate_stats_button.pack(side=tk.RIGHT,padx=5)
        # Bind close event to handle when the window is closed
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)


    #Function to create initial graph
    def plot_data(self):

        #Smooths data
        self.Smoothed_Data = [np.transpose(savgol_filter(np.transpose(x),self.window_length,self.poly_order,mode='nearest')) for x in self.Final_Data]
        self.mean_lists = []
        self.boundary_lists = []

        #Creates family of lines for each data set - mean and confidence limits
        for item in self.Smoothed_Data:
            mean_list = []
            lower_list = []
            upper_list = []

            for j in item:
                mean = np.mean(j)
                sem = np.std(j)/np.sqrt(len(j))
                mean_list.append(mean)
                lower_list.append(mean-sem)
                upper_list.append(mean+sem)
            
            self.mean_lists.append(mean_list)
            self.boundary_lists.append([lower_list,upper_list])
        
        #Clears existing axis
        self.ax.clear()

        #Plots all lines
        for i,line in enumerate(self.mean_lists):
            self.ax.plot(self.x_axis,line,color=self.colors[i],label=f'{self.Legend_info[i]}')
            self.ax.fill_between(self.x_axis,self.boundary_lists[i][0],self.boundary_lists[i][1],color=self.colors[i],alpha=0.3)

        #Removes border between data and boundaries of the graph
        self.ax.set_xlim(3,30)

        #Add the legend
        if self.legend is not None:
            self.legend.remove()
        self.legend = self.ax.legend(loc='upper left')


    #Function to update plot when variables are changed
    def update_plot(self, event=None):

        # Get the current window length from the scale (slider)
        self.window_length = int(float(self.window_length_scale.get()))
        if self.window_length % 2 == 0:
            self.window_length += 1  # Ensure window length is odd

        # Update window length entry value
        self.window_length_value.set(str(self.window_length))

        # Get the current polynomial order from the scale (slider)
        self.poly_order = int(float(self.poly_order_scale.get()))

        # Update polynomial order entry value
        self.poly_order_value.set(str(self.poly_order))

        #Plot the Data
        self.plot_data()

        #Check to see if custom x-axis has been input
        if len(self.ticks)>0:
            self.ax.set_xticks(self.ticks)

        # Redraw the canvas
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()


    #Function for changing colours in graph
    def apply_colors(self):
        # Get the color values from the entry boxes and update the lines
        for i, color_entry in enumerate(self.color_entries):
            color = color_entry.get()
            self.colors[i] = color

        #Plot the Data
        self.plot_data()

        # Update the legend
        self.legend.remove()  # Remove the old legend
        self.legend = self.ax.legend(loc='upper left')  # Create a new legend

        # Redraw the canvas
        self.canvas.draw()


    #Function for opening legend editing window
    def open_legend_window(self):
        # Create a new window
        self.legend_window = tk.Toplevel(self.root)
        self.legend_window.title("Edit Legend")

        # Create entry boxes for each label
        self.legend_entries = []
        for i, label in enumerate(self.Legend_info):
            tk.Label(self.legend_window, text=f"Label {i+1}:", font=('Arial', 14)).pack(side=tk.TOP, pady=5)
            legend_entry = tk.Entry(self.legend_window, font=('Arial', 14))
            legend_entry.pack(side=tk.TOP, fill=tk.X, expand=1, pady=5)
            legend_entry.insert(0, label)
            self.legend_entries.append(legend_entry)

        # Create a button to apply the legend changes
        self.apply_legend_button = tk.Button(self.legend_window, text="Apply Legend", command=self.apply_legend, font=('Arial', 14))
        self.apply_legend_button.pack(side=tk.BOTTOM, fill=tk.X, pady=10)


    #Function for applying changes to the legend
    def apply_legend(self):
        # Get the legend values from the entry boxes and update the lines
        for i, legend_entry in enumerate(self.legend_entries):
            label = legend_entry.get()
            self.Legend_info[i] = label

        # Update the plot
        self.plot_data()

        # Redraw the canvas
        self.canvas.draw()

        # Close the legend window
        self.legend_window.destroy()


    #Function to open x-axis editing window
    def open_axis_window(self):
        #Create a new window
        self.axis_window = tk.Toplevel(self.root)
        self.axis_window.title("Edit x-axis")

        #Create label for entry box
        self.x_axis_label = tk.Label(self.axis_window, text="X-axis step:", font=('Arial',14))
        self.x_axis_label.pack(side=tk.TOP, fill=tk.X, pady=10)

        #Create entry box for x-axis step
        self.x_axis_entry = tk.Entry(self.axis_window,font=('Arial',14))
        self.x_axis_entry.pack(side=tk.TOP,fill=tk.X,pady=5)

        #Create button to apply changes to x-axis
        self.apply_x_axis_button = tk.Button(self.axis_window, text="Apply x_axis step", command=self.apply_x_axis,font=('Arial',14))
        self.apply_x_axis_button.pack(side=tk.BOTTOM, fill=tk.X, pady=10)


    #Function to apply changes to x-axis
    def apply_x_axis(self):
        
        #Retrieves new step for x-axis
        step = self.x_axis_entry.get()

        #Trims list to start at 3
        def trim_list(ticks):
            for index,num in enumerate(ticks):
                if num>=3:
                    return ticks[index:]

        #If valid step value was input, creates new x-axis
        if step:
            try:
                step = float(step)
                if step<=0:
                    raise ValueError("Step must be a positive number")
                self.ticks = list(np.arange(0,30,step))
                if self.ticks[-1]!=30:
                    self.ticks.append(30)
                
                self.ticks=trim_list(self.ticks)
                if self.ticks[0]!=3:
                    self.ticks.insert(0,3)
                self.ax.set_xticks(self.ticks)
                self.canvas.draw()
                self.axis_window.destroy()
            except ValueError as e:
                print(f"Invalid step {e}. Please enter a valid positive number")


    #Function to create and open save window
    def open_save_window(self):
        #Create a new window
        self.save_window = tk.Toplevel(self.root)
        self.save_window.title("Save as")

        #Bring save window to forefront
        self.save_window.attributes('-topmost',True)

        self.directory_frame = tk.Frame(self.save_window)
        self.directory_frame.pack(side=tk.TOP,fill=tk.X,pady=10)

        self.directory_label = tk.Label(self.directory_frame, text="Directory:", font=('Arial',14))
        self.directory_label.pack(side=tk.LEFT,fill=tk.X,padx=5)

        self.directory_entry = tk.Entry(self.directory_frame,font=('Arial',14))
        self.directory_entry.pack(side=tk.LEFT,fill=tk.X,padx=10)

        #If previous save directory was used, fills directory with the previous save directory
        if self.directory:
            self.directory_entry.delete(0,tk.END)
            self.directory_entry.insert(0,self.directory)

        self.directory_button = tk.Button(self.directory_frame, text="Browse", command=self.get_directory, font=('Arial',14))
        self.directory_button.pack(side=tk.LEFT,fill=tk.X,padx=5)

        self.filename_frame = tk.Frame(self.save_window)
        self.filename_frame.pack(side=tk.TOP,fill=tk.X,pady=10)

        self.filename_label = tk.Label(self.filename_frame, text="Filename:", font=('Arial',14))
        self.filename_label.pack(side=tk.LEFT,fill=tk.X,padx=5)

        self.filename_entry = tk.Entry(self.filename_frame,font=('Arial',14))
        self.filename_entry.pack(side=tk.LEFT,fill=tk.X,padx=5)

        #Fills field with previous filename or 'Graph' if no previous filename
        if self.filename:
            self.filename_entry.insert(0,self.filename)
        else:
            self.filename_entry.insert(0,"Graph")

        #Adds buttons to bottom of the window
        self.save_cancel_frame = tk.Frame(self.save_window)
        self.save_cancel_frame.pack(side=tk.BOTTOM,fill=tk.X,pady=10)

        self.cancel_button = tk.Button(self.save_cancel_frame, text="Cancel", command=self.cancel, font=('Arial',14))
        self.cancel_button.pack(side=tk.RIGHT,fill=tk.X,padx=5)

        self.save_graph_button = tk.Button(self.save_cancel_frame, text="Save", command=self.save_graph, font=('Arial',14))
        self.save_graph_button.pack(side=tk.RIGHT,fill=tk.X,pady=10)
    

    #Function to obtain a file directory to save files
    def get_directory(self):

        self.save_window.attributes('-topmost',False)

        #Opening window to search for file directory
        self.directory = filedialog.askdirectory()

        self.save_window.attributes('-topmost',True)

        #Filling directory into entry box
        if self.directory:
            self.directory_entry.delete(0,tk.END)
            self.directory_entry.insert(0,self.directory)


    #Function for cancel button to close save window
    def cancel(self):
        self.save_window.destroy()


    #Function for saving graph
    def save_graph(self):
        #Getting filepath
        self.directory = self.directory_entry.get()

        #Checks if the filepath is valid
        folder_path=False
        if os.path.exists(self.directory):
            folder_path = True
        
        #Saves graph if filepath is valid
        if folder_path==True:
            self.filename = self.filename_entry.get()
            filepath = os.path.join(self.directory,f"{self.filename}.png")

            #While loop to ensure files with the same filename aren't saved
            i=1
            while os.path.exists(filepath):
                filename=f"{self.filename}({i})"
                filepath = os.path.join(self.directory,f"{filename}.png")
                i+=1
            
            self.fig.savefig(filepath)
            tk.messagebox.showinfo(title="Saved", message="Graph saved successfully")
            self.save_window.destroy()
        
        else:
            tk.messagebox.showerror(title="Error", message="Invalid directory")
            

    #Function to open stats window
    def get_stats(self):
        # This function opens a window with the SPM graphs
        self.stats_window = tk.Toplevel(self.root)
        self.stats_window.title("SPM stats")
        self.stats_window.state('zoomed')

        #Separate control from test data
        self.stats_graph_labels = [f'{self.Legend_info[0]}x{x}' for x in self.Legend_info[1:]]
        self.Smoothed_control = self.Smoothed_Data[0]
        self.Smoothed_test = self.Smoothed_Data[1:]

        #Creates stats graphs and adds them to a dictionary
        self.Figures = {}
        for i,data in enumerate(self.Smoothed_test):
            fig = plt.figure()
            #Plots left subplot with original data
            ax = fig.add_subplot(1,2,1)
            ax.set_title(f'{self.stats_graph_labels[i]}')

            self.tick_labels = [int(x) if x.is_integer() else x for x in self.ticks]

            ax.plot(self.x_axis,self.mean_lists[0],color='black',label=f'{self.Legend_info[0]}')
            ax.fill_between(self.x_axis,self.boundary_lists[0][0],self.boundary_lists[0][1],color='black',alpha=0.3)
            ax.plot(self.x_axis,self.mean_lists[i+1],color='red',label=f'{self.Legend_info[i+1]}')
            ax.fill_between(self.x_axis,self.boundary_lists[i+1][0],self.boundary_lists[i+1][1],color='red',alpha=0.3)
            ax.set_xticks(self.ticks)
            ax.set_xticklabels(self.tick_labels)
            ax.legend(loc='upper left')
            ax.set_xlim(3,30)

            #Plots right subplot with statistical test
            ax = fig.add_subplot(1,2,2)

            t = spm1d.stats.ttest2(np.transpose(self.Smoothed_control), np.transpose(data))
            try:
                alpha = float(self.alpha_sig_entry.get())
                if alpha<0:
                    raise ValueError("Alpha must be a positive value")
                elif alpha>=1:
                    raise ValueError("Alpha must be below 1")
                alpha_corrected = alpha/len(self.Smoothed_test)
                ti = t.inference(alpha_corrected, two_tailed=True, interp=True)
                #Plotting stats
                ti.plot()
                ti.plot_threshold_label(fontsize=8)
                ti.plot_p_values(size=10, offset_all_clusters=(0,0.9))

                self.xtick_indexes = [x_axis.index(float(x)) for x in self.ticks]
                ax.set_xticks(self.xtick_indexes)
                ax.set_xticklabels(self.tick_labels)

                self.Figures[self.stats_graph_labels[i]] = fig
            except:
                raise ValueError("Alpha must be a number between 0 and 1")


        #Drop down menu for swapping between graphs
        self.stats_menu_frame = tk.Frame(self.stats_window)
        self.stats_menu_frame.pack(side=tk.TOP,fill=tk.X,pady=10)

        self.style = ttk.Style()
        self.style.configure('.',font=('Arial',14))
        
        self.selected_graph = tk.StringVar(value=self.stats_graph_labels[0])
        self.dropdown = ttk.OptionMenu(self.stats_menu_frame,self.selected_graph,self.stats_graph_labels[0],*self.stats_graph_labels,command=self.update_stats)
        self.dropdown['menu'].configure(font=('Arial',14))
        self.dropdown.pack(side=tk.RIGHT,fill=tk.X,padx=5)

        self.dropdown_label = tk.Label(self.stats_menu_frame,text="Menu:",font=('Arial',14))
        self.dropdown_label.pack(side=tk.RIGHT,fill=tk.X,padx=5)

        #Frame for graph
        self.stats_canvas_frame = tk.Frame(self.stats_window)
        self.stats_canvas_frame.pack(side=tk.TOP,fill=tk.X,pady=10)

        self.stats_canvas = FigureCanvasTkAgg(self.Figures[self.selected_graph.get()],master=self.stats_canvas_frame)
        self.stats_canvas_widget = self.stats_canvas.get_tk_widget()
        self.stats_canvas_widget.pack(fill=tk.X,expand=True)

        #Buttons to save and close window
        self.stats_save_frame = tk.Frame(self.stats_window)
        self.stats_save_frame.pack(side=tk.BOTTOM,fill=tk.X,pady=10)

        self.stats_close_button = tk.Button(self.stats_save_frame, text = "Close", command=self.cancel_stats, font=('Arial',14))
        self.stats_close_button.pack(side=tk.RIGHT,fill=tk.X,padx=5)

        self.save_all_stats_button = tk.Button(self.stats_save_frame, text="Save all", command=self.save_all_graphs, font=('Arial',14))
        self.save_all_stats_button.pack(side=tk.RIGHT,fill=tk.X,padx=5)

        self.save_stats_graph_button = tk.Button(self.stats_save_frame, text="Save", command=self.save_stats,font=('Arial',14))
        self.save_stats_graph_button.pack(side=tk.RIGHT,fill=tk.X,padx=5)


    #Function to update active stats graph
    def update_stats(self,selected_graph):
        # Remove the current canvas widget
        self.stats_canvas_widget.pack_forget()
        
        # Update the canvas with the selected figure
        self.stats_canvas = FigureCanvasTkAgg(self.Figures[selected_graph], master=self.stats_canvas_frame)
        self.stats_canvas_widget = self.stats_canvas.get_tk_widget()
        self.stats_canvas_widget.pack(fill=tk.X, expand=True)
    

    #Function to close stats window
    def cancel_stats(self):
        #Closes stats window when cancel is pressed
        self.stats_window.destroy()


    #Function to open save window for stats
    def save_stats(self):
        #Create a new window
        self.save_window = tk.Toplevel(self.root)
        self.save_window.title("Save as")

        self.save_window.attributes('-topmost',True)

        self.directory_frame = tk.Frame(self.save_window)
        self.directory_frame.pack(side=tk.TOP,fill=tk.X,pady=10)

        self.directory_label = tk.Label(self.directory_frame, text="Directory:", font=('Arial',14))
        self.directory_label.pack(side=tk.LEFT,fill=tk.X,padx=5)

        self.directory_entry = tk.Entry(self.directory_frame,font=('Arial',14))
        self.directory_entry.pack(side=tk.LEFT,fill=tk.X,padx=10)

        #Checks for preexisting directory
        if self.directory:
            self.directory_entry.delete(0,tk.END)
            self.directory_entry.insert(0,self.directory)

        self.directory_button = tk.Button(self.directory_frame, text="Browse", command=self.get_directory, font=('Arial',14))
        self.directory_button.pack(side=tk.LEFT,fill=tk.X,padx=5)

        self.filename_frame = tk.Frame(self.save_window)
        self.filename_frame.pack(side=tk.TOP,fill=tk.X,pady=10)

        self.filename_label = tk.Label(self.filename_frame, text="Filename:", font=('Arial',14))
        self.filename_label.pack(side=tk.LEFT,fill=tk.X,padx=5)

        #Fills filename entry with automatically generated filename
        self.filename_entry = tk.Entry(self.filename_frame,font=('Arial',14))
        self.filename_entry.pack(side=tk.LEFT,fill=tk.X,padx=5)
        self.filename_entry.insert(0,f"{self.selected_graph.get()} stats")

        self.save_cancel_frame = tk.Frame(self.save_window)
        self.save_cancel_frame.pack(side=tk.BOTTOM,fill=tk.X,pady=10)

        self.cancel_button = tk.Button(self.save_cancel_frame, text="Cancel", command=self.cancel, font=('Arial',14))
        self.cancel_button.pack(side=tk.RIGHT,fill=tk.X,padx=5)

        self.save_graph_button = tk.Button(self.save_cancel_frame, text="Save", command=self.save_stats_graph, font=('Arial',14))
        self.save_graph_button.pack(side=tk.RIGHT,fill=tk.X,pady=10)


    #Function for saving stats graphs
    def save_stats_graph(self):
        #Getting filepath
        self.directory = self.directory_entry.get()

        #Checks if filepath is valid
        folder_path=False
        if os.path.exists(self.directory):
            folder_path = True
        
        if folder_path==True:
            self.filename = self.filename_entry.get()
            filepath = os.path.join(self.directory,f"{self.filename}.png")

            #While loop to prevent files with the same name being saved
            i=1
            while os.path.exists(filepath):
                filename=f"{self.filename}({i})"
                filepath = os.path.join(self.directory,f"{filename}.png")
                i+=1
            
            #Cropping graph before saving
            fig = self.Figures[self.selected_graph.get()]
            fig.set_size_inches(16,7)
            fig.tight_layout()
            fig.savefig(filepath)
            tk.messagebox.showinfo(title="Saved", message="Graph saved successfully")
            self.save_window.destroy()

            self.stats_window.focus_force()
        
        else:
            tk.messagebox.showerror(title="Error", message="Invalid directory")


    #Function for saving all graphs
    def save_all_graphs(self):
        #Opening window to search for file directory
        self.directory = filedialog.askdirectory()

        #Checks if filepath is valid
        folder_path=False
        if os.path.exists(self.directory):
            folder_path = True
        
        #If filepath is valid saves all graphs
        if folder_path==True:
            for name,graph in self.Figures.items():
                self.filename = name
                filepath = os.path.join(self.directory,f"{self.filename} stats.png")

                #While loop to prevent files with the same name being saved
                i=1
                while os.path.exists(filepath):
                    filename=f"{self.filename}({i})"
                    filepath = os.path.join(self.directory,f"{filename}.png")
                    i+=1

                #Cropping each graph before saving
                graph.set_size_inches(16,7)
                graph.tight_layout()
                graph.savefig(filepath)
            tk.messagebox.showinfo(title="Saved", message="Graphs saved successfully")

            self.stats_window.focus_force()
        
        else:
            tk.messagebox.showerror(title="Error", message="Invalid directory")
    

    #Function to close window and exit program
    def on_close(self):
        # This function is called when the user closes the window with 'x' or 'close' button
        self.root.quit()  # Quit the Tkinter main loop
        self.root.destroy()  # Destroy the Tkinter window


root1 = tk.Tk()
app = LivePlotApp(root1, All_Data, Legend_info)
root1.mainloop()
