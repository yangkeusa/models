#!/usr/local/opt/python/libexec/bin/python

from datetime import datetime
import numpy as np
import cv2
import getopt
import sys
import threading
import time

def single_camera_capture(idx, barrier, capture, frames, max_seconds):
    """ Capture the videos in a thread
    Args:
      idx: the index of the thread/camera
      barrier: a Barrier object to synchronize all the threads to start
      b_end: a Barrier object to synchronize all the threads to end
      capture: a video capture object
      frames: the list to store all the frames captured, 
          each element in the list should be a (timestamp, image) pair
      max_seconds: exit after this many seconds have elapsed
    """
    print("Thread %d starts..." % idx)
    print("Warming up [idx=%d]..." % idx)
    for i in range(5):
        print("Taking ramp img #%d for thread idx%d" % (i, idx))
        ret, frame = capture.read()
        print ("RET=", ret, "i=", i, "IDX=", idx)
        #cv2.imshow('frame', frame)
    print("Warm up done [idx=%d]" % idx)
    size = (int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v') # note the lower case
    vout = cv2.VideoWriter()
    file_name = 'output_%d.mov' % idx
    fps = 30
    success = vout.open(file_name, fourcc, fps, size, True)
    print("Videp Writer ready: idx=%d" % idx)
    barrier.wait()
    print("Starting [idx=%d]" % idx)
    start = time.time()
    num_frames = 0
    i = 0
    while(True):
        ret, frame = capture.read()
        now = time.time()
        frames.append((now, frame))
        print("TIME: %s Capture idx %d frame %d: ret = %d" % (str(datetime.now()), idx, i, ret))
        vout.write(frame) 
        num_frames = num_frames + 1
        if now > max_seconds + start:
            break;
        i = i + 1
    end = time.time()
    elapsed = end - start
    fps = float(num_frames) / float(elapsed)
    print("Thread %d finished: total time = %f, total frames = %d, FPS = %f" %
          (idx, elapsed, num_frames, fps))
    vout.release()
    pass

def mt_capture(num_cameras, fps, duration):
    barrier = threading.Barrier(num_cameras + 1, timeout=10)
    caps = [cv2.VideoCapture(i) for i in range(num_cameras)]
    frames = [list() for i in range(num_cameras)]
    threads = list()
    for i in range(num_cameras):
        t = threading.Thread(
            target=single_camera_capture,
            args=(i, barrier, caps[i], frames[i], duration))
        threads.append(t)
        t.start()
    # wait for keystroke
    input("Press a key to start")
    barrier.wait()
    print("Starting all threads!")
    for t in threads:
        t.join()
    print("All threads finished");
    for i in range(num_cameras):
        caps[i].release()
    print("ALL DONE")
    # print the frames
    #print(frames)
    # save the videos
    # for i in range(num_cameras):
    #     # Now try to save to a file
    #     cap = caps[i]
    #     size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    #     fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v') # note the lower case
    #     vout = cv2.VideoWriter()
    #     file_name = 'output_%d.mov' % i
    #     success = vout.open(file_name, fourcc, fps, size, True)
    #     if False and not success:
    #         raise Exception("Unable to open file %s to write" % file_name)
    #     for item in frames[i]:
    #         time_stamp, frame = item
    #         vout.write(frame) 
    #     vout.release()
    #     print("FILE %s done" % file_name)
    pass

def capture(num_cameras, fps, duration):
    """Captures the videos simultaneously.

    Args:
      num_cemeras: number of cameras.
      fps: frames per second
      duration: number of seconds to capture
    """
    caps = [cv2.VideoCapture(i) for i in range(num_cameras)]
    start = time.time()
    end = start + duration
    print ("All captures ready: time = ", start)
    while(True):
        for idx in range(num_cameras):
            cap = caps[idx]
            ret = cap.grab()
            if ret == 0:
                raise Exception("failed to grab for idx %d" % (idx))
            now = str(datetime.now())
            print("Captured for idx %d at time %s" % (idx, now))
        for idx in range(num_cameras):
            cap = caps[idx]
            ret, img = cap.retrieve()
            if ret == 0:
                raise Exception("failed to retrieve for idx %d" % (idx))
            now = str(datetime.now())
            print("Retrieved for idx %d at time %s" % (idx, now))
            cv2.imshow('frame %d' % idx, img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

def main(argv):
   num_cameras=1
   fps=24
   duration=10
   try:
      opts, args = getopt.getopt(
          argv,
          "n:f:d:",
          ["num_cameras=",
           "fps=",
           "duration=",
          ])
   except getopt.GetoptError:
      print('save.py -n <num_cameras>')
      sys.exit(2)
   for opt, arg in opts:
       if opt in ("-n", "--num_cameras"):
           num_cameras = int(arg)
       elif opt in ('-f', '--fps'):
           fps = int(arg)
       elif opt in ('-d', '--duration'):
           duration = int(arg)
       else:
           print("UNKNOWN OPT: ", opt)
           sys.exit(2)
   print('num_cameras=', num_cameras, "fps=", fps, "duration=", duration)
   #capture(num_cameras, fps, duration)
   mt_capture(num_cameras, fps, duration)

if __name__ == "__main__":
    main(sys.argv[1:])
    quit()
  
cap = cv2.VideoCapture(0)

fps = 15
#capSize = (1028,720) # this is the size of my source video
size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v') # note the lower case
vout = cv2.VideoWriter()
success = vout.open('output.mov', fourcc, fps, size, True)


while(cap.isOpened()):
    ret, frame = cap.read()
    if ret==True:
        #frame = cv2.flip(frame,0)

        # write the flipped frame
        #out.write(frame)
        vout.write(frame) 

        cv2.imshow('frame',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

# Release everything if job is finished
cap.release()
vout.release()
cv2.destroyAllWindows()
