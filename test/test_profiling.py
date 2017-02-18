""" Test profiling module """

import unittest
import uuid

import mock

from smserver import profiling
from smserver import conf

class ProfilingTest(unittest.TestCase):
    """ Test profiling class """

    @mock.patch("tempfile.gettempdir")
    def test_get_profile_path(self, gettempdir):
        """ Test getting the profile path """

        gettempdir.return_value = "/tmp"

        # Test an existing folder
        self.assertEqual(profiling.get_profile_path("smserver"), "smserver")

        gettempdir.assert_not_called()

        # Test a file in a folder
        self.assertEqual(profiling.get_profile_path("smserver/aaa"), "smserver")
        gettempdir.assert_not_called()

        # Test an invalid path
        self.assertEqual(
            profiling.get_profile_path("invalid_folder_%s" % uuid.uuid4().hex),
            "/tmp"
        )
        gettempdir.assert_called_with()

    @mock.patch("pstats.Stats.dump_stats")
    @mock.patch("smserver.profiling.get_profile_path")
    def test_profile(self, get_profile_path, dump_stats):
        """ Test profiling a function """

        @profiling.profile("arg")
        def func_to_profile(arg):
            """ Function use to test profiling """
            return arg

        @profiling.profile()
        def func_to_profile_without_arg(arg):
            """ Function use to test profiling """
            return arg

        conf.config["profile_path"] = None
        self.assertEqual(func_to_profile(arg="my_arg"), "my_arg")
        get_profile_path.assert_not_called()
        dump_stats.assert_not_called()


        conf.config["profile_path"] = "profile_path"
        get_profile_path.return_value = "profile_path"

        self.assertEqual(func_to_profile(arg="my_arg"), "my_arg")
        get_profile_path.caled_with("profile_path")
        dump_stats.assert_called_once()
        self.assertEqual(dump_stats.call_args[0][0].split("/")[0], "profile_path")
        self.assertIn("str", dump_stats.call_args[0][0].split("/")[1])
        dump_stats.reset_mock()

        get_profile_path.reset_mock()
        self.assertEqual(func_to_profile(arg="my_arg"), "my_arg")
        get_profile_path.assert_not_called()
        dump_stats.assert_called_once()
        self.assertEqual(dump_stats.call_args[0][0].split("/")[0], "profile_path")
        self.assertIn("str", dump_stats.call_args[0][0].split("/")[1])
        dump_stats.reset_mock()

        conf.config["profile_path"] = "another_path"
        get_profile_path.return_value = "another_path"
        self.assertEqual(func_to_profile_without_arg(arg="my_arg"), "my_arg")
        get_profile_path.caled_with("another_path")
        dump_stats.assert_called_once()
        self.assertEqual(dump_stats.call_args[0][0].split("/")[0], "another_path")
        self.assertNotIn("str", dump_stats.call_args[0][0].split("/")[1])
        dump_stats.reset_mock()

        conf.config["profile_path"] = None
