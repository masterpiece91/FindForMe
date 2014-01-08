__author__ = 'alex'

import os
import subprocess
from colorama import Style, init, Back, Fore
from Common import Common


class OutputInteraction:
    def __init__(self):
        self.common_tools = Common()

    def request_result_item(self, search_directory, result_dictionary, input_message):
        message_tool = NotificationController()
        user_input = raw_input(input_message)

        # If escape key is pressed then escape method
        if user_input == '':
            return

        # If the input provided is not a number indicate to user and continue to loop through method until correct input
        # provided.
        if not user_input.isdigit():
            message_tool.print_with_style("No such option exists", message_tool.notification_category.Warning)
            return self.request_result_item(search_directory, result_dictionary, input_message)

        # If the input provided is not a number indicate to user and request another option
        if not user_input.isdigit():
            user_input = raw_input("")

        current_operating_system = self.common_tools.get_operating_system()

        # Make sure that the requested key exists otherwise return a message.
        if int(user_input) in result_dictionary:
            if result_dictionary[int(user_input)]["is_directory"]:
                message_tool.print_with_style(os.path.join(
                    os.path.expanduser(result_dictionary[int(user_input)]["root_directory"]),
                    result_dictionary[int(user_input)]["name"]), message_tool.notification_category.Header)
                print ""
                if current_operating_system == "Windows":
                    subprocess.check_call(["dir", os.path.join(
                        os.path.expanduser(result_dictionary[int(user_input)]["root_directory"]),
                        result_dictionary[int(user_input)]["name"])])
                else:
                    subprocess.check_call(["ls", "-l",
                                           os.path.join(os.path.expanduser(
                                               result_dictionary[int(user_input)]["root_directory"]),
                                               result_dictionary[int(user_input)]["name"])])
            else:
                # os.system('vi %s' % search_results[int(user_input)])
                subprocess.call(["nano",
                                       os.path.join(os.path.expanduser(
                                           result_dictionary[int(user_input)]["root_directory"]),
                                           result_dictionary[int(user_input)]["name"])])
        else:
            message_tool.print_with_style("No such option exists.", message_tool.notification_category.Warning)


class NotificationController:
    def __init__(self):
        self.common_tools = Common()
        self.notification_category = self.common_tools.enum(Normal=Style.NORMAL + Fore.CYAN,
                                                            Large_Header=Style.BRIGHT + Back.RED + Fore.WHITE,
                                                            Header=Style.BRIGHT + Back.WHITE + Fore.BLACK,
                                                            Small_Header=Style.NORMAL + Fore.MAGENTA,
                                                            Small_Print=Style.NORMAL + Fore.GREEN,
                                                            Warning=Style.BRIGHT + Fore.YELLOW,
                                                            Error=Style.BRIGHT + Fore.RED,
                                                            Style=Style.NORMAL + Fore.BLUE)

    def print_with_style(self, output, notification_category):
        # Initialize colorama object
        init()

        if not notification_category:
            notification_category = self.notification_category.Normal

        print notification_category + output + Style.RESET_ALL
