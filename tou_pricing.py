"""
ToU electricity pricing for different networks
"""
# defining peak/off_peak hours for Canberra
peak_start_hour = 7
peak_end_hour = 17
shoulder_start_hour = 17
shoulder_end_hour = 22
off_peak_start_hour = 22
off_peak_end_hour = 7
peak_price = 0.4065 * 0.60
shoulder_price = 0.3322 * 0.60
off_peak_price = 0.2745 * 0.60
Peak_hours = [(peak_start_hour * 60, peak_end_hour * 60), (peak_start_hour * 60 + 1440, peak_end_hour * 60 + 1440),
              (peak_start_hour * 60 + 2 * 1440, peak_end_hour * 60 + 2 * 1440), peak_price]
Off_peak_hours = [(0, off_peak_end_hour * 60), (off_peak_start_hour * 60, 1440),
                  (0 + 1440, off_peak_end_hour * 60 + 1440), (off_peak_start_hour * 60 + 1440, 1440 + 1440),
                  (0 + 2 * 1440, off_peak_end_hour * 60 + 2 * 1440),
                  (off_peak_start_hour * 60 + 2 * 1440, 1440 + 2 * 1440), off_peak_price]
Shoulder_period = [(shoulder_start_hour * 60, shoulder_end_hour * 60),
                   (shoulder_start_hour * 60 + 1440, shoulder_end_hour * 60 + 1440),
                   (shoulder_start_hour * 60 + 2 * 1440, shoulder_end_hour * 60 + 2 * 1440), shoulder_price]

# defining peak/off_peak hours for Durham, Canada
peak_start_hour_durham_may_october = 11
peak_end_hour_durham_may_october = 17
peak_price_durham_may_october = 0.182 * 0.67

peak_start_hour_durham_november_april_first = 7
peak_end_hour_durham_november_april_first = 11
peak_start_hour_durham_november_april_second = 17
peak_end_hour_durham_november_april_second = 19
peak_price_durham_november_april = 0.158 * 0.67

first_window_start_hour_durham = 7
first_window_end_hour_durham = 11
second_window_start_hour_durham = 11
second_window_end_hour_durham = 17
third_window_start_hour_durham = 17
third_window_end_hour_durham = 19

off_peak_start_hour_durham_first = 0
off_peak_end_hour_durham_first = 7
off_peak_start_hour_durham_second = 19
off_peak_end_hour_durham_second = 24
off_peak_price_durham_may_october = 0.087 * 0.67
off_peak_price_durham_november_april = 0.076 * 0.67

mid_peak_start_hour_durham_may_october_first = 7
mid_peak_end_hour_durham_may_october_first = 11
mid_peak_start_hour_durham_may_october_second = 17
mid_peak_end_hour_durham_may_october_second = 19
mid_peak_price_durham_may_october = 0.122 * 0.67

mid_peak_start_hour_durham_november_april = 11
mid_peak_end_hour_durham_november_april = 17
mid_peak_price_durham_november_april = 0.122 * 0.67

first_window_price_first = (1 / 3 * peak_price_durham_november_april + 2 / 3 * mid_peak_price_durham_may_october)
first_window_price_second = (2 / 3 * peak_price_durham_november_april + 1 / 3 * mid_peak_price_durham_may_october)
second_window_price_first = (1 / 3 * mid_peak_price_durham_november_april + 2 / 3 * peak_price_durham_may_october)
second_window_price_second = (2 / 3 * mid_peak_price_durham_november_april + 1 / 3 * peak_price_durham_may_october)
third_window_price_first = (1 / 3 * peak_price_durham_november_april + 2 / 3 * mid_peak_price_durham_may_october)
third_window_price_second = (2 / 3 * peak_price_durham_november_april + 1 / 3 * mid_peak_price_durham_may_october)
off_peak_updated_price_first = (
        1 / 3 * off_peak_price_durham_november_april + 2 / 3 * off_peak_price_durham_may_october)
off_peak_updated_price_second = (
        2 / 3 * off_peak_price_durham_november_april + 1 / 3 * off_peak_price_durham_may_october)

peak_price_durham_average = (peak_price_durham_november_april + mid_peak_price_durham_may_october) / 2
off_peak_price_durham_average = (off_peak_price_durham_may_october + off_peak_price_durham_november_april) / 2
mid_peak_price_durham_average = (mid_peak_price_durham_november_april + peak_price_durham_may_october) / 2

