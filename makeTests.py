#!/usr/bin/env python

#PRE: all java files are correctly according to common conventions. Only test have Test somewhere in the
# name. commented are not ignored (so they can screw up recognition).
# uses a fragile linke. Assumes parameters's passed to constructor will be names of the corresponding field.
# i.e.
# public Foo(String first, string second) {
#    this.first = first;
#    this.second = second;
# }
# means the Foo class has getters: getFirst, getSecond

#POST: adds equals, toHashCode

from os import listdir
from os.path import isfile, join
LOCAL_DIR = "./"

def prepend_and_camel_case(prepend, word):
    word_first_letter_upper = word[0].upper()
    if len(word) > 1:
        word_first_letter_upper += word[1:]
    return prepend + word_first_letter_upper

class JavaFiles(object):
    def __init__(self):
        self.files_in_dir = None

    def get_java_classes_with_tests(self):
        java_files = [f for f in self.get_files_in_dir() if ".java" in f]
        return [(f, self.test_name_for_file(f)) for f in java_files if self.file_has_test(f)]

    @staticmethod
    def test_name_for_file(file):
        """
        :param file: *.java where * is the wildcard matching
        :returns testname of corresponding class.
        """
        without_extension = file.split(".")[0]
        return without_extension + "Test.java"

    def file_has_test(self, file):
        """
        :param file: *.java where * is the wildcard matching
        :returns bool if file has corresponding test
        """
        return self.test_name_for_file(file) in self.get_files_in_dir()

    def get_files_in_dir(self):
        if self.files_in_dir is None:
            self.files_in_dir = [f for f in listdir(LOCAL_DIR) if isfile(join(LOCAL_DIR, f))]
        return list(self.files_in_dir)


class JavaConstructor(object):
    def __init__(self, constructor_lines):
        self.constructor_lines = constructor_lines

    def get_args(self):
        one_string = " ".join(self.constructor_lines)
        opening_paren_index = one_string.index("(")
        closing_paren_index = one_string.index(")")
        between_parens = one_string[opening_paren_index+1:closing_paren_index]
        arguments = between_parens.split(",")
        arguments = [arg.strip() for arg in arguments]
        arguments = [arg.split(" ") for arg in arguments]
        return arguments

    # def count_args_of_constructor(self):
    #     between_parens = self.get_between_parens()
    #     return len(self.get_args)

    def __repr__(self):
        return str(self.constructor_lines)

    # def get_args_names(self):
    #     names = []
    #     for arg in self.get_args():
    #         name = arg[1]
    #         names.append(name)
    #     return names



class FileBase(object):
    def __init__(self, file):
        super(FileBase, self).__init__()
        self.file = file
        self.file_lines = []
        with open(self.file, 'r') as f:
            for i, line in enumerate(f):
                self.file_lines.append(line)

    def get_line_numbers_of_substring(self, substring):
        line_numbers = []
        for i, line in enumerate(self.file_lines):
            if substring in line:
                line_numbers.append(i)
        return line_numbers

    def substrings_exist_in_file(self, substrings):
        """
        :param substrings: iterable of strings
        :return: set of strings from substrings that were found in file
        """
        substrings_that_exist_in_file = set()
        for line in self.file_lines:
            for substring in substrings:
                if substring in line:
                    substrings_that_exist_in_file.add(substring)
        return substrings_that_exist_in_file

    # def get_line(self, line_num):
    #     return self.get_lines([line_num])

    # def get_lines(self, lines_to_get):
    #     lines = []
    #     with open(self.file, 'r') as f:
    #         for i, cur_line in enumerate(f):
    #             if i in lines_to_get:
    #                 lines.append(cur_line)
    #     return lines

    def collect_to_closing_curly_braces(self, line_with_or_before_curlybrace):
        lines = []
        stack = []
        has_found_init_curlybrace = False

        for cur_line in self.file_lines[line_with_or_before_curlybrace:]:
                lines.append(cur_line)
                if not has_found_init_curlybrace:
                    if "{" in cur_line:
                        has_found_init_curlybrace = True
                if has_found_init_curlybrace:
                    if "{" in cur_line:
                        stack.append("{")
                    if "}" in cur_line:
                        stack.pop()
                if has_found_init_curlybrace and not stack:
                    break
        return lines


class TestBase(object):
    def __init__(self, *args, **kwargs):
        super(TestBase, self).__init__(*args, **kwargs)
        self._hash_code_exists = False
        self._equals_exists = False
        self._has_run_hashcode_equals_check = False

    @property
    def hash_code_method(self):
        raise NotImplementedError("forgot to implement hash_code_method")

    @property
    def equals_method(self):
        raise NotImplementedError("forgot to implement equals_method")

    def can_use_to_make_test(self):
        raise NotImplementedError("can_make_test not implemented")

    def _run_hashcode_equals_exists_check(self):
        existing_substings = self.substrings_exist_in_file([self.hash_code_method, self.equals_method])
        self._hash_code_exists = self.hash_code_method in existing_substings
        self._equals_exists = self.equals_method in existing_substings
        self._has_run_hashcode_equals_check = True

    def _hash_code_method_exists(self):
        if not self._has_run_hashcode_equals_check:
            self._run_hashcode_equals_exists_check()
        return self._hash_code_exists

    def _equals_method_exists(self):
        if not self._has_run_hashcode_equals_check:
            self._run_hashcode_equals_exists_check()
        return self._equals_exists


