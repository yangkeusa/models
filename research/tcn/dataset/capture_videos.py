#!/usr/local/opt/python/libexec/bin/python

from datetime import datetime
import numpy as np
import cv2
import getopt
import sys
import threading
import time

def single_camera_capture(idx, barrier, capture, timer, max_frames):
    """ Capture the videos in a thread
    Args:
      idx: the index of the thread/camera
      barrier: a Barrier object to synchronize all the threads to start
      b_end: a Barrier object to synchronize all the threads to end
      capture: a video capture object
      timer: used for synchronization
      max_frames: exit after this man frames have been captured
    """
    print("Thread %d starts..." % idx)
    print("Warming up [idx=%d]..." % idx)
    barrier.wait()
    print("Starting [idx=%d" % idx)
    start = time.time()
    end = time.time()
    elapsed = end - start
    print("Thread %d finished: total time = %f" %(idx, elapsed))
    pass

def mt_capture(num_cameras, fps, duration):
    barrier = threading.Barrier(num_cameras + 1, timeout=10)
    caps = [cv2.VideoCapture(i) for i in range(num_cameras)]
    threads = list()
    for i in range(num_cameras):
        t = threading.Thread(target=single_camera_capture, args=(i, barrier, caps[i], None, 10))
        threads.append(t)
        t.start()
    barrier.wait()
    print("Starting all threads!")
    for t in threads:
        t.join()
    print("All threads finished");
    for i in range(num_cameras):
        caps[i].release()
    print("ALL DONE")

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
