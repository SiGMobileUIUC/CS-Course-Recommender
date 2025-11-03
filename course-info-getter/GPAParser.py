import csv
import json
import requests
from io import StringIO


def search_file():
    cs_classes = []
    COURSE_TYPE_INDEX = 3

    url = 'https://raw.githubusercontent.com/wadefagen/datasets/refs/heads/main/gpa/uiuc-gpa-dataset.csv'

    response = requests.get(url)
    response.raise_for_status()

    csv_data = StringIO(response.text)
    csvFile = csv.reader(csv_data)

    for lines in csvFile:
        if lines[COURSE_TYPE_INDEX] == "CS":
            cs_classes.append(lines)

    return cs_classes


def add_arrays_by_index(arr1, arr2):
    if len(arr1) != len(arr2):
        raise ValueError("Arrays must be of equal length to add element-wise.")

    result_array = []
    for i in range(len(arr1)):
        result_array.append(arr1[i] + arr2[i])
    return result_array


def get_class_grades_dict(data):
    NAME_INDEX = 5

    GRADES_INDEX_START = 7
    GRADES_INDEX_END = 20

    name = data[0][NAME_INDEX]
    grades = [int(item) for item in data[0][GRADES_INDEX_START:GRADES_INDEX_END]]
    class_dict = {name: grades}
    for i in range(1, len(data)):
        line_data = [int(item) for item in data[i][GRADES_INDEX_START:GRADES_INDEX_END]]
        line_name = data[i][NAME_INDEX]
        if line_name in class_dict:
            temp_grades = add_arrays_by_index(class_dict[line_name], line_data)
            class_dict[line_name] = (temp_grades)
        else:
            temp_dict = {line_name: line_data}
            class_dict.update(temp_dict)

    return find_class_gpa(class_dict)

def find_class_gpa(data):
    gpa_scale = [4.0, 4.0, 3.67, 3.33, 3.0, 2.67, 2.33, 2.0, 1.67, 1.33, 1.0, 0.67, 0.0]

    class_gpa_dict = {}

    for key in data:
        grades = data[key]
        students = 0
        sum = 0.0
        for i in range(0, len(grades)):
            students += grades[i]
            sum += grades[i] * gpa_scale[i]
        class_gpa_dict.update({key: round(sum / students, 2)})

    return class_gpa_dict

def get_names(data):
    class_names = {}
    CLASS_NAME_INDEX = 5
    CLASS_ID_INDEX = 4

    for array in data:
        if array[CLASS_NAME_INDEX] not in class_names:
            info = {array[CLASS_NAME_INDEX] : int(array[CLASS_ID_INDEX])}
            class_names.update(info)

    return class_names

def final_info(class_dict, names):
    info = []
    index = 0

    for key in class_dict:
        info_dict = {"ID" : names[key], "NAME": key, "GPA" : int(class_dict[key])}
        info.append(info_dict)
        index += 1
    return info

def main():
    data = search_file()
    class_dict = get_class_grades_dict(data)
    names = get_names(data)
    final = final_info(class_dict, names)

    with open('class_gpa.json', 'w') as json_file:
        json.dump(final, json_file, indent=4)

    print(f"Successfully processed {len(final)} CS courses")
    print(f"Output saved to class_gpa.json")


if __name__ == '__main__':
    main()



