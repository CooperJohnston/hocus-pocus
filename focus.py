import math
import os
time_offscreen = 0
counter = 1

def distance(p1, p2):
    return math.sqrt(((p2[0] - p1[0]) ** 2) + ((p2[1] - p1[1]) ** 2))

def focus_score(student_stare, file_name, image):
# dummy variable for student gaze
    if not os.path.exists("User_Data/MADDY_TEST_DATA.txt"):
        with open("User_Data/MADDY_TEST_DATA.txt", "w") as user_write:
            user_write.write("Start file\n")

    # I would like to calculate the distance between where the student is looking and where the student should be looking (words)
    # Should be doing this every once in a while, but not all the time
    # words = []
    min_dist = None
    # min_word = None
    min_word_coords = (0, 0)
    curr_word = None
    with open(file_name) as important:
        heads = important.readline()
        rank = 1
        for line in important.readlines():
            elms = line.split(',')
            # words.append(elms[0])
            curr_coord = (int(elms[0]), int(elms[1]))
            curr_dist = distance(curr_coord, student_stare)
            if curr_word == None:
                curr_word = elms[2]
            elif curr_word != elms[2]:
                rank += 1
                curr_word = elms[2]
            
            if min_dist == None or curr_dist < min_dist:
                min_dist = curr_dist
                # min_word = elms[0]
                min_word_coords = curr_coord
                min_word_ranking = rank
            

    # print(f"min_dist: {min_dist}\nmin_word_coords: {min_word_coords}\nmin_word_ranking: {min_word_ranking}")
    # The closest important word is saved. Will that be more helpful to Jade? Nevertheless, it can be used to help determine the focus.
    # ... but how?
    # Also the rank is to figure out if the student is looking at the most important word. Should that be used as a weight or as a separate measurement altogether?

    # Also want to check if the student is looking at the screen


    #REMOVED OFF SCREEN UNTIL GAZE CAN BE FIGURED OUT
    if student_stare[0] < 20 or student_stare[0] > image.width - 20 or student_stare[1] < 20 or student_stare[1] > image.height - 20:
        # Need to figure out how much to take from focus score for not even looking at the screen.
        # Not looking at screen could indicate lack of focus but also could indicate listening to instructions.
        # How long the student has been looking away? Like a timer thing
        # Could multiply by factor depending on how often THIS program grabs student gaze
        global time_offscreen
        time_offscreen += 1
    else:
        time_offscreen = 0

    # print(f"time_offscreen: {time_offscreen}")
    # Also want to score based on if the student is scrolling or not... but I'm not yet sure how that is/will be measured


    # The following should possibly help determine
    canvas_words = ['Inbox', 'Dashboard', 'Canvas', 'Info', 'Help']
    bad_words = ['youtube', 'Squidward', 'snail', 'rick']
    all_curr_words = []
    with open("LOC_ACTUAL.csv", "r") as all:
        heads = all.readline()
        for line in all.readlines():
            elms = line.split(',')
            all_curr_words.append(elms[0])

    canvas_words_count = 0
    for w in canvas_words:
        if w in all_curr_words:
            print(f"GOOD WORD: {w}")
            canvas_words_count += 1
    for w in bad_words:
        if w in all_curr_words:
            print(f"BAD WORD: {w}")
            canvas_words_count -= 1

    if canvas_words_count > 2:
        onCanvas = True
    else:
        onCanvas = False
    # print(canvas_words_count)
    # print(onCanvas)

    # 1 / Ranking to get some sort of decimal based on if the student is looking near the most important word(s) ((MAX 1 scaled by 2))
    # 1 - distance/1000 To see how close to the word(s) a student is ((MAX 1))
    # 1 - timeoffscreen/10 (or however many seconds we want to have be the determining factor lol) ((MAX 1 scaled by 3))
    # Add the boolean of whether or not the student is on canvas ((1 or 0) scaled by 10) (should probably be scaled up/down)

    # focus_score = ((1 / min_word_ranking) * 2) + (1 - (min_dist / 1000)) + ((1 - (time_offscreen / 10)) * 3) + (onCanvas * 10)
    focus_score = ((1 / min_word_ranking) * 2) + ((1 - (min_dist / 1000)) * 4) + (onCanvas * 10)
    # print(f"\nFINAL SCORE: {focus_score}")
    print(f"Student gaze: {student_stare}")
    print(f"Closest word: {min_word_coords}")
    print(f"Word ranking result: {(1 / min_word_ranking)} * 2")
    print(f"Gaze to word result (high means close): {1 - (min_dist / 1000)} * 4")
    print(f"Time offscreen: {(1 - (time_offscreen / 10))} * 3")
    print(f"On canvas: {onCanvas} * 10")
    print(f"{(focus_score / 16) * 100}\n")
    focus_score = (focus_score / 16) * 100
    # global counter
    # if counter == 1:
    #      counter = 2
    # elif counter == 2:
    #     counter = 1
    #     with open("User_Data/MADDY_TEST_DATA.txt", "a") as user_write:
    #                     user_write.write(f'Student gaze: {student_stare}\nClosest word: {min_word_coords}\nWord ranking result: {(1 / min_word_ranking)} * 2\nGaze to word result (high means close): {1 - (min_dist / 1000)} * 4\nTime offscreen: {(1 - (time_offscreen / 10))} * 3\nOn canvas: {onCanvas} * 10\n{focus_score}\n\n')
                

    # rank is how I kept track of how many words there. Indexed on 1 haha so it's an actual count
    return focus_score, min_word_coords, rank
