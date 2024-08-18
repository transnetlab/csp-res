import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os


def plot_box_heatmap(test_data, variations, network, fig_size=(20, 10), fs=12, ls=18, xlim=(4, 20), ar=0.05):
    # box plot for GTI variations
    # plot a weekly grid plot for the given data
    # create a copy of the test dataset
    df = pd.DataFrame(test_data)
    # create a box plot
    plt.figure(figsize=fig_size)
    heatmap = sns.boxplot(x='Hour', y=variations, data=df, color='orange')
    plt.xticks(fontsize=fs+2)
    plt.yticks(fontsize=fs+2)
    # x-axis label
    plt.xlabel('Hour', fontsize=ls)
    # y-axis label
    plt.ylabel(ylabel=variations, fontsize=ls)
    # plt.title('Box plot of GTI value at every hour')
    # use xlim to set the x-axis limit
    plt.xlim(xlim[0], xlim[1])
    sequence = [str(i) for i in range(xlim[0], xlim[1], 2)]
    plt.xticks(range(xlim[0], xlim[1], 2), sequence)

    # save the figure as pdf
    if variations == 'GTI (W/m2)':
        plt.savefig(f'./{network}/visualization/box_plot_{network}.pdf', bbox_inches='tight')
    else:
        plt.savefig(f'./{network}/visualization/box_plot_grid_plot_{network}_temperature.pdf', bbox_inches='tight')
    plt.show()

    ##################################################################################################
    # # # # test_data introduce new column 'day' and assign day from 1 to 365 considering hours from 1 to 24
    # test_data['day'] = np.repeat(range(1, 366), 24)
    # # find the week for each day
    # test_data['week'] = test_data['day'] // 7
    # # # find the average of GHI value for each week
    # test_data_grouped = test_data.groupby(['week', 'Hour']).mean().reset_index()
    ##################################################################################################
    # grid plot for GTI variations for each scenario
    # Create a pivot table with mean aggregation
    pivot_df = test_data.pivot_table(index='Scenario', columns='Hour', values=variations, aggfunc='mean')
    # reverse the index as on yaxis the scenario should be in 1-52 order not 52-1
    pivot_df = pivot_df.iloc[::-1]
    # Create a heatmap plot
    plt.figure(figsize=fig_size)
    # use yellow and red color for heatmap
    heatmap = sns.heatmap(pivot_df, cmap='YlOrRd')
    # plt.title('Weekly grid plot of GHI value at every hour')
    # increase x and y ticks font size
    plt.xticks(fontsize=fs)
    plt.yticks(fontsize=fs)
    # x-axis label
    plt.xlabel('Hour', fontsize=ls)
    # y-axis label
    plt.ylabel('Scenario', fontsize=ls)
    # use xlim to set the x-axis limit
    plt.xlim(xlim[0], xlim[1])
    sequence = [str(i) for i in range(xlim[0], xlim[1], 2)]
    plt.xticks(range(xlim[0], xlim[1], 2), sequence)
    # add label to cbars
    cbar = heatmap.collections[0].colorbar
    cbar.set_label(variations, fontsize=ls)
    # Adjust the width of the color bar
    cbar.ax.set_aspect(ar)
    # Set the fontsize of the color bar ticks
    cbar.ax.tick_params(labelsize=fs)
    # add values on y-axis
    plt.yticks(range(0, len(pivot_df.index), 3), pivot_df.index[::3])
    # save the plot as pdf with tight layout
    if variations == 'GTI (W/m2)':
        plt.savefig(f'./{network}/visualization/weekly_grid_plot_{network}.pdf', bbox_inches='tight')
    else:
        plt.savefig(f'./{network}/visualization/weekly_grid_plot_{network}_temperature.pdf', bbox_inches='tight')
    plt.show()


###################################################################################################################

network_name = 'Surat'
file_name = f'./{network_name}/52_scenario/solar_data/'
# find the file name in file_name directory
files = os.listdir(file_name)
file_name = file_name + files[10]
data = pd.read_csv(file_name)
# change column name Mean_Temperature to Temperature (C)
data.rename(columns={'Mean_Temperature': 'Temperature (°C)',
                     'Plane of Array Irradiance (W/m2)': 'GTI (W/m2)'}, inplace=True)

print('Maximum Temperature:', data['Temperature (°C)'].max())
print('Minimum Temperature:', data['Temperature (°C)'].min())

temp = 0
# temp == 1, plot for variations in GTI, else plot for variations in Temperature
if temp == 1:
    type_of_graph = 'GTI (W/m2)'
    aspect_ratio = 0.05
    figure_size = (20, 10)
    x_limit = (4, 20)
    font_size = 20
    label_size = 24
else:
    type_of_graph = 'Temperature (°C)'
    aspect_ratio = 2
    figure_size = (20, 10)
    x_limit = (4, 20)
    font_size = 20
    label_size = 24

plot_box_heatmap(data, type_of_graph, network_name, figure_size, font_size, label_size, xlim=x_limit, ar=aspect_ratio)
