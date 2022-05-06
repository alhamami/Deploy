import numpy as np
import cv2
import copy
from progress.bar import Bar
import os
import re

import numpy as np
import cv2
import copy
from progress.bar import Bar
import os
import re

def heatmap(videoPath, videoID):
    if(videoPath is None):
        return
    capture = cv2.VideoCapture(videoPath)
    background_subtractor = cv2.bgsegm.createBackgroundSubtractorMOG()
    fps = int(capture.get(cv2.CAP_PROP_FPS))
    length = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))

    bar = Bar('Processing Frames', max=length)

    first_iteration_indicator = 1
    for i in range(0, length):

        ret, frame = capture.read()
        if (frame is not None):
            print(frame.shape)
        
        # If first frame
        if frame is not None:	
            if first_iteration_indicator == 1:
                height, width = frame.shape[:2]
                accum_image = np.zeros((height, width), np.uint8)
                first_iteration_indicator = 0
            else:
                filter = background_subtractor.apply(frame)  # remove the background

                x = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))

                threshold = 1 #- (x / (1 - x))
                maxValue = 2 #- (x / (2 - x))
                ret, th1 = cv2.threshold(filter, threshold, maxValue, cv2.THRESH_BINARY)

                # add to the accumulated image
                accum_image = cv2.add(accum_image, th1)
                #cv2.imwrite('./mask.jpg', accum_image)

                color_image_video = cv2.applyColorMap(accum_image, cv2.COLORMAP_JET)

                video_frame = cv2.addWeighted(frame, 0.7, color_image_video, 0.7, 0)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        bar.next()

    bar.finish()

    #make_video('./frames/', './output.avi')

    background_frame = get_background(capture)
    color_image = cv2.applyColorMap(accum_image, cv2.COLORMAP_JET)
    result_overlay = cv2.addWeighted(background_frame, 0.7, color_image, 0.7, 0)

    # save the final heatmap
    cv2.imwrite("./static/images/{}.jpg".format(videoID), result_overlay)

    # cleanup
    capture.release()
    cv2.destroyAllWindows()
    return result_overlay

def get_background(video):
	FOI = video.get(cv2.CAP_PROP_FRAME_COUNT) * np.random.uniform(size=30)

	#creating an array of frames from frames chosen above
	frames = []
	for frameOI in FOI:
		video.set(cv2.CAP_PROP_POS_FRAMES, frameOI)
		ret, frame = video.read()
		frames.append(frame)
	#calculate the average
	backgroundFrame = np.median(frames, axis=0).astype(dtype=np.uint8)

	return backgroundFrame

def atoi(text):
    # A helper function to return digits inside text
    return int(text) if text.isdigit() else text


def natural_keys(text):
    # A helper function to generate keys for sorting frames AKA natural sorting
    return [atoi(c) for c in re.split(r'(\d+)', text)]

if __name__ == '__main__':
    heatmap(None, 0)
