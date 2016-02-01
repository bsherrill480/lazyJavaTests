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
# this means multiple constructors of the same length will cause problems, since I only tell constructors apart by
# number of arguments

#POST: adds equals, toHashCode

from os import listdir
from os.path import isfile, join
import re
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
        self._args = None
        self.constructor_lines = constructor_lines
        self._get_method_to_constructor_pos = self._build_get_method_to_constructor_pos()

    def get_args(self):
        if self._args is None:
            one_string = " ".join(self.constructor_lines)
            opening_paren_index = one_string.index("(")
            closing_paren_index = one_string.index(")")
            between_parens = one_string[opening_paren_index+1:closing_paren_index]
            arguments = between_parens.split(",")
            arguments = [arg.strip() for arg in arguments]
            arguments = [arg.split(" ") for arg in arguments]
            self._args = arguments
        return self._args

    def _build_get_method_to_constructor_pos(self):
        getter_names = [prepend_and_camel_case("get", arg[1]) for arg in self.get_args()]
        return {getter_name: i for (i, getter_name) in enumerate(getter_names)}

    def get_method_name_to_constructor_pos(self, method):
        return self._get_method_to_constructor_pos[method]

    # def count_args_of_constructor(self):
    #     between_parens = self.get_between_parens()
    #     return len(self.get_args)

    def __len__(self):
        return len(self.get_args())

    def __repr__(self):
        return str(self.constructor_lines)

    # def get_args_names(self):
    #     names s[]
    #     for arg in self.get_args():
    #         name = arg[1]
    #         names.append(name)
    #     return names


class SetupTestObject(object):
    def __init__(self, line):
        """
        :param line: a single line (from change into single line) that constructs class to be tested object
        """
        line_split = line.split("=")
        self.variable_name = line_split[0].strip()
        self._object_instantiation = line_split[1].strip()

    def get_args_to_constructor(self):
        first_paren_index = self._object_instantiation.index("(")
        last_paren_index = [i for i, x in enumerate(self._object_instantiation) if x == ")"][-1]
        args_string = self._object_instantiation[first_paren_index + 1:last_paren_index]
        location_of_outer_parnes = []
        stack = []
        for i, char in enumerate(args_string):
            if char == "," and not stack:
                location_of_outer_parnes.append(i)
            elif char == "(":
                stack.append("(")
            elif char == ")":
                stack.pop()
        substrings_to_get = location_of_outer_parnes + [len(args_string)]
        args = []
        last_location = 0
        for subtring_upper in substrings_to_get:
            args.append(args_string[last_location:subtring_upper])
            last_location = subtring_upper + 1
        return args

    def __repr__(self):
        return "\"{} = {}\"".format(self.variable_name, self._object_instantiation)

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

    def get_contents_of_method(self, lines):
        start_paren = 0
        for i, line in enumerate(lines):
            if "{" in line:
                start_paren = i
        return lines[start_paren + 1:-1]

    def compress_into_single_java_lines(self, lines):
        compressed_lines = []
        line_accumulator = ""
        for line in lines:
            line = line.strip()
            line_accumulator += line
            if len(line) >= 2 and line[-1] == ";" or line[0:2] == "//":
                compressed_lines.append(line_accumulator)
                line_accumulator = ""
        return compressed_lines


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

class GetterJavaTest(object):
    def __init__(self, method_name, test_method_name):
        self.method_name = method_name
        self.test_method = test_method_name

    def __repr__(self):
        return "{}, {}".format(self.method_name, self.test_method)

    def method_string(self):
        return "public void {}() throws Exception {{\n".format(self.test_method)

