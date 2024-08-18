
# defining peak/off_peak hours for Canberra
Peak_hours = [(420, 1020), (420 + 1440, 1020 + 1440), (420 + 2 * 1440, 1020 + 2 * 1440), 0.245]
Off_peak_hours = [(0, 420), (1320, 1440), (0 + 1440, 420 + 1440), (1320 + 1440, 1440 + 1440),
                  (0 + 2 * 1440, 420 + 2 * 1440), (1320 + 2 * 1440, 1440 + 2 * 1440), 0.141]
Shoulder_period = [(1020, 1320), (1020 + 1440, 1320 + 1440),
                   (1020 + 2 * 1440, 1320 + 2 * 1440), 0.180]


# defining peak/off_peak hours for Thunder_bay Ontario
Peak_hours_thunder_bay_may_october = [(960, 1260), (960 + 1260, 1260 + 1440), (960 + 2 * 1440, 1260 + 2 * 1440), 0.194]
Overnight_hours_thunder_bay = [(0, 420), (1380, 1440), (0 + 1440, 420 + 1440), (1380 + 1440, 1440 + 1440),
                               (0 + 2 * 1440, 420 + 2 * 1440), (1380 + 2 * 1440, 1440 + 2 * 1440), 0.019]
# from october to april 30
Off_hours_thunder_bay_october_april = [(960, 1260), (960 + 1260, 1260 + 1440), (960 + 2 * 1440, 1260 + 2 * 1440), 0.083]


# for arlington
Peak_hours_june_sept = [(600, 1320), (600 + 1440, 1320 + 1440), (600 + 2 * 1440, 1320 + 2 * 1440), 0.0188]
Peak_hours_rest = [(420, 1320), (420 + 1440, 1320 + 1440), (420 + 2 * 1440, 1320 + 2 * 1440), 0.0188]
# off-peak hours price for all the months = 0.0078


# function to check in which time period the charging event is happening
def tou_pricing_time_stamp_wise(time_stamp, scenario, number_of_scenarios, network):
    """
     gives the price of the energy based on the time period
    :param time_stamp: int
    :param scenario: int
    :param number_of_scenarios: int
    :param network: str
    :return:
    cost of the energy at the time stamp
    """
    # if network string contains Canberra, then the following time period will be considered
    if network.startswith("Canberra"):
        for peak_hour in Peak_hours[:-1]:
            if (time_stamp >= peak_hour[0]) & (time_stamp < peak_hour[1]):
                return Peak_hours[-1]
        for off_peak_hour in Off_peak_hours[:-1]:
            if (time_stamp >= off_peak_hour[0]) & (time_stamp < off_peak_hour[1]):
                return Off_peak_hours[-1]
        for shoulder_hour in Shoulder_period[:-1]:
            if (time_stamp >= shoulder_hour[0]) & (time_stamp < shoulder_hour[1]):
                return Shoulder_period[-1]

    elif (network.startswith("Thunder_bay")) or (network.startswith("Durham")):
        if number_of_scenarios == 1:
            # single scenario
            check_set = {}
        elif number_of_scenarios == 3:
            # 2nd scenario
            check_set = {2}
        elif number_of_scenarios == 12:
            # may, june, july, august, september, october
            check_set = {5, 6, 7, 8, 9, 10}
        else:
            # corresponding weeks of may, july, august, september, october
            check_set = set(range(17, 44))

        if scenario in check_set:
            for peak_hour in Peak_hours_thunder_bay_may_october[:-1]:
                if peak_hour[0] <= time_stamp < peak_hour[1]:
                    return Peak_hours_thunder_bay_may_october[-1]
            for overnight_peak_hour in Overnight_hours_thunder_bay[:-1]:
                if overnight_peak_hour[0] <= time_stamp < overnight_peak_hour[1]:
                    return Overnight_hours_thunder_bay[-1]
            else:
                # mid-peak hour price
                return 0.083
        else:
            for off_peak_hour in Off_hours_thunder_bay_october_april[:-1]:
                if off_peak_hour[0] <= time_stamp < off_peak_hour[1]:
                    return Off_hours_thunder_bay_october_april[-1]
            for overnight_peak_hour in Overnight_hours_thunder_bay[:-1]:
                if overnight_peak_hour[0] <= time_stamp < overnight_peak_hour[1]:
                    return Overnight_hours_thunder_bay[-1]
            else:
                # peak hour price
                return 0.194

    else:
        if number_of_scenarios == 1:
            # single scenario
            check_set = {}
        elif number_of_scenarios == 3:
            # 2nd scenario
            check_set = {2}
        elif number_of_scenarios == 12:
            # june, july, august, september
            check_set = {6, 7, 8, 9}
        else:
            # corresponding weeks of june, august, september
            check_set = set(range(21, 39))

        if scenario in check_set:
            for peak in Peak_hours_june_sept[:-1]:
                if peak[0] <= time_stamp < peak[1]:
                    return Peak_hours_june_sept[-1]
            else:
                return 0.0078
        else:
            for peak in Peak_hours_rest[:-1]:
                if peak[0] <= time_stamp < peak[1]:
                    return Peak_hours_rest[-1]
            else:
                return 0.0078


# check which hour the instance belongs to in a day with 24 hours
def which_hour(time_stamp):
    """
    returns the hour in which the time_stamp lies
    :param time_stamp:
    :return:
    """
    num_days = time_stamp // 1440
    if time_stamp >= 1440:
        time_stamp = time_stamp - num_days * 1440

    return time_stamp // 60
