__author__ = 'alex'

import glob
import os
import itertools
import fnmatch
import mmap
import re
import contextlib
import InteractionManager
from Common import Common
from os.path import join, getsize


# This object will contain all properties for a result item
class ResultController:
    def __init__(self):
        self.common_tools = Common()
        self.search_type = self.common_tools.enum(SubDirectory=1, FileName=2, FileContent=3)

    @staticmethod
    def convert_item_to_result_object(item, current_root_directory, current_search_type, item_content=None):
        result_dictionary = {}

        result_dictionary["size"] = getsize(join(current_root_directory, item))
        result_dictionary["is_directory"] = os.path.isdir(os.path.join(os.path.expanduser(current_root_directory), item))
        result_dictionary["root_directory"] = str(current_root_directory)
        result_dictionary["name"] = str(item)
        result_dictionary["search_type"] = current_search_type

        if not item_content is None:
            result_dictionary["item_content"] = item_content

        return result_dictionary

    def convert_list_to_result_object_dictionary(self, current_list, last_dict_enumerator, current_root_directory,
                                                 current_search_type):
        dictionary_enumerator = last_dict_enumerator
        new_dictionary = {}

        for item in current_list:
            assert isinstance(item, str)
            dictionary_enumerator += 1

            new_dictionary[dictionary_enumerator] = self.convert_item_to_result_object(item, current_root_directory,
                                                                                       current_search_type)

        return new_dictionary