class JavaTestClassFile(TestBase, FileBase):
    hash_code_method = 'public void testHashCode'
    equals_method = 'public void testEquals'

    def __init__(self, file):
        super(JavaTestClassFile, self).__init__(file)
        setup_line_num = self.get_setup_line_numbers()
        self.setup_lines = self.collect_to_closing_curly_braces(setup_line_num[0]) if len(setup_line_num) > 0 else []
        self.setup_lines_contents = self.get_contents_of_method(self.setup_lines)

    def get_class_name(self):
        return self.file.split(".")[0][:-4] #remove Test

    def getters_without_tests(self, possible_getters_methods):
        """

        :param possible_getters_methods: e.g. ['public String getFirst', 'public String getLast']
        :return: array of GetterJavaTest
        """
        potential_getter_tests = set()
        test_method_name_to_method_name = dict()
        for possible_getters_method in possible_getters_methods:
            method_name = possible_getters_method.split(" ")[2]
            test_method_name = prepend_and_camel_case("test", method_name)
            test_method = "public void {}".format(test_method_name)
            test_method_name_to_method_name[test_method] = method_name
            potential_getter_tests.add(test_method)
        test_that_do_exist = self.substrings_exist_in_file(potential_getter_tests)
        test_that_do_not_exist = potential_getter_tests.difference(test_that_do_exist)
        return [GetterJavaTest(method_name, test_method) for test_method, method_name in
                test_method_name_to_method_name.items() if test_method in test_that_do_not_exist]

    def hash_code_test_method_exists(self):
        return self._hash_code_method_exists()

    def equals_test_method_exists(self):
        return self._equals_method_exists()

    def can_use_to_make_test(self):
        return self.setup_lines

    def get_setup_line_numbers(self):
        setup_begginging = "public void setUp"
        return self.get_line_numbers_of_substring(setup_begginging)

    def get_compressed_lines(self):
        return self.compress_into_single_java_lines(self.setup_lines_contents)

    def get_subclasses(self, compressed_lines):
        subclasses = set()
        class_name = self.get_class_name()
        for line in compressed_lines:
            if "is subclass of {}".format(class_name):
                m = re.search("\s*([a-zA-z]+) is a subclass of {}".format(class_name), line)
                if m:
                    subclasses.add(m.groups()[0])
        return subclasses


    def get_lines_with_objects_to_test(self, compressed_lines):
        """
        :param compressed_lines: compressed single compressed_lines
        :return: lines that create instance of class we need to test
        """

    def get_test_objects(self):
        compressed_lines = self.get_compressed_lines()
        subclasses = self.get_subclasses(compressed_lines)
        possible_classes = set(subclasses)
        possible_classes.add(self.get_class_name())
        setup_test_objects = []
        for line in compressed_lines:
            one_of_possible_classes_in_line = False
            for possible_class in possible_classes:
                one_of_possible_classes_in_line = one_of_possible_classes_in_line or possible_class in line
            if one_of_possible_classes_in_line and "=" in line:
                setup_test_objects.append(SetupTestObject(line))
        return setup_test_objects

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

    def get_test_methods_for_getters(self):
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
        return self.java_test_class_file.getters_without_tests(self.java_class_file.get_test_methods_for_getters())

    def get_setup_test_objects(self):
        return

    def add_missing_getters(self):
        missing_tests = self.get_getter_tests_that_need_to_be_made()
        test_objects = self.java_test_class_file.get_test_objects()
        constructors = self.java_class_file.constructors
        # print("missig-tests:")
        # print(missing_tests)
        # print("test_objects ")
        # print(test_objects)
        # print("constructors ")
        # print(constructors)
        missing_tests_string = ""
        arg_len_to_constructor = {len(constructor): constructor for constructor in constructors}
        for missing_test in missing_tests:
            test_string = ""
            test_string += missing_test.method_string()
            method_name = missing_test.method_name
            for test_object in test_objects:
                var_name = test_object.variable_name
                args_to_test_obj = test_object.get_args_to_constructor()
                constructor = arg_len_to_constructor[len(args_to_test_obj)]
                index_of_expected_return = constructor.get_method_name_to_constructor_pos(method_name)
                expected_return = args_to_test_obj[index_of_expected_return]
                test_string += "   assertEquals({var_name}.{method_name}(), {expected_return}".format(
                    var_name=var_name, method_name=method_name, expected_return=expected_return
                )
            test_string += "}\n"  # close method string
            missing_tests_string += test_string
        return missing_tests_string
    def __repr__(self):
        return self.java_class_file.get_class_name()


class JavaTestAllMaker(object):
    def __init__(self):
        java_files = JavaFiles()
        self.potential_tests_to_make = [JavaTestClassMaker(JavaClassFile(f), JavaTestClassFile(t))
                            for f, t in java_files.get_java_classes_with_tests()]
        self.valid_tests_to_make = [f for f in self.potential_tests_to_make if f.can_make_test()]

    def debug(self):
        for possible_test_to_make in self.valid_tests_to_make:
            # constructors = possible_test_to_make.java_class_file.constructors
            # for constructor in constructors:
            #     print(constructor._get_method_to_constructor_pos)
            # print(possible_test_to_make.java_class_file.get_class_name())
            # print(possible_test_to_make.java_class_file.get_test_methods_for_getters())
            # print(possible_test_to_make.get_getter_tests_that_need_to_be_made())
            # test_objects = possible_test_to_make.java_test_class_file.get_test_objects()
            # for obj in test_objects:
            #     print("{}, {}".format(obj.variable_name, obj.get_args_to_constructor()))
            # print(possible_test_to_make.java_class_file.hash_code_method_exists())
            # print(possible_test_to_make.java_class_file.equals_method_exists())
            # print(possible_test_to_make.java_test_class_file.hash_code_test_method_exists())
            # print(possible_test_to_make.java_test_class_file.equals_test_method_exists())
            possible_test_to_make.add_missing_getters()
jtam = JavaTestAllMaker()
jtam.debug()
