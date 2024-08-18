from datetime import date
import pickle
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch


# function to assign bus number to trip
def bus_number_assign(bus_trip_assign, trip_df):
    """
      assigning bus number to given assignment
      Parameters:
      ____________
      bus_trip_assign: list of list bus trip assignment
      trips_df: DataFrame trip schedule

      returns:
      total number of bus_assigned
      """

    # assigning bus_number to trip as per bus assignment
    bus_number = 1
    for list_trip in bus_trip_assign:
        for trip in list_trip[1:-1]:
            index2 = trip_df[trip_df.Trip_ID == trip].index.values[0]
            trip_df.loc[index2, 'bus_number'] = bus_number
        bus_number += 1
    return bus_number - 1

def duration_bus_spent(data_charging, trip_data, num_bus):
    """
    creates a dataframe which consists of % duration spent for trip, charging, idling for each bus
    Parameters:
    ____________
    data_charging: DataFrame charging schedule
    trip_data: DataFrame trip schedule
    num_bus: int number of buses

    return
    duration_df: DataFrame
    bus_ids: list of 10 bus_ids with less idle time and also having charging activities
    """
    # % duration of trip, charging and idling
    charging_duration = data_charging[["bus_number", "duration_in_min"]].groupby(['bus_number']).sum()
    trip_duration = trip_data[["bus_number", "duration_in_min"]].groupby(['bus_number']).sum()
    trip_duration.reset_index(inplace=True)
    charging_duration.reset_index(inplace=True)
    duration_df = pd.DataFrame()
    bus_ids = sorted(list(trip_data.bus_number.unique()))
    for i in range(len(bus_ids)):
        duration_df.loc[i, 'bus_number'] = bus_ids[i]
        bus_start_time = trip_data[trip_data.bus_number == bus_ids[i]].Start_Time.head(1).values[0]
        bus_end_time = trip_data[trip_data.bus_number == bus_ids[i]].End_Time.tail(1).values[0]
        duration_df.loc[i, "start_time"] = bus_start_time
        duration_df.loc[i, "end_time"] = bus_end_time
        duration_df.loc[i, "total_time"] = (bus_end_time - bus_start_time) / np.timedelta64(1, 'm')

        try:
            duration_df.loc[i, 'trip_duration'] = trip_duration[trip_duration.bus_number == bus_ids[i]].duration_in_min.values[0]
            duration_df.loc[i, 'charge_duration'] = charging_duration[charging_duration.bus_number == bus_ids[i]].duration_in_min.values[0]
        except IndexError:
            duration_df.loc[i, 'charge_duration'] = 0

    duration_df['idle_time'] = duration_df['total_time'] - duration_df['trip_duration'] - duration_df['charge_duration']
    # duration_df['per_trip_time'] = (100 * duration_df['trip_duration']) / duration_df['total_time']
    # duration_df['per_charge_time'] = (100 * duration_df['charge_duration']) / duration_df['total_time']
    # duration_df['per_idle_time'] = (100 * duration_df['idle_time']) / duration_df['total_time']
    duration_df.sort_values(['idle_time'], ascending=True, inplace=True)
    # to save the DataFrame in csv format
    # duration_df.to_csv('trip_charging_idle_duration.csv')
    # bus_ids = list(duration_df[duration_df.charge_duration > 0].bus_number.head(10))
    bus_ids_df = duration_df.sort_values(by="charge_duration", ascending=False)
    bus_ids = (bus_ids_df.bus_number.unique())
    count = 1
    for bus in bus_ids:
        for index, row in data_charging[data_charging.bus_number == bus].iterrows():
            data_charging.loc[index, 'update_number'] = count

        for index1, row1 in trip_data[trip_data.bus_number == bus].iterrows():
            trip_data.loc[index1, 'update_number'] = count

        count += 1
    # data_charging.to_csv('char.csv')
    # trip_data.to_csv('trip.csv')
    return duration_df, bus_ids


# read trip_times file in arlington network
network = 'Canberra_3.91k'
folder_path = f'E:/PycharmProjects/CSP-Benders'
number_of_scenario = 52
# open the file dict_network_name.pkl
with open('./dict_network_name.pkl', 'rb') as f:
    dict_network_short_name = pickle.load(f)
