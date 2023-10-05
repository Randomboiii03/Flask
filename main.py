from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from claude_api import Client
import json
import re

app = Flask(__name__)


def get_prompt(question_type, level):
    if question_type == "mcq":
        prompt = f'''
                    I want you to act as highly experienced {level} professor with expertise in the subject matter covered in the uploaded document.

                    Write 100 multiple-choice questions for a college-level test based on the uploaded document. Each question should exercise students' problem-solving and reading comprehension skills. The questions should not repeat, be easy to understand, and yet challenging.

                    Steps to complete:
                    1. Carefully review the uploaded document to identify key topics, concepts, and information that should be covered in the questions.
                    2. For each question, create a stem (the main part of the question) that fully describes the problem. Ensure that students could answer the question based on the stem alone, without looking at the answer choices.            
                    3. Include all relevant information in the stem and avoid repeating information in the answer choices. This will make the options easier to read and understand.            
                    4. Eliminate excessive wording and irrelevant information from the stem to avoid confusing students and wasting their time.            
                    5. Limit the number of answer choices to between four and five per question. Research suggests that this range is effective, and it's challenging to come up with plausible distractors beyond this range.            
                    6. Make sure there is only one correct answer per question. Avoid having multiple correct options where one is "more" correct than the others.            
                    7. Craft distractors (incorrect answer choices) that are appealing and plausible. If the distractors are too farfetched, students may easily identify the correct answer.            
                    8. Ensure that the answer choices do not repeat throughout the set of questions.

                    Write a 100 multiple-choice questions that cover the content of the uploaded document and adhere to the guidelines provided.

                    Format Output: The output should be in JSON format, follow this template:

                    {{
                       "title": "Unique Title",
                       "tags": ["Genres", "Difficulty", "Topics", "Level", "Question-Type", "Many More"],
                       "description": "Short and Engaging Description",
                       "questions": [
                          {{
                             "question": "Question Stem?",
                             "choices": ["Choice A", "Choice B", "Choice C", "Choice D"],
                             "answer": "Correct Choice"
                          }},
                          // Add more questions in a similar format as needed
                       ]
                    }}

                    Each question should have a unique title, appropriate tags, a concise description, and a clear stem with answer choices.
                    Remember to follow the additional information provided for designing multiple-choice questions, and ensure that the question is well-crafted to effectively assess students' knowledge.
                    '''

    elif question_type == "tof":
        prompt = f'''
                    I want you to act as highly experienced {level} professor with expertise in the subject matter covered in the uploaded document.

                    Write 100 true or false questions for an upcoming college test based on the uploaded document. This question should be clear, concise, and challenging, ensuring it exercises students' problem-solving and reading comprehension skills.

                    Steps to complete:
                    1. Review the uploaded document thoroughly to understand its content.
                    2. Identify a specific statement or concept from the document that can be transformed into a TRUE OR FALSE question.
                    3. Formulate the question as a statement that is unequivocally true or false without any exceptions.
                    4. Ensure the question is not negatively constructed and is free from ambiguity.
                    5. Make incorrect answers appear tempting to students who do not know the correct answer.

                    Write a 100 true or false questions that assesses students' understanding of the document's content..

                    Format Output: The output should be in JSON format, follow this template:

                    {{
                       "title": "Unique Title",
                       "tags": ["Genres", "Difficulty", "Topics", "Level", "Question-Type", "Many More"],
                       "description": "Short and Engaging Description",
                       "questions": [
                          {{
                             "question": "Question Stem?",
                             "choices": ["True", "False"],
                             "answer": "True or False (based on the correct answer)"
                          }},
                          // Add more questions in a similar format as needed
                       ]
                    }}

                    Each question should have a unique title, appropriate tags, a concise description, and a clear stem with answer choices.
                    Remember to follow the additional information provided for designing true or false questions, and ensure that the question is well-crafted to effectively assess students' knowledge.
                    '''

    elif question_type == "sa":
        prompt = f'''
                    I want you to act as highly experienced {level} professor with expertise in the subject matter covered in the uploaded document.

                    Write 100 short answer questions for an upcoming college test based on the uploaded document. The question should be unique, clear, and challenging enough to test their problem-solving and reading comprehension skills. Make sure it aligns with the content of the document.

                    Steps to complete:
                    1. Carefully review the uploaded document to understand its content thoroughly.
                    2. Identify a specific topic or concept from the document that you want to assess.
                    3. Craft a short answer question that relates to the chosen topic or concept. Ensure the question is not vague and provides clear instructions.
                    4. Specify the correct answer to the question.
                    5. Consider the verbs you use in the question to match the intended learning outcome and guide students in their response.
                    6. Delimit the scope of the question to prevent unrelated responses.

                    Write a 100 true or false questions that assesses students' understanding of the document's content..

                    Format Output: The output should be in JSON format, follow this template:

                    {{
                       "title": "Unique Title",
                       "tags": ["Genres", "Difficulty", "Topics", "Level", "Question-Type", "Many More"],
                       "description": "Short and Engaging Description",
                       "questions": [
                          {{
                             "question": "Question Stem?",
                             "answer": "Correct answer to the question."
                          }},
                          // Add more questions in a similar format as needed
                       ]
                    }}

                    Each question should have a unique title, appropriate tags, a concise description, and a clear stem with answer choices.
                    Remember to follow the additional information provided for designing short answer questions, and ensure that the question is well-crafted to effectively assess students' knowledge.
                    '''
    elif question_type == "fitb":
        prompt = f'''
                    I want you to act as highly experienced {level} professor with expertise in the subject matter covered in the uploaded document.

                    Write 100 fill-in-the-blank questions for a college-level test based on the uploaded document. Each question should exercise students' problem-solving and reading comprehension skills. The questions should not repeat, be easy to understand, and yet challenging.

                    Steps to complete:
                    1. Carefully review the uploaded document to identify key topics, concepts, and information that should be covered in the questions.
                    2. For each question, create a stem (the main part of the question) that fully describes the problem. Ensure that students could answer the question based on the stem alone, without looking at the answer choices.            
                    3. Include all relevant information in the stem and avoid repeating information in the answer choices. This will make the options easier to read and understand.            
                    4. Eliminate excessive wording and irrelevant information from the stem to avoid confusing students and wasting their time.            
                    5. Limit the number of answer choices to between four and five per question. Research suggests that this range is effective, and it's challenging to come up with plausible distractors beyond this range.            
                    6. Make sure there is only one correct answer per question. Avoid having multiple correct options where one is "more" correct than the others.            
                    7. Craft distractors (incorrect answer choices) that are appealing and plausible. If the distractors are too farfetched, students may easily identify the correct answer.            
                    8. Ensure that the answer choices do not repeat throughout the set of questions.

                    Write a 100 multiple-choice questions that cover the content of the uploaded document and adhere to the guidelines provided.

                    Format Output: The output should be in JSON format, follow this template:

                    {{
                       "title": "Unique Title",
                       "tags": ["Genres", "Difficulty", "Topics", "Level", "Question-Type", "Many More"],
                       "description": "Short and Engaging Description",
                       "questions": [
                          {{
                             "question": "Question Stem?",
                             "choices": ["Choice A", "Choice B", "Choice C", "Choice D"],
                             "answer": "Correct Choice"
                          }},
                          // Add more questions in a similar format as needed
                       ]
                    }}

                    Each question should have a unique title, appropriate tags, a concise description, and a clear stem with answer choices.
                    Remember to follow the additional information provided for designing fill-in-the-blank questions, and ensure that the question is well-crafted to effectively assess students' knowledge.
                    '''

    return prompt


