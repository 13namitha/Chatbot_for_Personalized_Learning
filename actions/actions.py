from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import json


class ActionFetchLMS(Action):
    def name(self) -> Text:
        return "action_fetch_lms"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        topic = tracker.get_slot('topic')
        if not topic:
            dispatcher.utter_message(text="Please specify a topic.")
            return []

        # Load LMS data
        try:
            with open('lms.json', 'r') as f:
                lms_data = json.load(f)
            if topic in lms_data:

                answer = lms_data.get(topic, {}).get('answer', "I don't have information on that topic.")
                response = f" Here is the solution : {answer}"

            else:
                response = f"Sorry, I don't have information about {topic} right now."
        except Exception as e:
            response = "There was an issue retrieving the course information."
        dispatcher.utter_message(text=response)
        return []

class ActionFetchLMSReference(Action):
    def name(self) -> Text:
        return "action_fetch_lms_reference"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Retrieve the topic from the user's input
        topic = tracker.get_slot('topic')
        if not topic:
            dispatcher.utter_message(text="Please specify a topic to get references.")
            return []

        try:
            # Load LMS data
            with open('lms_data.json', 'r') as f:
                lms_data = json.load(f)

            # Fetch references for the specified topic
            topic_data = lms_data.get(topic)
            if topic_data and isinstance(topic_data, dict):
                references = topic_data.get('references', [])

                # Build the response in Markdown format
                if references and isinstance(references, list):
                    response = f"Here are some useful references for **{topic}**:\n\n"
                    for ref in references:
                        response += f"- [{ref['name']}]({ref['url']})\n"
                    response = response.strip()
                else:
                    response = f"No valid references available for the topic: **{topic}**."
            else:
                response = f"Sorry, I don't have any information about the topic: **{topic}**."
        except FileNotFoundError:
            response = "The LMS data file is missing. Please ensure 'lms_data.json' exists in the project directory."
        except Exception as e:
            response = f"There was an issue retrieving the references: {str(e)}"

        # Send the response to the user
        dispatcher.utter_message(response, allow_html=True)  # Ensure Markdown/HTML is allowed
        return []




COURSE_DATA_FILE = "courses.json"


# Utility function to load and save data
def load_course_data():
    try:
        with open(COURSE_DATA_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_course_data(data):
    with open(COURSE_DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)


class ActionRegisterCourse(Action):
    def name(self) -> Text:
        return "action_register_course"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_id = tracker.sender_id
        course = tracker.get_slot("course")

        if not course:
            dispatcher.utter_message(text="Please specify the course you want to register for.")
            return []

        # Load course data
        data = load_course_data()

        # Add course for user
        if user_id not in data:
            data[user_id] = {}

        if course not in data[user_id]:
            data[user_id][course] = {"progress": 0}  # Start with 0% progress
            save_course_data(data)
            dispatcher.utter_message(template="utter_course_registered", course=course)
        else:
            dispatcher.utter_message(text=f"You are already registered for {course}.")

        return []


class ActionShowEnrollments(Action):
    def name(self) -> Text:
        return "action_show_enrollments"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_id = tracker.sender_id
        data = load_course_data()

        if user_id in data and data[user_id]:
            courses = "\n".join([f"- {course}" for course in data[user_id].keys()])
            dispatcher.utter_message(template="utter_enrolled_courses", courses=courses)
        else:
            dispatcher.utter_message(template="utter_no_courses")

        return []


class ActionFetchCourseProgress(Action):
    def name(self) -> Text:
        return "action_fetch_course_progress"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_id = tracker.sender_id
        course = tracker.get_slot("course")

        if not course:
            dispatcher.utter_message(text="Please specify the course you want to check progress for.")
            return []

        data = load_course_data()

        if user_id in data and course in data[user_id]:
            progress = data[user_id][course]["progress"]
            dispatcher.utter_message(template="utter_course_progress", course=course, progress=progress)
        else:
            dispatcher.utter_message(template="utter_course_not_found", course=course)

        return []