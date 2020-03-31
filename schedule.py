import pandas as pd
import itertools
# add length column
# assume longest possible class is 6 hours and no class goes past midnight!
# let user either enter a filename fro which we can obtain a dataframe, or manually enter class names, times, days, start times
# add some kind of undo functionality, also add save last settings functionality
def time_to_int(time):
    res = ""
    for char in time:
        if char.isdigit():
            res += char
    return int(res)
# print(time_to_int("8:50"))

# return list of length 2 with [start_time, end_time] in miilitary time as integers,
# assumes time range is no more than 6 hours and time range doesn't end after midnight
def to_military(times, times_start):
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

def get_start_hour(time_range, am_pm):
    start_hour = int(time_range.split(":")[0])
    if am_pm == "PM":
        return str(start_hour + 12)
    else:
        return str(start_hour)
# print(get_start_hour("8:50-10:10"))

def add_start_hour_column(df):
    df["Start hour"] = df.apply(lambda x: get_start_hour(x["Time"], x["Start"]), axis=1)

# if times1 starts before times2, then times1 must end before times2 starts
# if times2 starts before times1, then times2 must end before times1 starts
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

def classes_compatible(times1, times2, start1, start2, days1, days2):
    compatible = True
    if not no_overlap(times1, times2, start1, start2) and not days_compatible(days1, days2):
        compatible = False
    return compatible

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

#min_max_exact can be "Min" or "Max" "Exactly" or "MAX"
# n is a number
# credits is True if you want to restrict number of credits instead of number of classes
# times_deps_names is "Start hour" or "Department" or "Name" or "Days"
# from is a list of departments, starting hours, or class
# returns True iff schedule has min/max/exactly n credtis/classes from list
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



#restrictions is a list of lists, where each inner list has length 5
def possible_schedules(data, number_of_classes, restrictions):
    df = pd.read_excel(data)
    df.dropna(subset=["Days", "Time", "Start"], inplace=True)
    add_start_hour_column(df)
    # gets list of all classes, list of pandas.series
    all_classes = [df.iloc[i] for i in range(len(df))]
    # get all schedules of length 4, regardless of compatibility (all subsets of all_schedules)
    # i.e, gets list of lists where each list is length number_of_classes and contains pandas.series objects
    all_schedules1 = list(itertools.combinations(all_classes, number_of_classes))
    # change from list of tuples to list of lists
    all_schedules  = [list(sched) for sched in all_schedules1]
    good_schedules = [schedule for schedule in all_schedules if schedule_good(schedule) and check_all_restrictions(schedule, restrictions)]
    # done now, this is just for printing
    good_schedules_only_names = [", ".join(only_names(schedule)) for schedule in good_schedules]
    print("\n".join(good_schedules_only_names))
    print(f"You have {len(good_schedules_only_names)} options")


def main():
    still_playing = True
    while still_playing:
        spreadsheet = input("Type the name of an excel file with your class information.\nRequired columns:\nName\nTime (in this exact format: 8:50-10:10)\nDays (formatted like: MWF)\nStart (AM if class starts before noon, else PM)\Other suggested columns:\nCredits\nDepartment\n***NOTE: EVERYTHING IS CASE SENSITIVE!***\n")
        number_of_classes = int(input("How many classes would you like to take?  "))
        adding_restrictions = True
        restrictions = []
        while adding_restrictions:
            yes_no = input("Would you like to add any more restrictions? Yes or No: ")
            if yes_no == "No":
                adding_restrictions = False
            elif yes_no == "Yes":
                to_restrict = input("What class characteristic what would you like to restrict by?\nOptions: Start hour, or any column name in your excel file. Useful choices include: Department, Name, Day, Time, Start hour:  ")
                print(f"Your restriction will be of the form:\n My schedule will have (A)(at most/at least/exactly) (B)(N) (C)(classes/credits) which have {to_restrict} as one of the following: (D)(list of {to_restrict}s)")
                min_max = input("Enter your response for (A): type 1 for at most, 2 for at least, 3 for exactly:  ")
                n = int(input("Enter your response for (B) (ex: 2)  "))
                classes_credits = input("Enter your response for (C) - 1 for credits, 2 for classes -  ")
                credits = (classes_credits == "1")
                froms_input = input(f"Enter a list of {to_restrict}s  in the following format: item1,item2,item3,item4 (separated by commas, no spaces)\nIf restricting by start hour, enter list items in military time.\n")
                froms_list = froms_input.split(",")
                restrictions.append([min_max, n, credits, to_restrict, froms_list])
            else:
                print("Try again - make sure to type either Yes or No.")
        print("Ok, here come your schedules!")
        possible_schedules(spreadsheet, number_of_classes, restrictions)

        play_again = input("Would you like to do all that again? Yes or No?  ")
        if play_again != "Yes":
            still_playing = False

main()


# check for duplicates
# res = []
# for schedule in good_schedules_only_names:
#     if schedule in res:
#         print("VERY BAD")
#         break
#     else:
#         res.append(schedule)

#check that changing to only names worked
# def is_good(names, alls):
#     for i in range(len(names)):
#         this_name = names[i]
#         if this_name != alls[i][0]:
#             return False
#     return True
# for i in range(len(good_schedules)):
#     if not is_good(good_schedules_only_names[i], good_schedules[i]):
#         print("OH NO!")
