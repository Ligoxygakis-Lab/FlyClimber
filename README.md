<h1>FlyTracker</h1>

<h2>Overview</h2>

`FlyTracker` is a python based particle detection script to streamline the  [rapid iterative negative geotaxis (RING) assay](https://www.sciencedirect.com/science/article/pii/S0531556505000343?casa_token=E8QE2aYrEwoAAAAA:MNa-Wc8BeOXMvmlNuj-b4tH2cMQFuI1ZfUt8qZm0IRY8Qe88xOvw0em07UpwkNqh0QBIPbNZikY) used in the assessment of a *Drosophila's* climbing performance. It is capable of live video feed analysis to identify the position of flies within each frame using colour filtration and quantifying they're position in relation to the vial the flies are climbing in.

Raw data from the video analysis is output to csv files that can be efficiently analysed by the `FlyTracker Graphing` program. This GUI allows for changing of smoothing parameters before applying [Statistical Parametric Mapping (SPM)](https://www.tandfonline.com/doi/abs/10.1080/10255842.2010.527837) to identify specific time point ranges with statistically significant differences in behaviour.

<h2>Requirements</h2>

Python Modules:

    - Numpy         [1.26.3]
    - OpenCV        [4.9.0.80]
    - Matplotlib    [3.8.2]
    - Statsmodels   [0.14.1]
    - spm1d         [0.4.24]
    - Scipy         [1.12.0]

<h2>Installation</h2>

This program was developed and run using a virtual environment in Visual Studio Code (VS Code). The download for VS Code can be found [here](https://code.visualstudio.com/download). After downloading VS Code, install the python extension.

Create a folder to store the programs and output csv files. In VS Code go to `File>Open Folder...` and select the folder just created. Instructions for creating and operating within a virtual environment can be found [here](https://code.visualstudio.com/docs/python/environments). Before creating a virtual environment, if operating a windows device, make sure that the latest version of [python](https://www.python.org/downloads/) is downloaded. Copy both the `FlyTracker` and `Flytracker Analysis` programs into the folder for use.

Once the virtual environment is active, the required python modules can be installed. To do this run the following commands in the **command prompt terminal**:

    pip install numpy
    pip install opencv-python
    pip install statsmodels
    pip install spm1d
    pip install scipy

<h2>Using the Programs</h2>

<h3>Experimental Setup</h3>

Because of the colour filtration employed for detection, the assays should be carried out with the flies inside of a plain clear vial with a white background. A small line should be drawn on the bottom and the top of the vial for the program to identify the confines of the vial in the frame. `FlyTracker` is set up to detect a dark blue line but this can be changed by changing the colour values in the code (variable names: `low_blue` and `high_blue`).

Due to the live video tracking of `FlyTracker`, a physical connection is required between the camera and laptop running the program. A phone camera is sufficient and for macbook/iphone pairings, a USB charging cable connecting the phone and macbook is sufficient for a video connection. Other pairings such as windows/android may require additional software such as [Droidcam](https://www.dev47apps.com/droidcam/windows/) to allow the laptop to access the phone camera.

<h3>Performing the Assay</h3>

When `FlyTracker` is run, a window will ask for identifying information about the flies being tested. This information is used to create the filename and search for data using the analysis program. **If the filename created is identical to an existing file, that existing file will be replaced and lost**. The date the assay is carried out is included in the filename, so identical information (for example with biological replicate experiments) can be used on different days.

Input boxes can be left blank except for `time step` and `Genetic Background` both marked as essential with an asterisk. `Time step` dictates how often the program collects data. The input can be **any number 0.1 or higher**. `Genetic Background` dictates the colour ranges that are filtered by the program to detect flies. The input can be **YW or W1118**.

Pressing the `Open Camera` button will bring up a live feed of the phone camera and start tracking flies. The feed will display the identifying information along with two green horizontal lines. The camera should be positioned throughout the assay such that the lower blue line dictating the bottom of the vial is below the lower green line and the upper blue line dictating the top of the vial is above the higher green line.

The program should start circling the flies that it finds with either red or blue circles. A red circle indicates that it has found a single fly while a blue circle indicates that it has found multiple flies too close together for separate circles. The program will approximate how many flies are within this blue circle and record that height for each of them.

Pressing the `s` key starts a 5-second countdown. A force to knock the flies down should be applied at the end of the countdown when the 30 seconds for the assay will start. Data is collected from 3 seconds to 30 seconds at each time step. After 30 seconds the video feed will close and data collected is saved to a csv file.

<h3>Analysing the Data</h3>

Running the `FlyTracker Analysis` program will bring up a window with search fields to fill in. Using the search terms provided, the program will filter the csv files that fit those search terms and collate all the data together. Additional data sets can be added or removed using the `Add Group` and `Remove Group` buttons. Pressing the `Create Graph` button brings up an interface with a graph showing the mean height at each time point with standard error bars and several features to edit the graph:

  - **Colour editing** - Each line has its own text box to input a colour. Both words and hex code inputs (in the syntax #000000) are accepted. The `Apply Colours` button applies any changes to the colours of the lines.
  - **Edit Legend** - The `Edit legend` button can be used to change the automatically generated legend labels.
  - **Edit x-axis** - The `Edit x-axis` button brings up an input window to change the step of the x-axis.
  - **Alpha Significance** - This is the value for the overall significance threshold for the statistical testing. Where more than 2 data sets are input by the user (meaning more than 1 stats test) a multiple comparisons correction is applied to the significance threshold for each stats test.
  - **Saving the graph** - The `Save as` button is used to save the graph as a png file.

The data is smoothed using a Savitsky Golay filter. The degree of smoothing can be controlled with the sliding bars for window length and polynomial order. **Care should be taken to not oversmooth the data**. The `Get Stats` button performs SPM using the [spm1d python package](https://pubmed.ncbi.nlm.nih.gov/21756121/) on the data and brings up a window with graphs for the stats. The SPM graphs map a t-value against time and highlight which time points pass the threshold for significance. These graphs can also be saved as png files.

<h2>Troubleshooting</h2>

  - **The program isn't seeing the phone camera** - Make sure that the connection between the phone and laptop is working. If this is the case then in the `FlyTracker` program go to line 272 which reads `cap = cv.VideoCapture(1)`. The 1 refers to the second camera (laptop first, phone second) but different systems order cameras differently. For macbook/iphone pairings, the phone camera is 0. 
  - **Inability to track flies** - The colour ranges were optimised for our lab setup. With different lighting and different cameras, the colour ranges may not be optimal for fly detection. The colour values are stored under `YW_low_fly`, `YW_high_fly`, `W1118_low_fly`, `W1118_high_fly`. The colours are BGR (Blue, Green, Red) values.
  - **Program crashes when trying to compute stats** - SPM creates a matrix of values for the control and test data. In order for SPM to work, the datasets have to have the same number of time points.
  - **Analysis program can't find correct csv files** - The analysis program when searching for csv files looks in the folder that the analysis program is run from. Any csv files not in this folder cannot be seen by the analysis program. This can be used to exclude certain files from the search by storing them in a separate file while running the analysis program.

If there are any issues, email petros.ligoxygakis@bioch.ox.ac.uk