def delete_conversation(claude_api, conversation_id):
    if conversation_id:
        claude_api.delete_conversation(conversation_id)


def set_error_message(error_message):
    return {
        "isError": True,
        "errorMessage": error_message
    }


def parse_json(response):
    try:
        start_index = response.find('{')
        end_index = response.rfind('}') + 1
        json_data = response[start_index:end_index]

        response = json.loads(json_data)

    except:
        json_data += ']}'

        response = json.loads(json_data)

    return response


@app.route("/generate", methods=['POST'])
def generate_mcq():
    cookie = request.args.get("cookie")
    question_type = request.args.get("question_type")
    level = request.args.get("level")

    f = request.files['file']
    f.save(secure_filename(f.filename))

    try:
        claude_api = Client(cookie)

    except:
        return jsonify(set_error_message("Client error, please try again later.")), 403

    try:
        prompt = get_prompt(question_type, level)
        conversation_id = claude_api.create_new_chat()['uuid']
        response = claude_api.send_message(prompt, conversation_id, attachment=f.filename, timeout=600)

    except:
        delete_conversation(claude_api, conversation_id)
        return jsonify(set_error_message("Conversation or attachment error, please try again.")), 403

    try:
        response = parse_json(response)

    except:
        delete_conversation(claude_api, conversation_id)
        return jsonify(set_error_message("Parsing JSON error, please try again.")), 403

    delete_conversation(claude_api, conversation_id)

    return jsonify(response), 201


if __name__ == "__main__":
    app.run(debug=True)
