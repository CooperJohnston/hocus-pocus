import math
import os
import heapq
from PIL import Image
import numpy as np
from datetime import datetime

time_offscreen = 0
counter = 1
previousGaze = None
previousDistances = []

# userTextFile = "User_Data/MADDY_TEST_DATA.txt"

def distance(p1, p2):
    return math.sqrt(((p2[0] - p1[0]) ** 2) + ((p2[1] - p1[1]) ** 2))

def focus_score(student_stare, file_name, image, username):

    userTextFile = f'User_Data/{username}_EXTRA_DATA.txt'

    global previousDistances
    global previousGaze
    global time_offscreen

    if not os.path.exists(userTextFile):
        with open(userTextFile, "w") as user_write:
            user_write.write("Start file\n")


    min_dist = None
    min_word_coords = (0, 0)
    curr_word = None
    closest_words = []
    min_word_ranking = None
    with open(file_name, 'r') as important:
        heads = important.readline()
        rank = 0
        for line in important.readlines():
            elms = line.split(',')
            curr_coord = (int(elms[0]), int(elms[1]))
            curr_dist = distance(curr_coord, student_stare)
            if curr_word != elms[2]:
                rank += 1
                curr_word = elms[2]
            
            if min_dist == None or curr_dist < min_dist:
                min_dist = curr_dist
                min_word_coords = curr_coord
                min_word_ranking = rank
            
            heapq.heappush(closest_words, (-curr_dist, rank, curr_coord))
            if len(closest_words) > 5:
                heapq.heappop(closest_words)

    top_average = 0
    for (curr_dist, rank, curr_coord) in closest_words:
        # print(-curr_dist, rank)
        top_average += rank
    top_average /= 5
    # print(top_average)


    # The following should possibly help determine
    good_words = ['Inbox', 'Dashboard', 'Canvas', 'Info', 'Help', 'Courses', 'Calendar', 'Account', 'History', 'Announcements']
    bad_words = ['youtube', 'Squidward', 'snail', 'rick']
    all_curr_words = []
    reading = False
    with open("LOC_ACTUAL.csv", "r") as all:
        heads = all.readline()
        for line in all.readlines():
            elms = line.split(',')
            all_curr_words.append(elms[0])
            cCoord = (int(elms[1]), int(elms[2]))
            if distance(cCoord, student_stare) <= 175:
                reading = True

    canvas_words_count = 0
    canvas_words = []
    canvas_bad_words = []
    for w in good_words:
        if w in all_curr_words:
            # print(f"GOOD WORD: {w}")
            canvas_words_count += 1
            canvas_words.append(w)
    for w in bad_words:
        if w in all_curr_words:
            # print(f"BAD WORD: {w}")
            canvas_words_count -= 1
            canvas_bad_words.append(w)

    if ("Dashboard" in canvas_words or "Account" in canvas_words) and not canvas_bad_words:
        onCanvas = True
    elif canvas_words_count > 5:
        onCanvas = True
    else:
        onCanvas = False
    # print(canvas_words_count)
    # print(onCanvas)

    prevAvg = None
    if previousGaze:
        previousDistances.append(distance(previousGaze, student_stare))
    if len(previousDistances) > 5:
        previousDistances.pop(0)
        prevAvg = np.average(previousDistances)


    if student_stare[0] < 20 or student_stare[0] > image.width - 20 or student_stare[1] < 20 or student_stare[1] > image.height - 20:
        # Need to figure out how much to take from focus score for not even looking at the screen.
        # Not looking at screen could indicate lack of focus but also could indicate listening to instructions.
        # How long the student has been looking away? Like a timer thing
        # Could multiply by factor depending on how often THIS program grabs student gaze
        time_offscreen += 1
    elif prevAvg and not reading and prevAvg <= 215:
        time_offscreen += 1
    elif prevAvg and reading and prevAvg <= 175:
        time_offscreen += 1
    else:
        # global time_offscreen
        if time_offscreen > 10:
            time_offscreen //= 2
        elif time_offscreen - 5 > 0:
            time_offscreen -= 5
        else:
            time_offscreen = 0
    
    focus_score = 0
    if min_word_ranking:
        if (top_average < max(7, rank//2) or min_word_ranking <= max(5, rank // 10)) and min_dist <= 1000:  
            focus_score += 40
        elif (top_average < min(10, rank) or min_word_ranking <= max(7, rank//4)) and min_dist <= 1000: 
            focus_score += 30
        elif reading:
            focus_score += 25
        else:
            #penalize words from 20 onwards
            focus_score += (.625 - min_word_ranking/max(20, (rank//4)+1)) * 40
    else:
        if onCanvas:
            focus_score += 40
        else:
            focus_score += 20

    if onCanvas:
        focus_score += 50 # this should be about half of the points

    

    focus_score += (10 - 4 * time_offscreen)
    

    # if min_dist > 125:
    #     focus_score *= np.exp(-((min_dist-125)/125)**2)
    # if min_dist > 250:
    #     focus_score *= np.exp(-((min_dist-250)/250))

    # print(f'\nStudent gaze: {student_stare}\nClosest word: {min_word_coords}\nDistance: {min_dist}\nWord ranking: {min_word_ranking}\nTop avg ranking: {top_average}\nTime offscreen: {time_offscreen}\nOn canvas: {onCanvas}\nCanvas words :{canvas_words}\n{focus_score}\n\n')


    global counter
    if counter == 1:
         counter = 2
    elif counter == 2:
        counter = 1
        with open(userTextFile, "a") as user_write:
            user_write.write(f'Date & Time: {datetime.now()}\nStudent gaze: {student_stare}\nClosest word: {min_word_coords}\nDistance: {min_dist}\nWord ranking: {min_word_ranking}\nTop avg ranking: {top_average}\nPrevious Gaze: {previousGaze}\nPrevious Distances: {previousDistances}\nPrevious Gazes Distance Average: {prevAvg}\nTime offscreen: {time_offscreen}\nOn canvas: {onCanvas}\nCanvas words :{canvas_words}\nReading: {reading}\n{focus_score}\n\n')
                
    previousGaze = student_stare

    return focus_score, min_word_coords, time_offscreen, onCanvas



# focus_score((2081, 41), 'FINAL_ACTUAL.csv', Image.open('screenshot.png'))