import pandas as pd
import itertools

def time_to_int(time):
    res = ""
    for char in time:
        if char.isdigit():
            res += char
    return int(res)
# print(time_to_int("8:50"))

# times: string of time range, ex: 8:50-10:10
# times_start: string, either "AM" or "PM"
# return: list: [start_time, end_time], in military time as integers
# assumes time range is no more than 6 hours and time range doesn't end after midnight
def to_military(times, times_start):
    times = times.replace(" ", "")
    times_start_end = times.split("-")
    ints_start_end = [time_to_int(time) for time in times_start_end]
    start, end = ints_start_end[0], ints_start_end[1]

    if times_start == "AM" and start > end:
        new_end = end + 1200
        ints_start_end[1] = new_end
    elif times_start == "PM":
        if start < 1200:
            start += 1200
        new_end = end + 1200
        ints_start_end = [start, new_end]

    return ints_start_end
# print(to_military("8:50-10:10", "AM"))
# print(to_military("8:50-1:10", "AM"))
# print(to_military("8:50-1:10", "AM"))
# print(to_military("8:50-10:00", "PM"))
# print(to_military("8:50-12:00", "PM"))
# print(to_military("12:00-12:00", "PM"))

#start, end are integers representing military times
def time_subtraction(start, end):
    start_hour = start // 100
    end_hour = end // 100
    hours_gone_through = end_hour - start_hour
    adjuster = 40 * hours_gone_through
    return end - start - adjuster
# print(time_subtraction(900,1300)) #240
# print(time_subtraction(850,1010)) #80
# print(time_subtraction(900,1040)) #100
# print(time_subtraction(1050,1140)) #50
# print(time_subtraction(1320,1420)) #60

#time_range is same as times in to_military
def get_class_length(time_range, time_start):
    military = to_military(time_range, time_start)
    return str(time_subtraction(military[0], military[1]))

def add_class_length_column(df):
    df["Class length"] = df.apply(lambda row: get_class_length(row["Time"], row["Start"]), axis=1)

def get_start_hour(time_range, am_pm):
    start_hour = int(time_range.split(":")[0])
    if am_pm == "PM":
        return str(start_hour + 12)
    else:
        return str(start_hour)
# print(get_start_hour("8:50-10:10"))

def add_start_hour_column(df):
    df["Start hour"] = df.apply(lambda x: get_start_hour(x["Time"], x["Start"]), axis=1)

# returns whether times1 and times2 overlap, where times1/times2 are both strings representing time ranges
def no_overlap(times1, times2, times1_start, times2_start):
    range1 = to_military(times1, times1_start)
    range2 = to_military(times2, times2_start)
    r1_start, r1_end = range1[0], range1[1]
    r2_start, r2_end = range2[0], range2[1]

    if r1_start <= r2_start:
        compatible = (r1_end <= r2_start)
    else:
        compatible = (r2_end < r1_start)

    return compatible
# print(no_overlap("8:50-10:10", "10:50-11:40", "AM", "AM"))
# print(no_overlap("8:50-10:10", "10:50-11:40", "AM", "PM"))
# print(no_overlap("8:50-10:10", "10:50-11:40", "PM", "AM"))
# print(no_overlap("8:50-10:10", "10:50-11:40", "PM", "PM"))
# print(no_overlap("10:50-12:02", "12:00-1:00", "AM", "AM"))

#days1, days2: strings representing days of the form: "MWF"
def days_compatible(days1, days2):
    compatible = True
    for day in days1:
        if day in days2:
            compatible = False
    return compatible
# print(days_compatible("MWF", "MW"))
# print(days_compatible("M", "MW"))
# print(days_compatible("MFW", "W"))
# print(days_compatible("MFW", "TR"))

#returns true iff 2 classes are compatible given their time and day information
def classes_compatible(times1, times2, start1, start2, days1, days2):
    compatible = True
    if not no_overlap(times1, times2, start1, start2) and not days_compatible(days1, days2):
        compatible = False
    return compatible

#returns true iff a list of classes, where a class is defined by its time and day info, is a valid schedule
def schedule_good(schedule):
    i = 0
    while i < len(schedule):
        j = i + 1
        while j < len(schedule):
            if not classes_compatible(schedule[i].Time, schedule[j].Time, schedule[i].Start, schedule[j].Start, schedule[i].Days, schedule[j].Days):
                return False
            j += 1
        i += 1
    return True

# n: integer - the number the user inputs in the prompt
# credits: a boolean indicating whether the user is restricting by credits instead of classes
# times_deps_names is a column in the user's dataframe or start hour or class length
# from is a list of times_deps_names's
# returns True iff schedule has min/max/exactly n credtis/classes from froms
def meets_restriction(schedule, min_max_exact, n, credits, times_deps_names_days, froms):
    count = 0
    for classs in schedule:
        if credits:
            to_add = classs.Credits
        else:
            to_add = 1
        if classs[times_deps_names_days] in froms:
            count += to_add
    if min_max_exact == "2" and count < n:
        return False
    if min_max_exact == "1" and count > n:
        return False
    if min_max_exact == "3" and count != n:
        return False
    return True

def check_all_restrictions(schedule, restriction_list):
    for restriction in restriction_list:
        if not meets_restriction(schedule, restriction[0], restriction[1], restriction[2], restriction[3], restriction[4]):
            return False
    return True

def only_names(schedule):
    new_schedule = [classs.Name for classs in schedule]
    return new_schedule


#restrictions is a list of lists, where each inner list has length 5 (as indicated by meets_restriction function)
#data is dataframe of classes
#returns: list of possibile schedules
def possible_schedules(data, number_of_classes, restrictions):
    df = pd.read_excel(data)
    df.dropna(subset=["Days", "Time", "Start"], inplace=True)
    add_start_hour_column(df)
    add_class_length_column(df)
    # gets list of all classes, list of pandas.series
    all_classes = [df.iloc[i] for i in range(len(df))]

    # gets list of lists where each list is length number_of_classes and contains pandas.series objects
    all_schedules1 = list(itertools.combinations(all_classes, number_of_classes))

    # change from list of tuples to list of lists
    all_schedules  = [list(sched) for sched in all_schedules1]

    # filtes out any schedules that don't meet resitrctoins or don't have compatible schedules
    good_schedules = [schedule for schedule in all_schedules if schedule_good(schedule) and check_all_restrictions(schedule, restrictions)]

    # done now, this is just for printing in nicer format
    good_schedules_only_names = [", ".join(only_names(schedule)) for schedule in good_schedules]
    print("\n".join(good_schedules_only_names))
    print(f"You have {len(good_schedules_only_names)} options")
