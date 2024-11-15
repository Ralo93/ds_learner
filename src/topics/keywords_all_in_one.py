import json
import os
import logging
import networkx as nx
import openai
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from PyPDF2 import PdfReader
import spacy

# Load config and set OpenAI API key
with open(r"../config.json", "r") as file:
    config = json.load(file)
openai_api_key = config["openai"]["api_key"]
os.environ["OPENAI_API_KEY"] = openai_api_key

# Load English stopwords and SpaCy model
stop_words = set(stopwords.words("english"))
nlp = spacy.load("en_core_web_sm")

class PDFProcessor:
    def extract_text(self, file_path: str) -> str:
        logging.info(f"Extracting text from PDF: {file_path}")
        reader = PdfReader(file_path)
        text = "".join(page.extract_text() for page in reader.pages)
        logging.info("Text extraction complete.")
        return text

class KeywordExtractor:
    def preprocess(self, text: str) -> list:
        tokens = word_tokenize(text.lower())
        return [word for word in tokens if word.isalnum() and word not in stop_words]

    def extract_tfidf_keywords(self, tokens: list, num_keywords: int = 20) -> dict:
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([" ".join(tokens)])
        feature_names = vectorizer.get_feature_names_out()
        scores = zip(feature_names, tfidf_matrix.toarray()[0])
        return dict(sorted(scores, key=lambda x: x[1], reverse=True)[:num_keywords])

    def extract_ner_keywords(self, text: str) -> list:
        doc = nlp(text)
        return [ent.text for ent in doc.ents if len(ent.text.split()) > 1]

class ExplanationGenerator:
    @staticmethod

    def generate_explanation(keyword: str, context: str) -> str:
        """Generate explanation for a keyword using OpenAI's API."""
        prompt = (
            f"Explain the keyword '{keyword}' based on the following context from a scientific paper:\n\n"
            f"{context}\n\n"
            "Provide a concise and clear explanation suitable for someone with a basic understanding of the topic."
        )

        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.7
            )
            explanation = response.choices[0].message.content.strip()
            logging.info(f"Generated explanation for '{keyword}': {explanation}")
            return explanation
        except Exception as e:
            logging.error(f"Error generating explanation for '{keyword}': {e}")
            return "No explanation available."


    @staticmethod
    def filter_keywords(keywords: list, labels: list) -> list:
        prompt = (
            f"Filter this list so only scientific expressions remain, basically keywords: '{keywords}'"
            "Provide a filtered list which only contains expressions which are conceptual and represent or might represent a topic, filter out all gibberish."
            "Be aware that new expressions could be introduced, but they usually have some relation to the provided context. E.g. 'Label Smooting' is a new concept, wheras names of people and numbers are not."
        )
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.0
            )
            return response['choices'][0]['message']['content'].strip().split(", ")
        except Exception as e:
            logging.error(f"Error filtering keywords '{keywords}': {e}")
            return keywords

def main(pdf_path: str):
    processor = PDFProcessor()
    text = processor.extract_text(pdf_path)

    extractor = KeywordExtractor()
    tokens = extractor.preprocess(text)
    tfidf_keywords = extractor.extract_tfidf_keywords(tokens)
    ner_keywords = extractor.extract_ner_keywords(text)

    labels = ["machine learning", "artificial intelligence", "deep learning"]
    filtered_keywords = ExplanationGenerator.filter_keywords(ner_keywords, labels)

    generator = ExplanationGenerator()
    for keyword in filtered_keywords:
        context = " ".join([sentence for sentence in text.split('.') if keyword.lower() in sentence.lower()][:3])
        explanation = generator.generate_explanation(keyword, context)
        print(f"Keyword: {keyword}\nExplanation: {explanation}\n")

        #TODO insert into database


def text_to_json(input_file, output_file):
    """
    Converts a text file with 'Keyword' and 'Explanation' pairs into a JSON file.
    
    Args:
        input_file (str): Path to the input text file.
        output_file (str): Path to the output JSON file.
        
    Returns:
        None
    """
    data = []
    with open(input_file, 'r') as file:
        lines = file.readlines()
        
    current_entry = {}
    for line in lines:
        line = line.strip()
        if line.startswith("Keyword:"):
            # If there's an existing entry, save it first
            if current_entry:
                data.append(current_entry)
            current_entry = {"Keyword": line[len("Keyword:"):].strip()}
        elif line.startswith("Explanation:"):
            if current_entry is not None:
                current_entry["Explanation"] = line[len("Explanation:"):].strip()
    
    # Append the last entry
    if current_entry:
        data.append(current_entry)
    
    with open(output_file, 'w') as json_file:
        json.dump(data, json_file, indent=4)




if __name__ == "__main__":
    #main(r"C:\Users\rapha\repositories\learning_cards\data\attention_is_all_you_need_cropped.pdf")
    text_to_json(r"C:\Users\rapha\repositories\learning_cards\data\keywords\keywords.txt", r"C:\Users\rapha\repositories\learning_cards\data\keywords\output.json")