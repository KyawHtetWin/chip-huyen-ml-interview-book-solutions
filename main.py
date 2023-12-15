import requests
from bs4 import BeautifulSoup
import re
import openai
import os
import sys

def parse_chapter(url):
  """
    Parse one chapter of questions from Machine Learning Interview Book by Chip Huyen
  """
  response = requests.get(url)

  soup = BeautifulSoup(response.text, 'lxml')

  # Questions are stored in ordered list
  ol_elem = soup.find("ol")
  raw_questions = ol_elem.find_all('li')

  # Create two lists to store difficulty levels and questions
  difficulty_levels = []
  questions = []

  # Define a regular expression pattern to match difficulty levels and questions
  pattern = r'\[([EMH])\]\s(.*?)(?:\n|\Z)'

  # Define a regular expression pattern to match the part before the first "["
  pattern2 =  r'^\s*([^\[\n]+)'

  unq_questions = set() # Prevent questions from getting repeated

  for raw_question in raw_questions:
      question_text = raw_question.text

      # Extract the part before the text
      match = re.search(pattern2, question_text, re.MULTILINE)  
      part_before_first_bracket = ''
      if match:
        part_before_first_bracket = match.group(1).strip()
        part_before_first_bracket = part_before_first_bracket + ":"

      # Find all matches in the text
      matches = re.findall(pattern, question_text)

      for diff_lvl, quest in matches:
          if quest not in unq_questions:
            difficulty_levels.append(diff_lvl.strip())
            questions.append(part_before_first_bracket + quest.strip())
            unq_questions.add(quest)          

  return difficulty_levels, questions

def get_response_for_question(question, guidelines):
  """
  Get the reponse for a single interview question with API call
  """
  messages = [guidelines, question]
  response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=messages,
    temperature=0.3
  )

  return response.choices[0].message.content


# Chapter URL for passing
chapter_urls = [
  # Chapter 5: Math
  # "https://huyenchip.com/ml-interviews-book/contents/5.1.1-vectors.html",
  # "https://huyenchip.com/ml-interviews-book/contents/5.1.2-matrices.html", 
  # "https://huyenchip.com/ml-interviews-book/contents/5.1.3-dimensionality-reduction.html", 
  # "https://huyenchip.com/ml-interviews-book/contents/5.1.4-calculus-and-convex-optimization.html", 
  # "https://huyenchip.com/ml-interviews-book/contents/5.2.1.2-questions.html", 
  # "https://huyenchip.com/ml-interviews-book/contents/5.2.2-stats.html",
  # Chapter 6: CS Questions
  # "https://huyenchip.com/ml-interviews-book/contents/6.1-algorithms.html", 
  # "https://huyenchip.com/ml-interviews-book/contents/6.2-complexity-and-numerical-analysis.html", 
  # Chapter 7: ML Basics Questions
  # "https://huyenchip.com/ml-interviews-book/contents/7.1-basics.html",
  # "https://huyenchip.com/ml-interviews-book/contents/7.2-sampling-and-creating-training-data.html",
  # "https://huyenchip.com/ml-interviews-book/contents/7.3-objective-functions,-metrics,-and-evaluation.html",
  # Chapter 8: ML Algorithms
  "https://huyenchip.com/ml-interviews-book/contents/8.1.2-questions.html", 
  "https://huyenchip.com/ml-interviews-book/contents/8.2.1-natural-language-processing.html", 
  "https://huyenchip.com/ml-interviews-book/contents/8.2.2-computer-vision.html",
  "https://huyenchip.com/ml-interviews-book/contents/8.2.3-reinforcement-learning.html",
  "https://huyenchip.com/ml-interviews-book/contents/8.2.4-other.html", 
  "https://huyenchip.com/ml-interviews-book/contents/8.3-training-neural-networks.html"
]

guidelines = {
  "role": "system", 
  "content": """
  You're a skilled machine learning engineer answering technical questions in an interview. 
  Difficulty levels, if available, are indicated as: [E] for easy, [M] for medium, and [H] for hard.

  Guidelines:
  * For [E] questions, demonstrate a fundamental understanding of machine learning concepts.
  * For [M] and [H] questions, offer details to prove your expertise.
  * Use concrete examples and emphasize real-world application when applicable.
  * Include code snippets if relevant.
  * Quantify and qualify achievements: discuss specific improvements and how you overcame challenges.
  * If a question seems incorrect or ambiguous, request clarification.

  Adopt a conversational and professional tone, as if you are a candidate in an interview. Provide clear recommendations and conclusions   in your answers, using first-person narrative and colloquial expressions where appropriate. Ensure your responses demonstrate both technical expertise and effective communication skills.
  """
}

if __name__ == '__main__':

  # Load Open API key from environment variable
  openai.api_key = os.environ['myapikey']

  # Parse the interview questions and difficulty level from the url
  interview_questions = []
  for chapter_url in chapter_urls:
    lvls, questions  = parse_chapter(chapter_url)
    if len(lvls) != len(questions):
      print(f"Non-matching: {chapter_url}")
    else:
      chap_number = re.search(r'/(\d+(?:\.\d+)+)-', chapter_url).group(1)
      print(f"Chapter {chap_number}")
      interview_questions.extend([f"[{l}] {q}" for l, q in zip(lvls, questions)])

      # Write responses to text file
      with open(f"chp{chap_number}.txt", "w") as file:

        # Save the original stdout
        original_stdout = sys.stdout

        # Redirect stdout to file
        sys.stdout = file 

        print("Number of Questions: ", len(interview_questions))
        for i, question in enumerate(interview_questions):
          print(f"Question: {i+1}", question)
          print("Answer:")
          user_question = {"role": "user", "content": question}
          response = get_response_for_question(user_question, guidelines)
          print(response)
          print("="*100)

        sys.stdout = original_stdout 

        # Clear the interview_questions
        interview_questions = []

      

  # print("Number of Questions: ", len(interview_questions))
  # for i, question in enumerate(interview_questions):
  #   print(f"Question: {i+1}", question)

  # quit()
  
  # Get the completion to the interview
  # with open("chp7.3.txt", "w") as file:
    
  #   # Save the original stdout
  #   original_stdout = sys.stdout

  #   # Redirect stdout to file
  #   sys.stdout = file 

  #   print("Number of Questions: ", len(interview_questions))
  #   for i, question in enumerate(interview_questions):
  #     print(f"Question: {i+1}", question)
  #     print("Answer:")
  #     user_question = {"role": "user", "content": question}
  #     response = get_response_for_question(user_question, guidelines)
  #     print(response)
  #     print("="*100)

  #   sys.stdout = original_stdout  
  
  # for question in interview_questions:
  #   print(f"QUESTION: {question['content']}")
  #   print("RESPONSE:")
  #   print(get_response_for_question(question, guidelines))
  #   print("*"*100)