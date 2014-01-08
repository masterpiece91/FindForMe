__author__ = 'alex'

from cement.core import foundation, controller
from SearchManager import SearchManager
from InteractionManager import OutputInteraction
import time


# define an application base controller
class FindForMeBasedController(controller.CementBaseController):
    # Define command line arguments and default values
    class Meta:
        label = 'base'
        description = "Robust directory search application."

        # set default config options
        config_defaults = dict(
            quiet=False,
            debug=False
        )

        arguments = [
            (['-E', '--exact'], dict(action='store_true',
                                     help='Define whether search returns exact matches only.')),
            (['-C', '--case'], dict(action='store_true',
                                    help='Define whether search returns case sensitive results only.')),
            (['-N', '--name'], dict(action='store',
                                    help='Search on this text.')),
            (['-DC', '--show_file_content'], dict(action='store_true',
                                                  help='Show file content when searching through content.')),
            (['-SC', '--search_content'], dict(action='store_true',
                                               help='Search through file content.')),
            (['-D', '--dir'], dict(action='store',
                                   help='Directory in which search should be performed.')),
            (['-R', '--recursive'], dict(action='store_true',
                                         help='Define that search will only occur on top directory.')),
            (['-F', '--filter'], dict(action='store',
                                      help='Filter search by file types. Separate multiple by comma.'))
        ]

    # Define class variables
    __exact_search = None
    __search_query = None
    __file_types = None

    @controller.expose(hide=True, aliases=['run'])
    def default(self):
        self.log.info('Search Initializing...')
        self.log.info('**************************************************************')

        # This delay simply ensures that the cement messages appear before the FindForMe messages begin.
        time.sleep(0.2)

        __exact_case, __exact_search, __is_recursive, __search_dir, __search_query, __file_types, __search_content, \
            __show_file_content = self.setup_search_parameters()

        # Create SearchEngine object
        search_engine = SearchManager()

        # search_engine.search_by_file_type(__search_dir, __search_query, __exact_search, __file_types)
        search_results = search_engine.execute_search(__search_dir, __search_query, __exact_case, __exact_search,
                                                      __file_types, __search_content, __show_file_content,
                                                      __is_recursive)

        # If at least one result is returned then initiate user interaction
        if len(search_results) > 0:
            # Create Interaction object in order to interact with user via input.
            interaction = OutputInteraction()

            # Allow interaction object handle interaction with user
            interaction.request_result_item(__search_dir, search_results, "Choose a number from the list of results:")

    def setup_search_parameters(self):
        if self.pargs.case:
            __exact_case = True
        else:
            __exact_case = False

        if self.pargs.exact:
            __exact_search = True
        else:
            __exact_search = False

        if self.pargs.show_file_content:
            __show_file_content = True
        else:
            __show_file_content = False

        if self.pargs.search_content:
            __search_content = True
        else:
            __search_content = False

        if self.pargs.recursive:
            __is_recursive = True
        else:
            __is_recursive = False

        if self.pargs.name:
            __search_query = str(self.pargs.name).replace("'", "")
        else:
            __search_query = ''

        if self.pargs.dir:
            __search_dir = str(self.pargs.dir).replace("'", "")
        else:
            __search_dir = ''

        if self.pargs.filter:
            __file_types = str(self.pargs.filter).replace("'", "")
        else:
            __file_types = '*'

        return __exact_case, __exact_search, __is_recursive, __search_dir, __search_query, __file_types, \
            __search_content, __show_file_content


class FindForMe(foundation.CementApp):
    class Meta:
        label = 'FindForMe'
        base_controller = FindForMeBasedController

# create the app
app = FindForMe()

try:
    # setup the application
    app.setup()

    app.args.add_argument

    # run the application
    app.run()
finally:
    # close the app
    app.close()