class SearchManager:
    def __init__(self):
        pass

    common_tools = Common()

    def search_by_file_type(self, search_dir, search_query, match_case, search_pattern):
        # Set up counter to ensure keep track of records found
        record_counter = 0

        # Fix directory path
        clean_search_dir = os.path.expanduser(search_dir)

        if not match_case:
            search_query = search_query.lower()

        for fileName in self.__multiple_file_types(clean_search_dir, search_pattern):
            if match_case:
                cur_file = fileName
                if cur_file.find(search_query) != -1:
                    record_counter += 1
                    print fileName
            else:
                cur_file = fileName.lower()

                if cur_file.find(search_query.lower()) != -1:
                    record_counter += 1
                    print fileName

        if record_counter == 0:
            print 'No results found'

    def execute_search(self, search_dir, search_query, match_case, exact_search, search_pattern, search_content,
                       show_file_content, is_recursive=True):
        # TODO - Push all console interaction to the FindForMe class. Class will remain for search mechanism. (OOP)
        # Assert that method is receiving correct parameter object types
        assert isinstance(search_dir, str)
        assert isinstance(search_query, str)
        assert isinstance(match_case, bool)
        assert isinstance(exact_search, bool)
        assert isinstance(search_pattern, str)
        assert isinstance(search_content, bool)
        assert isinstance(show_file_content, bool)
        assert isinstance(is_recursive, bool)

        # Set up counters to ensure keep track of records found
        file_item_enumerator = 0
        sub_directory_enumerator = 0
        file_content_enumerator = 0
        result_enumerator = 0
        flat_results_enumerator = 0
        result_file_size = 0

        # Set up result controller
        result_controller = ResultController()

        # Set up search result dictionary
        flat_search_results = {}
        sub_directory_results = {}
        file_content_results = {}
        file_results = {}

        # Fix directory path
        if search_dir == '':
            clean_search_dir = os.path.dirname(os.path.abspath(__file__))
        else:
            clean_search_dir = os.path.expanduser(search_dir)

        if not match_case:
            search_query = search_query.lower()

        # Perform recursive search through all sub-directories
        for root_directory, sub_directories, files in os.walk(clean_search_dir):
            filtered_sub_directories = self.__filter_directories(sub_directories, search_query, exact_search,
                                                                 match_case)

            for sub_dir in filtered_sub_directories:
                # If a pattern does exist then do not search through sub directories. User is clearly
                # looking for files that fit the pattern therefore breakout of loop
                if search_pattern != '':
                    break

                sub_directory_enumerator += 1
                flat_results_enumerator += 1

                # Add to dictionary for future retrieval
                sub_directory_results[sub_directory_enumerator] = \
                    result_controller.convert_item_to_result_object(sub_dir, root_directory,
                                                                    result_controller.search_type.SubDirectory)

                # Add to flat dictionary. This dictionary is the one returned to client
                flat_search_results[flat_results_enumerator] = \
                    result_controller.convert_item_to_result_object(sub_dir, root_directory,
                                                                    result_controller.search_type.SubDirectory)

            # If search should not be recursive then simply delete all sub directories from list
            if not is_recursive:
                del sub_directories[:]

            # Filter file list by pattern
            filtered_files = fnmatch.filter(files, search_pattern)

            for listed_file in filtered_files:
                cur_file = listed_file
                if match_case:
                    if (cur_file.find(search_query) != -1 and exact_search is False) or (
                                cur_file == search_query and exact_search is True):
                        # Keep count of search results
                        file_item_enumerator += 1
                        flat_results_enumerator += 1

                        # Add to dictionary for future retrieval
                        file_results[file_item_enumerator] = result_controller. \
                            convert_item_to_result_object(listed_file, root_directory,
                                                          result_controller.search_type.FileName)

                        # Add to flat dictionary. This dictionary is the one returned to client
                        flat_search_results[flat_results_enumerator] = result_controller. \
                            convert_item_to_result_object(listed_file, root_directory,
                                                          result_controller.search_type.FileName)
                else:
                    if (cur_file.lower().find(search_query.lower()) != -1 and exact_search is False) or (
                                cur_file.lower() == search_query.lower() and exact_search is True):
                        # Keep count of search results
                        file_item_enumerator += 1
                        flat_results_enumerator += 1

                        # Add to dictionary for future retrieval
                        file_results[file_item_enumerator] = result_controller. \
                            convert_item_to_result_object(listed_file, root_directory,
                                                          result_controller.search_type.FileName)

                        # Add to flat dictionary. This dictionary is the one returned to client
                        flat_search_results[flat_results_enumerator] = result_controller. \
                            convert_item_to_result_object(listed_file, root_directory,
                                                          result_controller.search_type.FileName)

                # File content search is bound by the pattern provided. The use case for this is that I may only want
                # to find information in certain files such as a word document.
                if search_content:
                    # Keep count of how many occurrences are found
                    instance_enumerator = 0

                    # Instantiate content dictionary. Initialization happens here because we don't want to use more
                    # memory than needed
                    file_content_dict = {}

                    for content_extract in self.__search_file_content(listed_file, root_directory, search_query,
                                                                      match_case, exact_search):
                        instance_enumerator += 1

                        # If it is not desired to show content results then simply break from loop once first instance
                        # is found
                        if not show_file_content:
                            break

                        # Add content lines to dictionary. Will be used later to show content.
                        file_content_dict[instance_enumerator] = content_extract

                    # At least one instance of search query was found and therefore we should add the result object
                    # to our file results dictionary
                    if instance_enumerator >= 1:
                        file_content_enumerator += 1
                        flat_results_enumerator += 1

                        # Add to dictionary for future retrieval
                        file_content_results[file_content_enumerator] = result_controller.convert_item_to_result_object(
                            listed_file, root_directory, result_controller.search_type.FileContent, file_content_dict)

                        # Add to flat dictionary. This dictionary is the one returned to client
                        flat_search_results[flat_results_enumerator] = result_controller.convert_item_to_result_object(
                            listed_file, root_directory, result_controller.search_type.FileContent, file_content_dict)

            # Instantiate temp dictionary utilized for printing purposes
            temp_search_results = {}

            # Insert result dictionaries into one overall dictionary
            if len(sub_directory_results) > 0:
                temp_search_results["sub_directories"] = sub_directory_results
            if len(file_content_results) > 0:
                temp_search_results["file_content"] = file_content_results
            if len(file_results) > 0:
                temp_search_results["files"] = file_results

            # Print results
            result_file_size, result_enumerator = self.__print_results(temp_search_results, root_directory,
                                                                       result_enumerator, result_file_size)

            # Before looping through make sure to clear dictionaries
            file_results = {}
            file_content_results = {}
            sub_directory_results = {}

        if result_enumerator > 0:
            notification_manager = InteractionManager.NotificationController()
            # Print Search Statistics
            print ''    # Skip line
            notification_manager.print_with_style(
                "*********************************************************************************",
                notification_manager.notification_category.Style)
            notification_manager.print_with_style("\t\t\t\tResult File Size: %0.1f MB" % (result_file_size / 1024.0) +
                                                  " (%i" % result_file_size + ")",
                                                  notification_manager.notification_category.Small_Print)
            notification_manager.print_with_style(os.linesep + "\t\t\t\tResult Count: %i" % result_enumerator,
                                                  notification_manager.notification_category.Small_Print)

        return flat_search_results

    @staticmethod
    def __print_results(result_dictionary, current_directory, overall_enumerator, overall_result_file_size):
        sub_directory_counter = 0
        file_content_counter = 0
        file_counter = 0
        result_enumerator = overall_enumerator
        result_file_size = overall_result_file_size

        #try:
        notification_manager = InteractionManager.NotificationController()

        if len(result_dictionary) == 0:
            return result_file_size, result_enumerator

        notification_manager.print_with_style("Directory Searched: %s" % current_directory,
                                              notification_manager.notification_category.Large_Header)

        for result_dictionary_item in result_dictionary:

            result_item = result_dictionary[result_dictionary_item]
            if "sub_directories" in result_dictionary_item and len(result_item) > 0:
                # Print as header. It should print at before any results are printed.
                print ''    # Skip line
                notification_manager.print_with_style("Sub Directory Results:",
                                                      notification_manager.notification_category.Header)
                notification_manager.print_with_style("------------------------------------------------",
                                                      notification_manager.notification_category.Style)
                for sub_directory in result_item:
                    result_enumerator += 1
                    sub_directory_counter += 1
                    sub_directory_item = result_item[sub_directory]
                    result_file_size += int(sub_directory_item["size"])

                    notification_manager.print_with_style("(" + str(result_enumerator) + ") - " +
                                                          str(sub_directory_counter) + ".\t%s" %
                                                          sub_directory_item["name"] +
                                                          " (%0.1f MB" % (sub_directory_item["size"] / 1024.0) + ")",
                                                          notification_manager.notification_category.Normal)
            elif "file_content" in result_dictionary_item and len(result_item) > 0:
                # Print as header. It should print at before any results are printed.
                print ''    # Skip line
                notification_manager.print_with_style("File Content Results:",
                                                      notification_manager.notification_category.Header)
                notification_manager.print_with_style("------------------------------------------------",
                                                      notification_manager.notification_category.Style)
                for file_content in result_item:
                    result_enumerator += 1
                    file_content_counter += 1
                    file_content_item = result_item[file_content]
                    result_file_size += int(file_content_item["size"])

                    if not "item_content" in file_content_item:
                        notification_manager.print_with_style("(" + str(result_enumerator) + ") - " +
                                                              str(file_content_counter) + ".\t%s" %
                                                              file_content_item["name"] +
                                                              " (%0.1f MB" % (file_content_item["size"] / 1024.0) + ")",
                                                              notification_manager.notification_category.Normal)
                    else:
                        notification_manager.print_with_style("(" + str(result_enumerator) + ") - " +
                                                              str(file_content_counter) +
                                                              ".\tFile Name: %s" % file_content_item["name"] +
                                                              " (%0.1f MB" % (file_content_item["size"] / 1024.0) + ")",
                                                              notification_manager.notification_category.Normal)
                        notification_manager. \
                            print_with_style('*****************************************************************',
                                             notification_manager.notification_category.Style)

                        # set up content dictionary in order to iterate over it.
                        file_content_dictionary = file_content_item["item_content"]

                        for file_content_item in file_content_dictionary:
                            notification_manager.print_with_style(file_content_dictionary[file_content_item],
                                                                  notification_manager.notification_category.
                                                                  Small_Print)
            elif "files" in result_dictionary_item and len(result_item) > 0:
                # Print as header. It should print at before any results are printed.
                print ''    # Skip line
                notification_manager.print_with_style("File Name Results:",
                                                      notification_manager.notification_category.Header)
                notification_manager.print_with_style("------------------------------------------------",
                                                      notification_manager.notification_category.Style)

                for current_file in result_item:
                    result_enumerator += 1
                    file_counter += 1
                    file_item = result_item[current_file]
                    result_file_size += int(file_item["size"])

                    notification_manager.print_with_style("(" + str(result_enumerator) + ") - " + str(file_counter) +
                                                          ".\t%s" % file_item["name"] +
                                                          " (%0.1f MB" % (file_item["size"] / 1024.0) + ")",
                                                          notification_manager.notification_category.Normal)

        return result_file_size, result_enumerator

    @staticmethod
    def __search_file_content(current_file, current_directory, search_query, match_case, exact_search):

        if exact_search:
            search_query = r"\b" + re.escape(search_query) + r"\b"

        if match_case:
            pattern = re.compile(search_query)
        else:
            pattern = re.compile(search_query, re.IGNORECASE)

        with open(os.path.join(current_directory, current_file), mode='r') as file_object:
            try:
                with contextlib.closing(mmap.mmap(file_object.fileno(), 0, access=mmap.ACCESS_READ)) as file_stream:
                    previous_file_content_location = 0

                    for match in pattern.finditer(file_stream):
                        # Find beginning of line where instance exists
                        new_line_starting_location = file_stream.rfind(os.linesep,
                                                                       previous_file_content_location,
                                                                       match.start())

                        # Save current location for next iteration.
                        # This will allow next iteration what is the beginning of the line
                        previous_file_content_location = match.start()

                        # Move to position where first instance was found from the last current position
                        if new_line_starting_location != -1:
                            file_stream.seek(new_line_starting_location + 1, os.SEEK_SET)
                            yield str(file_stream.readline()).strip("\t").strip(os.linesep)
            except ValueError:
                pass

    def __multiple_file_types(self, search_dir, patterns):
        pattern_list = self.__arrange_pattern_array(patterns)
        return itertools.chain.from_iterable(glob.glob1(search_dir, pattern) for pattern in pattern_list)

    @staticmethod
    def __filter_directories(directories, search_query, exact_search, match_case):
        # If there is no search criteria then return the same directory listing
        if not search_query:
            return directories

        # Ensure that you match case if required only. Otherwise filter by any string match
        if exact_search:
            if match_case:
                filtered_directories = [directory for directory in directories if directory == search_query]
            else:
                filtered_directories = [directory for directory in directories if
                                        directory.lower() == search_query.lower()]
        else:
            if match_case:
                filtered_directories = [directory for directory in directories if
                                        directory.find(search_query) >= 0]
            else:
                filtered_directories = [directory for directory in directories if
                                        directory.lower().find(search_query.lower()) >= 0]

        return filtered_directories

    @staticmethod
    def __arrange_pattern_array(pattern):
        return pattern.replace(' ', '').split(",")