# defining peak/off_peak hours for Durham Ontario
Peak_hours_durham_may_october = [(peak_start_hour_durham_may_october * 60, peak_end_hour_durham_may_october * 60),
                                 (peak_start_hour_durham_may_october * 60 + 1440,
                                  peak_end_hour_durham_may_october * 60 + 1440),
                                 (peak_start_hour_durham_may_october * 60 + 2 * 1440,
                                  peak_end_hour_durham_may_october * 60 + 2 * 1440),
                                 peak_price_durham_may_october]

peak_hours_durham_november_april = [
    (peak_start_hour_durham_november_april_first * 60, peak_end_hour_durham_november_april_first * 60), (
        peak_start_hour_durham_november_april_first * 60 + 1440,
        peak_end_hour_durham_november_april_first * 60 + 1440),
    (peak_start_hour_durham_november_april_first * 60 + 2 * 1440,
     peak_end_hour_durham_november_april_first * 60 + 2 * 1440),
    (peak_start_hour_durham_november_april_second * 60, peak_end_hour_durham_november_april_second * 60),
    (peak_start_hour_durham_november_april_second * 60 + 1440,
     peak_end_hour_durham_november_april_second * 60 + 1440),
    (peak_start_hour_durham_november_april_second * 60 + 2 * 1440,
     peak_end_hour_durham_november_april_second * 60 + 2 * 1440),
    peak_price_durham_november_april]

Off_peak_hours_durham_may_october = [(off_peak_start_hour_durham_first * 60, off_peak_end_hour_durham_first * 60),
                                     (off_peak_start_hour_durham_second * 60, off_peak_end_hour_durham_second * 60),
                                     (off_peak_start_hour_durham_first * 60 + 1440,
                                      off_peak_end_hour_durham_first * 60 + 1440), (
                                         off_peak_start_hour_durham_second * 60 + 1440,
                                         off_peak_end_hour_durham_second * 60 + 1440),
                                     (off_peak_start_hour_durham_first * 60 + 2 * 1440,
                                      off_peak_end_hour_durham_first * 60 + 2 * 1440),
                                     (off_peak_start_hour_durham_second * 60 + 2 * 1440,
                                      off_peak_end_hour_durham_second * 60 + 2 * 1440),
                                     off_peak_price_durham_may_october]

Off_peak_hours_durham_november_april = [(off_peak_start_hour_durham_first * 60, off_peak_end_hour_durham_first * 60), (
    off_peak_start_hour_durham_second * 60, off_peak_end_hour_durham_second * 60), (
                                            off_peak_start_hour_durham_first * 60 + 1440,
                                            off_peak_end_hour_durham_first * 60 + 1440), (
                                            off_peak_start_hour_durham_second * 60 + 1440,
                                            off_peak_end_hour_durham_second * 60 + 1440), (
                                            off_peak_start_hour_durham_first * 60 + 2 * 1440,
                                            off_peak_end_hour_durham_first * 60 + 2 * 1440), (
                                            off_peak_start_hour_durham_second * 60 + 2 * 1440,
                                            off_peak_end_hour_durham_second * 60 + 2 * 1440),
                                        off_peak_price_durham_november_april]

mid_peak_hours_durham_may_october = [
    (mid_peak_start_hour_durham_may_october_first * 60, mid_peak_end_hour_durham_may_october_first * 60),
    (mid_peak_start_hour_durham_may_october_first * 60 + 1440, mid_peak_end_hour_durham_may_october_first * 60 + 1440),
    (mid_peak_start_hour_durham_may_october_first * 60 + 2 * 1440,
     mid_peak_end_hour_durham_may_october_first * 60 + 2 * 1440),
    (mid_peak_start_hour_durham_may_october_second * 60, mid_peak_end_hour_durham_may_october_second * 60),
    (
        mid_peak_start_hour_durham_may_october_second * 60 + 1440,
        mid_peak_end_hour_durham_may_october_second * 60 + 1440),
    (mid_peak_start_hour_durham_may_october_second * 60 + 2 * 1440,
     mid_peak_end_hour_durham_may_october_second * 60 + 2 * 1440),
    mid_peak_price_durham_may_october]

