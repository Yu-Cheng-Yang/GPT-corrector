import os
import streamlit as st
from docx import Document
import openai
from openai import OpenAI

# Initialize OpenAI API client
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Please set the OPENAI_API_KEY environment variable.")
client = OpenAI(api_key=api_key)
def read_word_file(file):
    document = Document(file)
    full_text = []
    for para in document.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def get_openai_feedback(text,operation,style):
    prompt_map = {
        "Formal": { "Feedback": f'Analyze the following text for its adherence to formal writing standards. Does it maintain a professional and structured tone? Provide comprehensive feedback and areas of improvement as much as possible.Try to avoid a full correction unless the following text is short. Also do not regurgitate the input text. : "{text}"',
                        "Reformulate": f"Translate the following text into a formal style. Ensure it's professionally structured, avoids colloquial language, and maintains precision: \"{text}\"",
                        "Correction": f"Refine this text to uphold formal writing conventions. Address any informalities, ambiguities, and ensure it projects a professional tone: \"{text}\""
                   },
        "Informal": {"Feedback": f'Evaluate this text for its informal tone. Does it feel relaxed and casual? Offer feedback on its conversational flow and usage of colloquialisms as much as possible.Try to avoid a full correction unless the following text is short.Also do not regurgitate the input text.: "{text}"',
                        "Reformulate": f"Turn the following text into a casual, relaxed piece. Feel free to use colloquial language and maintain a friendly tone: \"{text}\"",
                        "Correction": f"Adjust this text to sound more informal. If any parts feel too stiff or formal, relax them for a more laid-back feel: \"{text}\""
                     },
        "Conversational": {
            "Feedback": f'Evaluate this text based on its conversational tone. Does it sound like natural dialogue? Provide detailed feedback and suggestions. Also do not regurgitate the input text.: "{text}"',
            "Reformulate": f"Transform the following text to sound like a casual chat or discussion. Make it feel more like a spoken conversation: \"{text}\"",
            "Correction": f"Adjust the following text to adhere to conversational norms. Ensure it sounds natural and uses colloquial language where appropriate: \"{text}\""
                        },

        "Narrative": {
            "Feedback": f'Critique the narrative elements of this text: pacing, character development, plot coherence, and setting. Provide detailed feedback and suggestions for improvement as much as possible.Try to avoid a full correction unless the following text is short. Also do not regurgitate the input text.: "{text}"',
            "Reformulate": f"Turn the following text into a captivating narrative. Consider introducing a setting, characters, or a plot twist: \"{text}\"",
            "Correction": f"Adjust the following text to better fit narrative conventions, such as enhancing descriptions, ensuring consistent character voices, and improving the flow: \"{text}\""
                        },

        "Persuasive": {
            "Feedback": f'Evaluate this text for its persuasiveness. Does it present strong arguments, evidence, and appeal to the reader? Provide detailed feedback as much as possible.Try to avoid a full correction unless the following text is short.Also do not regurgitate the input text.: "{text}"',
            "Reformulate": f"Transform the following text to present a compelling argument. Use persuasive techniques to convince the reader: \"{text}\"",
            "Correction": f"Adjust the following text to enhance its persuasive elements. Strengthen any weak arguments and clarify the main point: \"{text}\""
                        },

        "Expository": {
            "Feedback": f'Assess this text for its clarity and informativeness. Does it explain the topic thoroughly without bias? Offer feedback and suggestions as much as possible.Try to avoid a full correction unless the following text is short. Also do not regurgitate the input text.: "{text}"',
            "Reformulate": f"Rephrase the following text to clearly and objectively explain the topic. Ensure it's factual and straightforward: \"{text}\"",
            "Correction": f"Modify the text to better fit expository standards. Ensure clarity, accuracy, and a neutral tone: \"{text}\""
                        },


    }

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a professional English teacher asked to review the following word document."},
            {"role": "user", "content": prompt_map[style][operation]}
        ]
    )
    feedback = response.choices[0].message.content

    return feedback


def get_elaboration(text):
    response = client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[
            {"role": "system", "content": "You are a high school English professor asked to review the following word document."},
            {"role": "user", "content": text},
            {"role": "user", "content": "Can you say more about that?"}
        ]
    )
    return response.choices[0].message.content

def question(text):
    response = client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[
            {"role": "system", "content": "You are a high school English professor asked to review the following word document."},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content
st.title("GrammarGPT")

uploaded_file = st.file_uploader("Upload Word document", type=["docx"])
operation = st.radio("Select operation", ["Correction","Reformulate", "Feedback"])
style = st.radio("Select Feedback Style", ["Formal", "Informal","Conversational","Narrative", "Persuasive", "Expository"])
if uploaded_file is not None:
    text = read_word_file(uploaded_file)
    st.write("Uploaded Text:")
    st.write(text)

    feedback = get_openai_feedback(text, operation, style)
    st.write("Feedback from ChatGPT:")
    st.write(feedback)
    # Buttons for "Say More" and asking custom questions
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Ask ChatGPT to Say More"):
            elaboration = get_elaboration(feedback)
            st.write(elaboration)
    with col2:
        user_question = st.text_input("Ask ChatGPT a question:")
        if st.button("Submit Question"):
            if user_question:
                answer = question(user_question)
                st.write(answer)
            else:
                st.warning("Please enter a question first.")