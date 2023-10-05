from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from claude_api import Client
import json
import re

app = Flask(__name__)


@app.route("/upload", methods=['POST'])
def upload():
    cookie = request.args.get("cookie")

    f = request.files['file']
    f.save(secure_filename(f.filename))

    try:
        claude_api = Client(cookie)

    except:
        return jsonify(
            {
                "isError": True,
                "errorMessage": "Client error, please try again later."
            }
        ), 403

    try:
        prompt = '''
            I want you to act as highly experienced College Professor with expertise in the subject matter covered in the uploaded document.

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
            
            {
               "title": "Unique Title",
               "tags": ["Genres", "Difficulty", "Topics", "Level", "Question-Type", "Many More"],
               "description": "Short and Engaging Description",
               "questions": [
                  {
                     "question": "Question Stem?",
                     "choices": ["Choice A", "Choice B", "Choice C", "Choice D"],
                     "answer": "Correct Choice"
                  },
                  // Add more questions in a similar format as needed
               ]
            }
            
            Each question should have a unique title, appropriate tags, a concise description, and a clear stem with answer choices.
            Remember to follow the additional information provided for designing multiple-choice questions, and ensure that the question is well-crafted to effectively assess students' knowledge.
            '''

        conversation_id = claude_api.create_new_chat()['uuid']
        response = claude_api.send_message(prompt, conversation_id, attachment=f.filename, timeout=600)

    except:
        if conversation_id:
            claude_api.delete_conversation(conversation_id)

        return jsonify(
            {
                "isError": True,
                "errorMessage": "Conversation or attachment Error, please try again later."
            }
        ), 403

    try:
        start_index = response.find('{')
        end_index = response.rfind('}') + 1
        json_data = response[start_index:end_index]

        json_data = re.sub(r"'(.*?)'", lambda x: x.group(0).replace('"', "XxMisMatCheDxX"), json_data)
        matches = re.findall(r"'(.*?)'", json_data)

        for match in matches:
            if "XxMisMatCheDxX" in match:
                json_data = json_data.replace(f"'{match}'", f'"{match}"')
            else:
                json_data = json_data.replace("'<", '"<').replace(">'", '>"')

        matches1 = re.findall(r"'(.*?)'", json_data)
        matches2 = re.findall(r'"(.*?)"', json_data)

        for match1 in matches1:
            isFound = False
            for match2 in matches2:
                if f"'{match1}'" in match2:
                    isFound = True
                    break

            if not isFound:
                json_data = json_data.replace(f"'{match1}'", f'"{match1}"')

        json_data = json_data.replace("XxMisMatCheDxX", "'")

    except:
        if conversation_id:
            claude_api.delete_conversation(conversation_id)

        return jsonify(
            {
                "isError": True,
                "errorMessage": "Converting JSON failed, please try again later."
            }
        ), 403

    try:
        response = json.loads(json_data)

    except:
        json_data += ']}'
        response = json.loads(json_data)

    return jsonify(response), 201


if __name__ == "__main__":
    app.run(debug=True)
