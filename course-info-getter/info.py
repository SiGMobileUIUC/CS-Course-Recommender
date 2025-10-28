import requests
import xml.etree.ElementTree as ET
import io
import json
import re

BASE_URL = "https://courses.illinois.edu/cisapp/explorer/schedule"
YEAR = "2026"
TERM = "spring"
SUBJECT = "CS"

def fetch_xml(url):
    """Fetch XML content and return parsed ElementTree root."""
    r = requests.get(url)
    r.raise_for_status()
    tree = ET.parse(io.StringIO(r.text))
    return tree.getroot()

def remove_namespace(tag):
    """Strip namespace from XML tags."""
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag

subject_url = f"{BASE_URL}/{YEAR}/{TERM}/{SUBJECT}.xml"
print(f"Fetching: {subject_url}\n")

root = fetch_xml(subject_url)

courses = []
for child in root.iter():
    if remove_namespace(child.tag) == "course":
        courses.append({
            "id": child.attrib.get("id"),
            "href": child.attrib.get("href"),
            "title": child.text.strip() if child.text else ""
        })

print(f"Found {len(courses)} {SUBJECT} courses for {TERM} {YEAR}.\n")

for course in courses:
    #print(f"\n=== {course['id']}: {course['title']} ===")
    try:
        course_root = fetch_xml(course["href"])
        tags = dict()
        tags["subject"] = SUBJECT
        for elem in course_root.iter():
            tag = remove_namespace(elem.tag)

            text = (elem.text or "").strip()
            if text and tag not in ["parents", "label", "section", "calendarYear", "term", "subject"]:
                if tag == "courseSectionInformation":
                    try:
                        details = text.split("Prerequisite: ", 1)
                        prereqs = re.split(r'(?: and |; |; and )', details[1])
                        tags["details"] = details[0].strip().rstrip(".")
                        lspre = prereqs[len(prereqs)-1].rstrip(".").strip().split(". ")
                        if len(lspre) > 1:
                            addition = lspre
                            prereqs.pop()

                        course_code_pattern = re.compile(r"[A-Z]{2,4} \d{3}")

                        for i in range(len(prereqs)):
                            prereq = prereqs[i].strip().rstrip(".")
                            if prereq.lower().startswith("one of"):
                                prereq = prereq.removeprefix("one of ").removeprefix("One of ")
                            parts = re.split(r'(?: or |, )', prereq)
                            clean_parts = []
                            for part in parts:
                                part = part.strip()
                                match = course_code_pattern.search(part)
                                if match:
                                    idx = match.start()
                                    condition_text = part[:idx].strip()
                                    course_code = part[idx:].strip()
                                    if condition_text:
                                        clean_parts.append(condition_text)
                                    clean_parts.append(course_code)
                                else:
                                    clean_parts.append(part)

                            bad_tokens = {"credit", "Credit", "", "or"}
                            prereqs[i] = [token for token in clean_parts if token not in bad_tokens]

                        print(prereqs)
                        tags["prereqs"] = prereqs
                    except:
                        tags[tag] = text.strip().rstrip(".")
                else:
                    tags[tag] = text.strip().rstrip(".")
        course["tags"] = tags
    except Exception as e:
        print(f"Failed to fetch {course['id']}: {e}")

with open("courses.json", "w", encoding="utf-8") as f:
    json.dump(courses, f, ensure_ascii=False, indent=4)