scenarios = [4, 10, 26, 33, 41, 50]
# scenarios = [32]
for scenario in scenarios:

    trip_schedule = pd.read_csv(f'{folder_path}/{network}/trip_times.csv')
    # open bus_trip_assignment.pkl file in arlington network
    bus_trip_assignment = pd.read_pickle(
        f'{folder_path}/{network}/{number_of_scenario}_scenario/bus_rotations/scenario_{scenario}_bus_rotations_cs.pkl')

    # load charging schedule
    charging_grid = pd.read_csv(
        f'{folder_path}/{network}/{number_of_scenario}_scenario/csp_{dict_network_short_name[network]}'
        f'_{scenario}_scenario.csv')

    # load charging solar schedule
    charging_solar = pd.read_csv(
        f'{folder_path}/{network}/{number_of_scenario}_scenario/csp_solar_{dict_network_short_name[network]}_'
        f'{scenario}_scenario.csv')

    # analysis on scenario 1
    charging_schedule = charging_grid[charging_grid.scenario == scenario]
    charging_solar_schedule = charging_solar[charging_solar.scenario == scenario]

    # # only consider the charging schedule of bus 110
    # charging_schedule = charging_grid[charging_grid.bus_number == 20]
    # charging_solar_schedule = charging_solar[charging_solar.bus_number == 20]

    for index, row in trip_schedule.iterrows():
        if row.Start_Day == 1:
            trip_schedule.loc[index, "Start_Time"] = str(int(row.Start_Time[:2]) - 24) + row.Start_Time[2:]
        if row.End_Day == 1:
            trip_schedule.loc[index, "End_Time"] = str(int(row.End_Time[:2]) - 24) + row.End_Time[2:]

    # date of today
    day = date.today()
    # next_day
    next_day = day.replace(day=day.day + 1)
    next_day_day = next_day.replace(day=next_day.day + 1)
    # convert date to string
    day_str = day.strftime("%d-%m-%Y")
    next_day_str = next_day.strftime("%d-%m-%Y")
    next_day_day_str = next_day_day.strftime("%d-%m-%Y")

    trip_schedule.Start_Time = np.where(trip_schedule.Start_Day == 0,
                                        next_day_str + " " + trip_schedule.Start_Time,
                                        next_day_day_str + " " + trip_schedule.Start_Time)

    trip_schedule.End_Time = np.where(trip_schedule.End_Day == 0,
                                      next_day_str + " " + trip_schedule.End_Time,
                                      next_day_day_str + " " + trip_schedule.End_Time)

    trip_schedule["Start_Time"] = pd.to_datetime(trip_schedule["Start_Time"], format='%d-%m-%Y %H:%M:%S').copy()

    trip_schedule["End_Time"] = pd.to_datetime(trip_schedule["End_Time"], format='%d-%m-%Y %H:%M:%S').copy()

    trip_schedule["duration_in_min"] = (trip_schedule["End_Time"] - trip_schedule["Start_Time"]).dt.total_seconds() / 60

    trip_schedule["bus_number"] = 0

    no_bus = bus_number_assign(bus_trip_assignment, trip_schedule)

    # add string to charging_start_time and charging_end_time based on start_day and end_day,
    # if start_day is 1 add day_str to charging_start_time else, elif start_day is 2 add next_day_str to
    # charging_start_time, else add next_day_day_str to charging_start_time
    charging_schedule.charging_start_time = np.where(charging_schedule.start_day == 1,
                                                    day_str + " " + charging_schedule.charging_start_time,
                                                    np.where(charging_schedule.start_day == 2,
                                                             next_day_str + " " + charging_schedule.charging_start_time,
                                                             next_day_day_str + " " + charging_schedule.charging_start_time))
    # similar to charging_end_time
    charging_schedule.charging_end_time = np.where(charging_schedule.end_day == 1,
                                                  day_str + " " + charging_schedule.charging_end_time,
                                                  np.where(charging_schedule.end_day == 2,
                                                           next_day_str + " " + charging_schedule.charging_end_time,
                                                           next_day_day_str + " " + charging_schedule.charging_end_time))

    # convert charging_start_time and charging_end_time to datetime
    charging_schedule["charging_start_time"] = pd.to_datetime(charging_schedule["charging_start_time"], format='%d-%m-%Y %H:%M:%S').copy()
    charging_schedule["charging_end_time"] = pd.to_datetime(charging_schedule["charging_end_time"], format='%d-%m-%Y %H:%M:%S').copy()
    charging_schedule["duration_in_min"] = (charging_schedule["charging_end_time"] - charging_schedule["charging_start_time"]).dt.total_seconds() / 60

    # implement this to the charging solar schedule
    charging_solar_schedule.charging_start_time = np.where(charging_solar_schedule.start_day == 1,
                                                           day_str + " " + charging_solar_schedule.charging_start_time,
                                                           np.where(charging_solar_schedule.start_day == 2,
                                                                    next_day_str + " " + charging_solar_schedule.charging_start_time,
                                                                    next_day_day_str + " " + charging_solar_schedule.charging_start_time))

    charging_solar_schedule.charging_end_time = np.where(charging_solar_schedule.end_day == 1,
                                                         day_str + " " + charging_solar_schedule.charging_end_time,
                                                         np.where(charging_solar_schedule.end_day == 2,
                                                                  next_day_str + " " + charging_solar_schedule.charging_end_time,
                                                                  next_day_day_str + " " + charging_solar_schedule.charging_end_time))

    charging_solar_schedule["charging_start_time"] = pd.to_datetime(charging_solar_schedule["charging_start_time"], format='%d-%m-%Y %H:%M:%S').copy()
    charging_solar_schedule["charging_end_time"] = pd.to_datetime(charging_solar_schedule["charging_end_time"], format='%d-%m-%Y %H:%M:%S').copy()
    charging_solar_schedule["duration_in_min"] = (charging_solar_schedule["charging_end_time"] - charging_solar_schedule["charging_start_time"]).dt.total_seconds() / 60

    # concatenate charging_schedule and charging_solar_schedule
    charging_schedule_new = pd.concat([charging_schedule, charging_solar_schedule], ignore_index=True)

    duration_df, bus_ids = duration_bus_spent(charging_schedule_new, trip_schedule, no_bus)

    ############# START OF GANTT CHART PLOTTING ####################
    # start time of charging schedule
    start_time_charging = pd.to_datetime(charging_schedule_new.charging_start_time.min().strftime("%d-%m-%y %H"), format='%d-%m-%y %H')
    end_time_str = charging_schedule_new["charging_end_time"].max().strftime("%d-%m-%y ")
    hour = int(charging_schedule_new["charging_end_time"].max().strftime("%H")) + 1
    if hour == 24:
        hour = 1
        end_time_str = str(next_day_day.day) + end_time_str[2:]
    elif hour == 23:
        hour = 0
        end_time_str = str(next_day_day.day) + end_time_str[2:]

    end_time_charging = pd.to_datetime(end_time_str + f"{hour:02d}", format='%d-%m-%y %H')

    # start time of trip schedule
    start_time_trip = pd.to_datetime(trip_schedule.Start_Time.min().strftime("%d-%m-%y %H"), format='%d-%m-%y %H')

    # end time of trip schedule
    end_time_str = trip_schedule["End_Time"].max().strftime("%d-%m-%y ")
    hour = int(trip_schedule["End_Time"].max().strftime("%H")) + 1
    if hour == 24:
        hour = 1
        end_time_str = str(next_day_day.day) + end_time_str[2:]
    elif hour == 23:
        hour = 0
        end_time_str = str(next_day_day.day) + end_time_str[2:]
    end_time_trip = pd.to_datetime(end_time_str + f"{hour:02d}", format='%d-%m-%y %H')

    start_time = min(start_time_trip, start_time_charging)
    end_time = max(end_time_trip, end_time_charging)
    total_time = (end_time - start_time).total_seconds() / 60

    # time in minutes at which charging started from start time
    trip_schedule["initial_time"] = (trip_schedule.Start_Time - start_time).dt.total_seconds() / 60
    charging_schedule_new["initial_time"] = (charging_schedule_new.charging_start_time - start_time).dt.total_seconds() / 60

    # remove the bus number with duration less than 0 in charging_schedule_new
    charging_schedule_new = charging_schedule_new[charging_schedule_new.duration_in_min > 0]

    # figure size
    fig, ax = plt.subplots(1, figsize=(60, 40))

    # bars for trip schedule
    ax.barh(trip_schedule['bus_number'] * 3, trip_schedule.duration_in_min, left=trip_schedule.initial_time,
             color='#87CEEB', label='Trip', edgecolor='#4C87B9', height=1.2)

    # bars for charging schedule with plain color
    # for grid
    charging_schedule_new_grid = charging_schedule_new[charging_schedule_new.grid_or_solar == 'grid']
    ax.barh(charging_schedule_new_grid['bus_number'] * 3, charging_schedule_new_grid.duration_in_min,
            left=charging_schedule_new_grid.initial_time, color='red', label='Grid Energy', edgecolor='red',
            height=1.2)
    # for solar
    charging_schedule_new_solar = charging_schedule_new[charging_schedule_new.grid_or_solar == 'solar']
    ax.barh(charging_schedule_new_solar['bus_number'] * 3, charging_schedule_new_solar.duration_in_min,
            left=charging_schedule_new_solar.initial_time, color='green', label='Solar Energy', edgecolor='green',
            height=1.2)


    # ticks along both axes and corresponding labels
    yticks = list(range(3, 3 * (len(trip_schedule.bus_number.unique()) + 1), 3))
    ytick_label = [f"{int(x)}" for x in sorted(list(trip_schedule.bus_number.unique()))]
    xticks = np.arange(0, total_time + 1, 60)
    ax.set_yticks(yticks[::6])
    xtick_labels = pd.date_range(start=start_time, end=end_time, periods=int(total_time) + 1).strftime("%H")
    ax.set_yticklabels(ytick_label[::6])
    ax.xaxis.set_tick_params(labelsize=50)
    ax.yaxis.set_tick_params(labelsize=50)
    ax.set_xticks(xticks)
    ax.set_xticklabels(xtick_labels[::60])
    ax.set_ylabel("Bus Number", fontsize=80)
    ax.set_xlabel("Time", fontsize=80)
    # add a rectangle from 10:00 to 22:00 and fill with grey color and alpha 0.2
    # find the rectangle start and end time from start_time and end_time
    # with next_day_str as day
    # extract date str from next_day
    # june to september weeks set for scenario check arrange from 20 to 36
    if network == 'Durham_2.1k':
        may_to_october = [17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39
            , 40, 41]
    else:
        may_to_october = []

    if scenario in may_to_october:
        rectangle_start_peak1 = pd.to_datetime(day.strftime("%d-%m-%y") + ' ' + '16', format='%d-%m-%y %H')
        rectangle_end_peak1 = pd.to_datetime(day.strftime("%d-%m-%y") + " 21", format='%d-%m-%y %H')
        start_time_peak1 = (rectangle_start_peak1 - start_time).total_seconds() / 60
        end_time_peak1 = (rectangle_end_peak1 - start_time).total_seconds() / 60
        ax.add_patch(plt.Rectangle((start_time_peak1, 0), end_time_peak1 - start_time_peak1,
                                   3 * len(trip_schedule.bus_number.unique()), fill=True, color='grey', alpha=0.3,
                                   edgecolor='grey'))
        rectangle_start_peak2 = pd.to_datetime(next_day.strftime("%d-%m-%y") + ' ' + '16', format='%d-%m-%y %H')
        rectangle_end_peak2 = pd.to_datetime(next_day.strftime("%d-%m-%y") + " 21", format='%d-%m-%y %H')
        start_time_peak2 = (rectangle_start_peak2 - start_time).total_seconds() / 60
        end_time_peak2 = (rectangle_end_peak2 - start_time).total_seconds() / 60
        ax.add_patch(plt.Rectangle((start_time_peak2, 0), end_time_peak2 - start_time_peak2,
                                   3 * len(trip_schedule.bus_number.unique()), fill=True, color='grey', alpha=0.3,
                                   edgecolor='grey'))
        rectangle_start_off_peak1 = pd.to_datetime(day.strftime("%d-%m-%y") + ' ' + '21', format='%d-%m-%y %H')
        rectangle_end_off_peak1 = pd.to_datetime(day.strftime("%d-%m-%y") + " 23", format='%d-%m-%y %H')
        rectangle_start_off_peak2 = pd.to_datetime(next_day.strftime("%d-%m-%y") + ' ' + '21', format='%d-%m-%y %H')
        rectangle_end_off_peak2 = pd.to_datetime(next_day.strftime("%d-%m-%y") + " 23", format='%d-%m-%y %H')
        rectangle_start_off_peak3 = pd.to_datetime(next_day.strftime("%d-%m-%y") + ' ' + '7', format='%d-%m-%y %H')
        rectangle_end_off_peak3 = pd.to_datetime(next_day.strftime("%d-%m-%y") + " 16", format='%d-%m-%y %H')

        start_time_off_peak1 = (rectangle_start_off_peak1 - start_time).total_seconds() / 60
        end_time_off_peak1 = (rectangle_end_off_peak1 - start_time).total_seconds() / 60
        ax.add_patch(plt.Rectangle((start_time_off_peak1, 0), end_time_off_peak1 - start_time_off_peak1,
                                   3 * len(trip_schedule.bus_number.unique()), fill=True, color='pink', alpha=0.3,
                                   edgecolor='pink'))
        start_time_off_peak2 = (rectangle_start_off_peak2 - start_time).total_seconds() / 60
        end_time_off_peak2 = (rectangle_end_off_peak2 - start_time).total_seconds() / 60
        ax.add_patch(plt.Rectangle((start_time_off_peak2, 0), end_time_off_peak2 - start_time_off_peak2,
                                   3 * len(trip_schedule.bus_number.unique()), fill=True, color='pink', alpha=0.3,
                                   edgecolor='pink'))
        start_time_off_peak3 = (rectangle_start_off_peak3 - start_time).total_seconds() / 60
        end_time_off_peak3 = (rectangle_end_off_peak3 - start_time).total_seconds() / 60
        ax.add_patch(plt.Rectangle((start_time_off_peak3, 0), end_time_off_peak3 - start_time_off_peak3,
                                   3 * len(trip_schedule.bus_number.unique()), fill=True, color='pink', alpha=0.3,
                                   edgecolor='pink'))



    else:
        # refer TOU pricing for Canberra
        if network.startswith('Canberra'):
            rectangle_start_peak = pd.to_datetime(next_day.strftime("%d-%m-%y") + ' ' + '7', format='%d-%m-%y %H')
            rectangle_end_peak = pd.to_datetime(next_day.strftime("%d-%m-%y") + " 16", format='%d-%m-%y %H')
            rectangle_start_shoulder1 = pd.to_datetime(day.strftime("%d-%m-%y") + ' ' + '16', format='%d-%m-%y %H')
            rectangle_end_off_shoulder1 = pd.to_datetime(day.strftime("%d-%m-%y") + " 22", format='%d-%m-%y %H')
            rectangle_start_shoulder2 = pd.to_datetime(next_day.strftime("%d-%m-%y") + ' ' + '16', format='%d-%m-%y %H')
            rectangle_end_off_shoulder2 = pd.to_datetime(next_day.strftime("%d-%m-%y") + " 22", format='%d-%m-%y %H')
            start_off_peak = (rectangle_start_shoulder1 - start_time).total_seconds() / 60
            end_off_peak = (rectangle_end_off_shoulder1 - start_time).total_seconds() / 60
            ax.add_patch(plt.Rectangle((start_off_peak, 0), end_off_peak - start_off_peak,
                                       3 * len(trip_schedule.bus_number.unique()), fill=True, color='pink', alpha=0.3,
                                       edgecolor='pink'))
            start_off_peak = (rectangle_start_shoulder2 - start_time).total_seconds() / 60
            end_off_peak = (rectangle_end_off_shoulder2 - start_time).total_seconds() / 60
            ax.add_patch(plt.Rectangle((start_off_peak, 0), end_off_peak - start_off_peak,
                                       3 * len(trip_schedule.bus_number.unique()), fill=True, color='pink', alpha=0.3,
                                       edgecolor='pink'))
            start_peak = (rectangle_start_peak - start_time).total_seconds() / 60
            end_peak = (rectangle_end_peak - start_time).total_seconds() / 60
            ax.add_patch(plt.Rectangle((start_peak, 0), end_peak - start_peak,
                                       3 * len(trip_schedule.bus_number.unique()), fill=True, color='grey', alpha=0.3,
                                       edgecolor='grey'))
        elif network.startswith('Durham'):
            rectangle_start_peak1 = pd.to_datetime(day.strftime("%d-%m-%y") + ' ' + '16', format='%d-%m-%y %H')
            rectangle_end_peak1 = pd.to_datetime(day.strftime("%d-%m-%y") + " 21", format='%d-%m-%y %H')
            start_time_peak1 = (rectangle_start_peak1 - start_time).total_seconds() / 60
            end_time_peak1 = (rectangle_end_peak1 - start_time).total_seconds() / 60
            ax.add_patch(plt.Rectangle((start_time_peak1, 0), end_time_peak1 - start_time_peak1,
                                       3 * len(trip_schedule.bus_number.unique()), fill=True, color='pink', alpha=0.3,
                                       edgecolor='pink'))
            rectangle_start_peak2 = pd.to_datetime(next_day.strftime("%d-%m-%y") + ' ' + '16', format='%d-%m-%y %H')
            rectangle_end_peak2 = pd.to_datetime(next_day.strftime("%d-%m-%y") + " 21", format='%d-%m-%y %H')
            start_time_peak2 = (rectangle_start_peak2 - start_time).total_seconds() / 60
            end_time_peak2 = (rectangle_end_peak2 - start_time).total_seconds() / 60
            ax.add_patch(plt.Rectangle((start_time_peak2, 0), end_time_peak2 - start_time_peak2,
                                       3 * len(trip_schedule.bus_number.unique()), fill=True, color='pink', alpha=0.3,
                                       edgecolor='pink'))
            rectangle_start_off_peak1 = pd.to_datetime(day.strftime("%d-%m-%y") + ' ' + '21', format='%d-%m-%y %H')
            rectangle_end_off_peak1 = pd.to_datetime(day.strftime("%d-%m-%y") + " 23", format='%d-%m-%y %H')
            rectangle_start_off_peak2 = pd.to_datetime(next_day.strftime("%d-%m-%y") + ' ' + '21', format='%d-%m-%y %H')
            rectangle_end_off_peak2 = pd.to_datetime(next_day.strftime("%d-%m-%y") + " 23", format='%d-%m-%y %H')
            rectangle_start_off_peak3 = pd.to_datetime(next_day.strftime("%d-%m-%y") + ' ' + '7', format='%d-%m-%y %H')
            rectangle_end_off_peak3 = pd.to_datetime(next_day.strftime("%d-%m-%y") + " 16", format='%d-%m-%y %H')

            start_time_off_peak1 = (rectangle_start_off_peak1 - start_time).total_seconds() / 60
            end_time_off_peak1 = (rectangle_end_off_peak1 - start_time).total_seconds() / 60
            ax.add_patch(plt.Rectangle((start_time_off_peak1, 0), end_time_off_peak1 - start_time_off_peak1,
                                       3 * len(trip_schedule.bus_number.unique()), fill=True, color='grey', alpha=0.3,
                                       edgecolor='grey'))
            start_time_off_peak2 = (rectangle_start_off_peak2 - start_time).total_seconds() / 60
            end_time_off_peak2 = (rectangle_end_off_peak2 - start_time).total_seconds() / 60
            ax.add_patch(plt.Rectangle((start_time_off_peak2, 0), end_time_off_peak2 - start_time_off_peak2,
                                       3 * len(trip_schedule.bus_number.unique()), fill=True, color='grey', alpha=0.3,
                                       edgecolor='grey'))
            start_time_off_peak3 = (rectangle_start_off_peak3 - start_time).total_seconds() / 60
            end_time_off_peak3 = (rectangle_end_off_peak3 - start_time).total_seconds() / 60
            ax.add_patch(plt.Rectangle((start_time_off_peak3, 0), end_time_off_peak3 - start_time_off_peak3,
                                       3 * len(trip_schedule.bus_number.unique()), fill=True, color='grey', alpha=0.3,
                                       edgecolor='grey'))

    # Subtitle of Graph
    # plt.suptitle(f'Bus Schedule', fontsize=45, y=0.95)
    # adding grid
    plt.grid(color='grey', linestyle='-', linewidth=0.5, alpha=0.5)
    # legend
    legend_elements = [Patch(facecolor='#87CEEB', edgecolor='#4C87B9', label='Trip'),
                       Patch(facecolor='red', edgecolor='red', label='Grid Energy'),
                       Patch(facecolor='green', edgecolor='green', label='Solar Energy'),
                       Patch(facecolor='grey', edgecolor='grey', label='Peak Hours'),
                       Patch(facecolor='pink', edgecolor='pink', label='Off Peak Hours'),
                       Patch(facecolor='white', edgecolor='black', label='Overnight Hours')]
    ax.legend(handles=legend_elements, fontsize=60)
    # Saving the figure in the working directory
    # plt.savefig(f"Bus_schedule", dpi='figure', format=None)
    # save the plot in pdf format
    plt.savefig(f'{folder_path}/{network}/visualization/bus_schedule_{scenario}_scenario_{network}.pdf',
                bbox_inches='tight')
    plt.show()