mid_peak_hours_durham_november_april = [
    (mid_peak_start_hour_durham_november_april * 60, mid_peak_end_hour_durham_november_april * 60), (
        mid_peak_start_hour_durham_november_april * 60 + 1440, mid_peak_end_hour_durham_november_april * 60 + 1440),
    (mid_peak_start_hour_durham_november_april * 60 + 2 * 1440,
     mid_peak_end_hour_durham_november_april * 60 + 2 * 1440),
    mid_peak_price_durham_november_april]

first_window_hours_durham_first = [(first_window_start_hour_durham * 60, first_window_end_hour_durham * 60),
                                   (first_window_start_hour_durham * 60 + 1440,
                                    first_window_end_hour_durham * 60 + 1440),
                                   (first_window_start_hour_durham * 60 + 2 * 1440,
                                    first_window_end_hour_durham * 60 + 2 * 1440), first_window_price_first]

first_window_hours_durham_second = [(first_window_start_hour_durham * 60, first_window_end_hour_durham * 60),
                                    (first_window_start_hour_durham * 60 + 1440,
                                     first_window_end_hour_durham * 60 + 1440),
                                    (first_window_start_hour_durham * 60 + 2 * 1440,
                                     first_window_end_hour_durham * 60 + 2 * 1440), first_window_price_second]

second_window_hours_durham_first = [(second_window_start_hour_durham * 60, second_window_end_hour_durham * 60),
                                    (second_window_start_hour_durham * 60 + 1440,
                                     second_window_end_hour_durham * 60 + 1440),
                                    (second_window_start_hour_durham * 60 + 2 * 1440,
                                     second_window_end_hour_durham * 60 + 2 * 1440), second_window_price_first]

second_window_hours_durham_second = [(second_window_start_hour_durham * 60, second_window_end_hour_durham * 60),
                                     (second_window_start_hour_durham * 60 + 1440,
                                      second_window_end_hour_durham * 60 + 1440),
                                     (second_window_start_hour_durham * 60 + 2 * 1440,
                                      second_window_end_hour_durham * 60 + 2 * 1440), second_window_price_second]

third_window_hours_durham_first = [(third_window_start_hour_durham * 60, third_window_end_hour_durham * 60),
                                   (third_window_start_hour_durham * 60 + 1440,
                                    third_window_end_hour_durham * 60 + 1440),
                                   (third_window_start_hour_durham * 60 + 2 * 1440,
                                    third_window_end_hour_durham * 60 + 2 * 1440), third_window_price_first]

third_window_hours_durham_second = [(third_window_start_hour_durham * 60, third_window_end_hour_durham * 60),
                                    (third_window_start_hour_durham * 60 + 1440,
                                     third_window_end_hour_durham * 60 + 1440),
                                    (third_window_start_hour_durham * 60 + 2 * 1440,
                                     third_window_end_hour_durham * 60 + 2 * 1440), third_window_price_second]

off_peak_hours_durham_updated_first = [(off_peak_start_hour_durham_first * 60, off_peak_end_hour_durham_first * 60),
                                       (off_peak_start_hour_durham_second * 60, off_peak_end_hour_durham_second * 60),
                                       (off_peak_start_hour_durham_first * 60 + 1440,
                                        off_peak_end_hour_durham_first * 60 + 1440), (
                                           off_peak_start_hour_durham_second * 60 + 1440,
                                           off_peak_end_hour_durham_second * 60 + 1440),
                                       (off_peak_start_hour_durham_first * 60 + 2 * 1440,
                                        off_peak_end_hour_durham_first * 60 + 2 * 1440),
                                       (off_peak_start_hour_durham_second * 60 + 2 * 1440,
                                        off_peak_end_hour_durham_second * 60 + 2 * 1440), off_peak_updated_price_first]

off_peak_hours_durham_updated_second = [(off_peak_start_hour_durham_first * 60, off_peak_end_hour_durham_first * 60),
                                        (off_peak_start_hour_durham_second * 60, off_peak_end_hour_durham_second * 60),
                                        (off_peak_start_hour_durham_first * 60 + 1440,
                                         off_peak_end_hour_durham_first * 60 + 1440), (
                                            off_peak_start_hour_durham_second * 60 + 1440,
                                            off_peak_end_hour_durham_second * 60 + 1440),
                                        (off_peak_start_hour_durham_first * 60 + 2 * 1440,
                                         off_peak_end_hour_durham_first * 60 + 2 * 1440),
                                        (off_peak_start_hour_durham_second * 60 + 2 * 1440,
                                         off_peak_end_hour_durham_second * 60 + 2 * 1440),
                                        off_peak_updated_price_second]

