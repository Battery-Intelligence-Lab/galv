# Using the Galvanalyser Web App

## Logging in

If you are not already logged in you will be presented with the login page. Enter your username in the first text box and your password in the second; these are the same as your database username and password. Optionally check the checkbox to remember your login details and then click the LOGIN button. If you successfully logged in then you will be presented with the data plotting tab.

## Logging out

Currently there isn't a UI element for logging out, however you may append `/logout` to the end of the URL in your browsers address bar to logout of the system.

## Finding Datasets and Data Series to Plot

Selecting data to plot is done in a sequence of steps
1. Change to the "Select Dataset" tab by clicking on it if it is not already active.
2. Populate the list of Datasets by pressing the GET DATASETS button. Optionally filter this list using the input fields above the button - see the **Filtering Datasets** section for details.
3. Select a Dataset from the list of search results in the Dataset list by checking the radio button in the left most column of the results. This will cause the data ranges table to be populated with the data ranges for the selected dataset.
4. Select which data ranges for which data columns you wish to plot using the checkboxes in the left most column of the data ranges table. Optionally filter the data ranges table using the input fields above it - see the **Data Ranges** section below for more details on data ranges and **Filtering Data Ranges** for filtering them.
5. Click the PLOT DATA RANGE button to add the selected data ranges to the items to be plotted.

### Filtering Datasets

The list of datasets may be filtered based on several different types of criteria and these may all be combined.

The first method of filtering datasets is to filter by the dataset name. To do this enter a search term in the left most text box labelled "Name Like" in the Dataset Filters section. This box supports SQL LIKE wildcards, this means you can use the `%` character to represent any number of any character and the `_` character to represent any single character. The search pattern needs to match the entire name of the dataset, thus if you wanted to search for a dataset called "example" you could enter `exam%` to find it; entering only `exam` would not work as that would search for a dataset whose name exactly matched "exam". Leaving this blank will mean the results are not filtered by name.

The second method of filtering datasets is to filter by the date of the dataset. The Date From box will allow you to specify a date and only datasets after that date will be shown. The Date To box will allow you to specify a date and only datasets from be fore that date will be shown. Both boxes may be used together to specify a range of dates and only datasets within that range will be shown. Clicking in either of those boxes will display a calendar to aid selecting dates. Alternatively you may type the date you wish in the box in the format `YYYY MM DD` - numeric year followed by a space, numeric month followed by a space and then numeric day. When a date entry box is populated you may clear it by clicking the `X` button that appears within it towards the right hand side. Leaving the Date From box blank will mean that the results are not filtered by that criteria. Similarly leaving the Date To box blank will mean that there is no end date restriction on the search results.

The Third method of filtering datasets is by sampler machine type. If you have already clicked GET DATASETS then clicking in this box will present a dropdown listing the available sampler machine types. After displaying the dropdown you may select your desired machine type by clicking the item from the list. You may select multiple machine types by clicking the blank space within the box or the down arrow within the box to display the dropdown list and selecting another item. This may be done repeatedly. Selected machine types can be removed by clicking the `x` to the left of their name. If you haven't clicked the GET DATASETS button then you will need to do so first before using this filter. Leaving this blank will disable filtering of the datasets by machine type.

You need to click the GET DATASETS button to update the results 

### Data Ranges

The time series data within a dataset is stored according to sample number. When a battery cycler is performing a test it collects a series of readings of values simultaneously, these are typically voltage and current readings but other readings can be sampled. Other values can be stored at the same time such as the current the cycler is driving, the current timestamp and the current stage of the test cycle. During the test it repeatedly takes those samples. These samples are all given a unique integer sample number. The first set of samples collected are given sample number 1, the second set collected are given sample number 2 and so on. A data range is a pair of sample numbers that define a range of samples. It may be thought of as a way to specify a period of time within a test, except that it is specified using the sample numbers rather than the time the sample was collected. A data range has a name associated with it.

The Galvanalyser system automatically creates several types of data range for a dataset when the data for that dataset is uploaded by a harvester. The simplest automatically created data range is the "all" range which includes all the samples within the dataset - from sample 1 to the last sample in the dataset. Some cycler file formats include columns indicating test stages and these will automatically be converted into data ranges. The Galvanalyser system will also attempt to automatically determine charge and discharge cycles based on the changing values of the measured current and will generate labelled cycles from that information.

Users may also create their own data ranges to label regions of interest within a dataset.

### Filtering Data Ranges

The table of data ranges may contain a great many entries as a dataset may contain many data ranges and the data range table contains one row for each column type in the dataset for each label. The rows for each dataset column for a particular label will appear next to each other in the table. When adding ranges to plot first locate the labelled range you wish to plot in the table and then check the checkbox for the row with the desired dataset column named in the "column" column in the table.

There are several options for filtering the displayed data ranges. These may be used along or in conjunction with each other.

