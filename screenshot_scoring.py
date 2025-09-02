from PIL import Image
import pytesseract
import cv2
from keybert import KeyBERT
from keyphrase_vectorizers import KeyphraseCountVectorizer
import pandas as pd
from nltk.corpus import words
# import numpy as np

#LOL I just realized that this is not probably going to work on other devices lol that's going to be a problem
# pytesseract.pytesseract.tesseract_cmd = r"C:\Users\meglo\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

## This is just setting up input/output files
main_word = "ACTUAL"
# working_image = f"Screenshot Parsing/Course_Home_dummy.png"
csv_file = f"LOC_ACTUAL.csv"
# rect_jpg = f"outputs/LOC_{main_word.lower()}.jpg"
# heat_jpg = f"outputs/HEAT_{main_word.lower()}.jpg"
final_csv = f"FINAL_ACTUAL.csv"

def parseImage(working_image):
    #Open the image
    screenshot = Image.open(working_image)
    screenshot = screenshot.convert("RGB")

    #Grab text & image positions
    ocr_data = pytesseract.image_to_data(screenshot, output_type=pytesseract.Output.DICT)

    texts = ocr_data['text']
    positions = list(zip(ocr_data['left'], ocr_data['top'], ocr_data['width'], ocr_data['height']))
    # print(texts)

    img = cv2.imread(working_image)

    # Write to csv file and create rectangles image
    found_words = []
    just_words = []
    valid_words = set(words.words())
    for (text, (x, y, w, h)) in zip(texts, positions):
        # if text.strip() != '' and text != " " and (not any(ord(char) > 127 for char in text)) and (not '"' in text) and len(text) > 2:
        if text.lower() in valid_words and len(text) > 1:
            # cv2.putText(img, f"{text}", (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 0, 0), 2)
            # cv2.rectangle(img, (x,y), (x+w, y+h), (0,255,0), 2)
            found_words.append((text, x+(w//2), y+(h//2)))
            just_words.append(text)

    with open(csv_file, "w") as f:
        f.write("Word, X, Y\n")
        for word, x, y in found_words:
            f.write(f"{word.strip(',')}, {x}, {y}\n")

    string_words = ' '.join(just_words)
    # print(string_words)

    # cv2.imshow("Importance Scores", img)
    # cv2.imwrite(rect_jpg, img)
    # cv2.waitKey()

    #Importance scores!!
    try:
        kw_model = KeyBERT()
        keywords = kw_model.extract_keywords(docs=string_words, vectorizer = KeyphraseCountVectorizer())
        # print(keywords)

        dataframe = pd.read_csv(csv_file, on_bad_lines='skip')
        important_words = [(w,kw[1]) for kw in keywords for w in kw[0].split()]
        # print(important_words)

        #NEED TO SORT BY IMPORTANCE LOL
        important_words.sort(key=lambda x: x[1], reverse=True)

        # Create a dictionary to store the highest score for each word
        important_no_scores = []
        for word, score in important_words:
            if word not in important_no_scores:
                important_no_scores.append(word)
        # print(important_no_scores)
        # print(dataframe)

        #Create heatmap data stuff
        heatmap_data = []
        for word in important_no_scores:
            matches = dataframe[dataframe['Word'].str.lower() == word]
            # print(f"Matches for '{word}':\n", matches)
            for _, row in matches.iterrows():
                x = row.get(1)
                y = row.get(2)
                heatmap_data.append((x, y, word))
        # print(heatmap_data)

        ###COOPER, all of the coordinates of the "important" words are in the heatmap_data

        #Create actual heatmap
        # heatmap_img = cv2.imread(working_image)
        # heatmap = np.zeros_like(heatmap_img[:,:,0])

        # for (x,y) in heatmap_data:
        #     cv2.circle(heatmap, (x,y), radius=25, color=255, thickness=-1)

        # heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
        # overlay = cv2.addWeighted(heatmap_img, 0.7, heatmap, 0.3, 0)

        with open(final_csv, "w") as f:
            f.write("X, Y, Word\n")
            for (x,y,word) in heatmap_data:
                f.write(f"{x}, {y}, {word}\n")


        # cv2.imshow("Heatmap", overlay)
        # cv2.imwrite(heat_jpg, overlay)
        # cv2.waitKey()
    except ValueError as e:
        with open(final_csv, "w") as f:
            f.write("Word, X, Y\n")
            for word, x, y in found_words:
                f.write(f"{word.strip(',')}, {x}, {y}\n")