# for arlington (or other networks)
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
            # single scenario (assumption?)
            check_set = {}
            check_set_average = {1}
            check_set_first = {}
            check_set_second = {}
        elif number_of_scenarios == 3:
            # 2nd scenario (assumption?)
            check_set = {2}
            check_set_average = {3}
            check_set_first = {}
            check_set_second = {}
        elif number_of_scenarios == 4:
            check_set = {3}
            check_set_first = {2}
            check_set_second = {4}
            check_set_average = {}
        elif number_of_scenarios == 12:
            # may, june, july, august, september, october
            check_set = {5, 6, 7, 8, 9, 10}
            check_set_average = {}
            check_set_first = {}
            check_set_second = {}
        else:
            # corresponding weeks of may, june, july, august, september, october
            check_set = set(range(18, 44))
            check_set_average = {}
            check_set_first = {}
            check_set_second = {}

        if scenario in check_set:
            for peak_hour in Peak_hours_durham_may_october[:-1]:
                if peak_hour[0] <= time_stamp < peak_hour[1]:
                    return Peak_hours_durham_may_october[-1]
            for overnight_peak_hour in Off_peak_hours_durham_may_october[:-1]:
                if overnight_peak_hour[0] <= time_stamp < overnight_peak_hour[1]:
                    return Off_peak_hours_durham_may_october[-1]
            else:
                # mid-peak hour price
                return mid_peak_hours_durham_may_october[-1]

        elif scenario in check_set_average:
            for peak_hour in peak_hours_durham_november_april[:-1]:
                if peak_hour[0] <= time_stamp < peak_hour[1]:
                    return peak_price_durham_average
            for overnight_peak_hour in Off_peak_hours_durham_november_april[:-1]:
                if overnight_peak_hour[0] <= time_stamp < overnight_peak_hour[1]:
                    return off_peak_price_durham_average
            else:
                # mid-peak hour price
                return mid_peak_price_durham_average

        elif scenario in check_set_first:
            for hour_val in first_window_hours_durham_first[:-1]:
                if hour_val[0] <= time_stamp < hour_val[1]:
                    return first_window_hours_durham_first[-1]
            for hour_val in second_window_hours_durham_first[:-1]:
                if hour_val[0] <= time_stamp < hour_val[1]:
                    return second_window_hours_durham_first[-1]
            for hour_val in third_window_hours_durham_first[:-1]:
                if hour_val[0] <= time_stamp < hour_val[1]:
                    return third_window_hours_durham_first[-1]
            for hour_val in off_peak_hours_durham_updated_first[:-1]:
                if hour_val[0] <= time_stamp < hour_val[1]:
                    return off_peak_hours_durham_updated_first[-1]

        elif scenario in check_set_second:
            for hour_val in first_window_hours_durham_second[:-1]:
                if hour_val[0] <= time_stamp < hour_val[1]:
                    return first_window_hours_durham_second[-1]
            for hour_val in second_window_hours_durham_second[:-1]:
                if hour_val[0] <= time_stamp < hour_val[1]:
                    return second_window_hours_durham_second[-1]
            for hour_val in third_window_hours_durham_second[:-1]:
                if hour_val[0] <= time_stamp < hour_val[1]:
                    return third_window_hours_durham_second[-1]
            for hour_val in off_peak_hours_durham_updated_second[:-1]:
                if hour_val[0] <= time_stamp < hour_val[1]:
                    return off_peak_hours_durham_updated_second[-1]


        else:
            for off_peak_hour in mid_peak_hours_durham_november_april[:-1]:
                if off_peak_hour[0] <= time_stamp < off_peak_hour[1]:
                    return mid_peak_hours_durham_november_april[-1]
            for overnight_peak_hour in Off_peak_hours_durham_november_april[:-1]:
                if overnight_peak_hour[0] <= time_stamp < overnight_peak_hour[1]:
                    return Off_peak_hours_durham_november_april[-1]
            else:
                # peak hour price
                return peak_hours_durham_november_april[-1]

    else:  # other networks (not required here)
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
            # corresponding weeks of june, july, august, september
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