class JavaTestClassFile(TestBase, FileBase):
    hash_code_method = 'public void testHashCode'
    equals_method = 'public void testEquals'

    def __init__(self, file):
        super(JavaTestClassFile, self).__init__(file)

    def getters_without_tests(self, possible_getters_methods):
        """

        :param possible_getters_methods: e.g. ['public String getFirst', 'public String getLast']
        :return:
        """
        potential_getter_tests = set()
        for possible_getters_method in possible_getters_methods:
            method_name = possible_getters_method.split(" ")[2]
            test_method_name = prepend_and_camel_case("test", method_name)
            test_method = "public void {}".format(test_method_name)
            potential_getter_tests.add(test_method)
        test_that_do_exist = self.substrings_exist_in_file(potential_getter_tests)
        test_that_do_not_exist = potential_getter_tests.difference(test_that_do_exist)
        return test_that_do_not_exist

    def hash_code_test_method_exists(self):
        return self._hash_code_method_exists()

    def equals_test_method_exists(self):
        return self._equals_method_exists()

    def can_use_to_make_test(self):
        return True


class JavaClassFile(TestBase, FileBase):
    hash_code_method = 'public int hashCode'
    equals_method = 'public boolean equals'

    def __init__(self, file):
        super(JavaClassFile, self).__init__(file)
        self.constructors = self._get_constructors()

    def get_class_name(self):
        return self.file.split(".")[0]

    def get_constructors_line_numbers(self):
        constructor_beginning = "public {}(".format(self.get_class_name())
        return self.get_line_numbers_of_substring(constructor_beginning)

    # def get_constructors_lines(self):
    #     constructor_beginning = "public {}(".format(self.get_class_name())
    #     line_numbers = self.get_line_numbers_of_substring(constructor_beginning)
    #     return self.get_lines(line_numbers)

    @staticmethod
    def get_getter_methods(constructor):
        getter_names = []
        for arg in constructor.get_args():
            date_type = arg[0]
            getter_name = prepend_and_camel_case("get", arg[1])
            getter_method = "public {} {}".format(date_type, getter_name)
            getter_names.append(getter_method)
        return getter_names

    def get_getters_to_use_in_test(self):
        potential_getters = set()
        for constructor in self.constructors:
            for getter in self.get_getter_methods(constructor):
                potential_getters.add(getter)
        getters_that_actually_exist = self.substrings_exist_in_file(potential_getters)
        return getters_that_actually_exist

    def hash_code_method_exists(self):
        return self._hash_code_method_exists()

    def equals_method_exists(self):
        return self._equals_method_exists()

    def _get_constructors(self):
        constructor_lines = self.get_constructors_line_numbers()
        constructors = []
        for beginning_line in constructor_lines:
            lines_of_constructor = self.collect_to_closing_curly_braces(beginning_line)
            constructors.append(JavaConstructor(lines_of_constructor))
        return constructors

    def can_use_to_make_test(self):
        return self.constructors


class JavaTestClassMaker(object):
    def __init__(self, java_class_file, java_test_class_file):
        self.java_class_file = java_class_file
        self.java_test_class_file = java_test_class_file

    def can_make_test(self):
        return self.java_class_file.can_use_to_make_test() and self.java_test_class_file.can_use_to_make_test()

    def get_getter_tests_that_need_to_be_made(self):
        return self.java_test_class_file.getters_without_tests(self.java_class_file.get_getters_to_use_in_test())

    def __repr__(self):
        return self.java_class_file.get_class_name()


class JavaTestAllMaker(object):
    def __init__(self):
        java_files = JavaFiles()
        self.tests_to_make = [JavaTestClassMaker(JavaClassFile(f), JavaTestClassFile(t))
                            for f, t in java_files.get_java_classes_with_tests()]
        self.possible_tests_to_make = [f for f in self.tests_to_make if f.can_make_test()]

    def debug(self):
        for possible_test_to_make in self.possible_tests_to_make:
            print(possible_test_to_make.java_class_file.get_class_name())
            print(possible_test_to_make.java_class_file.get_getters_to_use_in_test())
            print(possible_test_to_make.get_getter_tests_that_need_to_be_made())
            # print(possible_test_to_make.java_class_file.hash_code_method_exists())
            # print(possible_test_to_make.java_class_file.equals_method_exists())
            # print(possible_test_to_make.java_test_class_file.hash_code_test_method_exists())
            # print(possible_test_to_make.java_test_class_file.equals_test_method_exists())

jtam = JavaTestAllMaker()
jtam.debug()
