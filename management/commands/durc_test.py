"""
Management command to run all DURC tests.
"""

import os
import sys
import unittest
import pytest
from django.core.management.base import BaseCommand, CommandError
from django.test.runner import DiscoverRunner


class Command(BaseCommand):
    help = 'Run all DURC tests, both Django-dependent and standalone tests'

    def add_arguments(self, parser):
        parser.add_argument(
            '--standalone-only',
            action='store_true',
            help='Run only standalone tests that do not require Django',
        )
        parser.add_argument(
            '--django-only',
            action='store_true',
            help='Run only tests that require Django',
        )
        parser.add_argument(
            '-v', '--verbosity',
            action='store',
            dest='verbosity',
            default=1,
            type=int,
            help='Verbosity level; 0=minimal output, 1=normal output, 2=verbose output, 3=very verbose output',
        )

    def handle(self, *args, **options):
        verbosity = options['verbosity']
        standalone_only = options['standalone_only']
        django_only = options['django_only']

        # Get the path to the tests directory
        import durc_is_crud
        package_dir = os.path.dirname(durc_is_crud.__file__)
        tests_dir = os.path.join(package_dir, 'tests')

        if verbosity >= 1:
            self.stdout.write(self.style.SUCCESS(f"Running DURC tests from {tests_dir}"))

        # If neither flag is set, run all tests
        run_standalone = not django_only
        run_django = not standalone_only

        success = True

        # Run standalone tests that don't require Django
        if run_standalone:
            if verbosity >= 1:
                self.stdout.write(self.style.NOTICE("Running standalone tests (no Django required):"))
            
            # List of standalone tests
            standalone_tests = [
                'test_utils/test_data_type_mapper.py',
            ]
            
            for test_file in standalone_tests:
                test_path = os.path.join(tests_dir, test_file)
                if verbosity >= 1:
                    self.stdout.write(f"  Running {test_file}...")
                
                # Use pytest to run the test
                try:
                    exit_code = pytest.main([test_path, f'-v'])
                    if exit_code != 0:
                        success = False
                        if verbosity >= 1:
                            self.stdout.write(self.style.ERROR(f"  Failed: {test_file}"))
                    elif verbosity >= 1:
                        self.stdout.write(self.style.SUCCESS(f"  Passed: {test_file}"))
                except Exception as e:
                    success = False
                    if verbosity >= 1:
                        self.stdout.write(self.style.ERROR(f"  Error running {test_file}: {str(e)}"))

        # Run tests that require Django
        if run_django:
            if verbosity >= 1:
                self.stdout.write(self.style.NOTICE("\nRunning tests that require Django:"))
            
            # List of Django-dependent tests
            django_tests = [
                'durc_is_crud.tests.test_utils.test_include_pattern_parser',
                'durc_is_crud.tests.test_utils.test_relational_model_extractor',
                'durc_is_crud.tests.test_commands.test_durc_mine',
                'durc_is_crud.tests.test_commands.test_durc_compile',
            ]
            
            # Use Django's test runner
            test_runner = DiscoverRunner(verbosity=verbosity)
            
            for test_label in django_tests:
                if verbosity >= 1:
                    self.stdout.write(f"  Running {test_label}...")
                
                try:
                    test_suite = test_runner.build_suite([test_label])
                    test_result = test_runner.run_suite(test_suite)
                    
                    if not test_result.wasSuccessful():
                        success = False
                        if verbosity >= 1:
                            self.stdout.write(self.style.ERROR(f"  Failed: {test_label}"))
                    elif verbosity >= 1:
                        self.stdout.write(self.style.SUCCESS(f"  Passed: {test_label}"))
                except Exception as e:
                    success = False
                    if verbosity >= 1:
                        self.stdout.write(self.style.ERROR(f"  Error running {test_label}: {str(e)}"))

        # Final summary
        if verbosity >= 1:
            self.stdout.write("\nTest Summary:")
            if success:
                self.stdout.write(self.style.SUCCESS("All tests passed!"))
            else:
                self.stdout.write(self.style.ERROR("Some tests failed. See above for details."))
                sys.exit(1)