The first method of filtering the displayed ranges is to enter a search pattern in the Name Like text box. Like the Name Like box described in the **Filtering Datasets** section this uses SQL LIKE wildcards which are described in that section. An example usage would be to search for `cycle%` to find all the data ranges whose names begin with "cycle". Leaving this blank will mean the results are not filtered by name. After typing a search term, the results will update when you press return/enter or click outside of the text box.

The second method of filtering allows you to only display rows of chosen time series columns. To do this use the box labelled Dataset Column. You interact with this box the same way as you interact with the sampler machine type filter box described in the **Filtering Datasets** section. The data range table will only display rows for the dataset column types listed within this box. Leaving this box blank will result in all column types being displayed. The results will update each time an item is added or removed.

The third method filters the rows based on whether or not the data range was created by the system or a user. There are two checkboxes labelled "Include" with sublabels "System Made" and "User Made". By default both are checked to include both automatically generated (System Made) data ranges and data ranges created by users (User Made). Unchecking the System Made checkbox will exclude the automatically generated data ranges from the results. Unchecking the User Made checkbox will exclude user created data ranges from the results.

## Plotting Data

The Plotting tab consists of two main sections. The biggest is the plotting area to the left which is used for displaying the plots of the data ranges selected for plotting. The second section is the right hand side side bar. The right ride bar has two tabs, the first it the Legend tab and the second is the Export tab. The Legend tab contains the interactive graph legend. The Export tab contains options for saving the current plot as an image file to disk.

Hovering the mouse over the plot will reveal a selection of tools in the top right. These tools allow the user to perform various actions including autoscaling the plot to the data, zooming in on sections of data in either or both axes or panning the view around the data. Both the plotting are and the tools have hover over text to help the user.

### The Interactive Legend

The Legend tab of the right sidebar contains the interactive plot legend. When data ranges have been selected for plotting it contains a list of each data range that is to be plotted, each contained within a box with the same colour as the line used to plot that range on the chart. The box includes the name of the time series column, the name of the data range, the samples numbers that describe that range and the offset value that will be described later. The top of the Legend tab has a button labelled SHOW RANGE EDITOR which will be discussed in the **Creating User Data Ranges** section; a button labelled SET REFERENCE VALUE TO VIEW; a sideways facing arrow shaped button that is used to switch the legend in and out of editing mode; and a numeric display/entry box labelled Reference Value. The reference value is a number representing a sample number that is used for aligning data ranges in the plot. The SET REFERENCE VALUE TO VIEW button sets the refernce value to the sample number at the left most end of the currently visible sample range.

#### Legend Editing Mode

When the left pointing arrow button at the top of the interactive legend is clicked the legend switches to editing mode and the button changes to a right facing arrow. In the editing mode each of the enteries in the legend contain a selection of buttons. Each of these buttons has hover over text to indicate what the button does as well as an icon relevant to the buttons function. The buttons have the following functions:
* Set Ref To Start - Sets the reference value to the first sample in this data range.
* Set Ref To End - Sets the reference value to the last sample in this data range.
* Align Start To Ref - Sets the Offset value for the data range such that when the data range is plotted the first sample in the range is aligned to the reference value.
* Align End To Ref - Sets the Offset value for the data range such that when the data range is plotted the last sample in the range is aligned to the reference value.
* Remove Range From Plot - This button removes the data range from the legend and the plot. The data range can be added once again by adding it from the Select Dataset tab.

If the user has the data ranges for several cycles plotted and wishes to align the cycles then the user may do the following. Click the Set Ref To Start button in the box for the cycle they wish to align the other cycles to. Then in each of the other cycles click the Align Start To Ref button. Alternativly the user could click the Align Start To Ref in all the cycles to align all the cycles to the current reference value.

#### Creating User Data Ranges

Clicking the SHOW RANGE EDITOR reveals the controls for creating and modifying user created ranges. To create a user defined range first select the dataset you wish to create the range for from the dropdown labelled "Range for Dataset". Next define the sample range using the numeric entry boxes labelled From and To, alternativly you can click the USE CURRENT CHART RANGE button to set the From and To boxes to the minimum and maximum sample numbers currently displayed on the chart. The numbers will then appear next to the labels "Closest lower sample number" and "Closest higher sample number" indicating the closest sample numbers found within the selected dataset to those requested in the From and To boxes. The sample numbers displayed in the labels are the ones that will be used for the sample range. Next Enter a name for the sample range in the Range Name text box. Clicking the SAVE CUSTOM RANGE button will create a new data range if the chosen name is not already used for that dataset. If the name has already been used then an error will be displayed. If a range with the same name already exists clicking the UPDATE CUSTOM RANGE button will update that range's from and to values to the currently selected values which is how you modify an existing range.

### Exporting Images of the Current Plot