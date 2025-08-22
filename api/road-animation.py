import time
import shutil
import sys
import random
import math
import json
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
  
  def do_GET(self):
        frames = self.compile_road_animation()
        response = json.dumps(frames)

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(response.encode("utf-8"))
        return

  def append_mountains(self, thirdHeight, width):
    frame = [""] * thirdHeight
    mountainAngle = thirdHeight / (width / 4)
    charLeft = ''
    charRight = ''
    if mountainAngle < 0.4:
      charLeft = '-'
      charRight = '-'
    elif mountainAngle < 0.9:
      charLeft = '/'
      charRight = '\\'
    else:
      charLeft = '|'
      charRight = '|'
    
    currentHeight = thirdHeight - 1
    goingUp = True
    
    for _ in range(0, width):
      rowPainted = False
      for j in range(0, thirdHeight):
        if not rowPainted and j == math.floor(currentHeight):
          rowPainted = True
          if (not goingUp and j == thirdHeight - 1) or (goingUp and j == 0) or random.randint(1, 8) == 8:
            goingUp = not goingUp
          if goingUp:
            frame[j] += charLeft
            currentHeight -= mountainAngle
          else:
            frame[j] += charRight
            currentHeight += mountainAngle
        else:
          frame[j] += " "
    
    return frame
        
  def draw_frame_of_road(self, initialFrame, height, thirdHeight, center, interval):
      
    frame = initialFrame[:]
    
    # Draw the road below the mountains
    for i in range(thirdHeight, height):
      row = ""

      # If in middle third we do a bar every 3 otherwise we do two then two spaces
      if i < thirdHeight * 2:
        bar = (i > thirdHeight) and ((i - interval) % 3 == 0)
      else:
        bar = (i - (interval + 1)) % 4 in (0, 1)
      
      # Populate row
      row += " " * (center - 3 - i + thirdHeight) + "." + " " * (2 + i - thirdHeight)
      row += "|" if bar else " "
      row += " " * (2 + i - thirdHeight) + "."
      
      frame.append(row)

    return frame

  def compile_road_animation(self):
    frames = []
    width, height = shutil.get_terminal_size((80, 24))
    pos = 0
    initialFrame = self.append_mountains(height//3, width - 1)
    initialFrame.append("-" * (width - 1))

    # get 60 frames
    for _ in range(60):
      # get current frame
      frame = self.draw_frame_of_road(initialFrame, height, height // 3, width // 2, pos % 3)
      # animate
      pos = (pos + 1) % height
      frames.append("\n".join(frame))
        
    return frames
