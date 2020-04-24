import pandas as pd
import itertools
import helpers

def main():
    still_playing = True
    while still_playing:
        spreadsheet = input("\nWELCOME TO SCHEDULER!!!\nType the name of an excel file with your class information.\n\nRequired columns:\nName\nTime (in this exact format: 8:50-10:10)\nDays (suggested formatting: MWF)\nStart (AM if class starts before noon, else PM)\nOther suggested columns:\nCredits\nDepartment\nYou can also have any other columns you'd like - you'll be able to restrict your outputted schedules by any column in your spreadsheet.\n\n***NOTE: EVERYTHING IS CASE SENSITIVE!***\n\n")
        initial_errors = []
        try:
            df = pd.read_excel(spreadsheet)
        except:
            initial_errors.append("The excel file couldn't be opened. Make sure you spelled its file name correctly and that you're in the right directory.")
        try:
            number_of_classes = int(input("\nHow many classes would you like to take?  "))
        except:
            initial_errors.append("Your input for number of classes was invalid. Make sure to enter a single number.")
        if initial_errors != []:
            print("\nYou already made one or two mistakes! Here they are:")
            print("\n".join(initial_errors))
            print("\nType 'Yes' when asked to play again to try again!")
            x = input("Read the above statements - press enter to continue.\n")
        else:
            adding_restrictions = True
            restrictions = []
            while adding_restrictions and initial_errors == []:
                yes_no = input("\nWould you like to add any more restrictions? Yes or No: ")
                errors = []
                if yes_no == "No":
                    adding_restrictions = False
                elif yes_no == "Yes":
                    print("\nIf you mess up, just keep going - you'll have the option to confirm or delete your restriction at the end.")
                    x = input("Read the above statement - press enter to continue. \n")
                    to_restrict = input("What class characteristic what would you like to restrict by?\nOptions: Start hour, Class length, or any column name in your excel file. Useful choices (if they exist in your spreadsheet) include: Department, Name, Days:  ")
                    if to_restrict not in df.columns and to_restrict not in ["Start hour", "Class length"]:
                        errors.append(f"{to_restrict} is not a valid class characteristic. The class characteristic must be either a column in your spreadsheet, 'Class length' or 'Start hour'.")
                    print(f"\nYour restriction will be of the form:\nMy schedule will have (A)(at most/at least/exactly) (B)(N) (C)(classes/credits) which have {to_restrict} as one of the following: (D)(list of {to_restrict}s)")
                    min_max = input("\nEnter your response for (A): type 1 for at most, 2 for at least, 3 for exactly:  ")
                    if min_max not in ["1", "2", "3"]:
                        errors.append("Your input for (A) was invalid. You must enter 1,2, or 3.")
                    n_str = input("Enter your response for (B) (ex: 2)  ")
                    try:
                        n = int(n_str)
                    except:
                        errors.append("Your input for (B) was invalid. You must enter a number.")
                    classes_credits = input("Enter your response for (C) - 1 for credits, 2 for classes -  ")
                    if classes_credits not in ["1", "2"]:
                        errors.append("Your input for (C) was invalid. You must enter 1 or 2.")
                    credits = (classes_credits == "1")
                    # not sure how to sanitize this input
                    froms_input = input(f"Enter a list of {to_restrict}s in the following format: item1,item2,item3,item4 (separated by commas, no spaces)\n(If restricting by Start hour, enter list items in military time. If restricting by Class length, enter lengths in minutes.)\n")
                    froms_list = froms_input.split(",")
                    if errors != []:
                        print("\nYou made at least one mistake. Your mistakes were:")
                        print("\n".join(errors))
                        x = input("Read the above statement - press enter to continue.")
                        print("\nThe restriction you just created won't be taken into account - try again!")
                        x = input("Read the above statement - press enter to continue.")
                    else:
                        min_max_dict = {"1": "at most", "2": "at least", "3": "exactly"}
                        credits_dict = {"1": "credits", "2": "classes"}
                        print(f"\nHere is the restriction you just created:\nMy schedule will consist of {min_max_dict[min_max]} {n} {credits_dict[classes_credits]} which have {to_restrict} as one of the following: {froms_input}.")
                        x = input("Read the above statement - press enter to continue.")
                        inp1 = input("\nDo you want this restriction to be applied when generating your possible schedules? Yes or No?  ")
                        if inp1 == "Yes":
                            restrictions.append([min_max, n, credits, to_restrict, froms_list])
                            print("\nRestriction added!")
                        else:
                            print("\nOk, this restriction will be deleted!")
                            x = input("Read the above statement - press enter to continue.")

                else:
                    print("Try again - make sure to type either Yes or No.")
            print("Ok, here come your schedules!")
            helpers.possible_schedules(spreadsheet, number_of_classes, restrictions)

        play_again = input("\nWould you like to play again? Yes or No?  ")
        if play_again != "Yes":
            still_playing = False
            print("See you next time!")

main()
