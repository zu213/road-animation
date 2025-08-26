import shutil
import random
import math
import json
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
  
  def do_OPTIONS(self):
    # Handle CORS preflight requests
    self.send_response(200)
    self.send_header("Access-Control-Allow-Origin", "*")
    self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
    self.send_header("Access-Control-Allow-Headers", "Content-Type")
    self.end_headers()
    return
  
  def do_GET(self):
    frames = self.compile_road_animation()
    response = json.dumps(frames)

    self.send_response(200)
    self.send_header("Content-type", "application/json")
    self.send_header("Access-Control-Allow-Origin", "*") 
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
        
  def draw_frame_of_road(self, initialFrame, height, center, interval, foliage):
    thirdHeight = height // 3
    frame = initialFrame[:]
    foliageLeft = foliage[0]
    foliageRight= foliage[1]
    
    # Draw the road below the mountains
    for i in range(thirdHeight, height):
      row = ""

      # If in middle third we do a bar every 3 otherwise we do two then two spaces
      if i < thirdHeight * 2:
        bar = (i > thirdHeight) and ((i - interval) % 3 == 0)
      else:
        bar = (i - (interval + 1)) % 4 in (0, 1)
      
      # Populate row with tree
      if i < 2 * thirdHeight:
        if foliage[0][0] == 1 and foliage[0][1] == i:
          row += " " * (foliage[0][2] - i + thirdHeight) + "@" + " " * (center - 4 - foliage[0][2]) + "." + " " * (2 + i - thirdHeight)
        elif foliage[0][0] == 2 and foliage[0][1] == i:
          row += " " * (foliage[0][2] - i + thirdHeight - 1) + "@" + " " * (center - 3 - foliage[0][2]) + "." + " " * (2 + i - thirdHeight)
        elif foliage[0][0] == 2 and foliage[0][1] == i - 1:
          row += " " * (foliage[0][2] - i + thirdHeight) + "|" + " " * (center - 4 - foliage[0][2]) + "." + " " * (2 + i - thirdHeight)
        else:
          row += " " * (center - 3 - i + thirdHeight) + "." + " " * (2 + i - thirdHeight)
      else:
        if foliage[0][0] == 1 and foliage[0][1] == i:
          row += " " * (foliage[0][2] - i + thirdHeight) + "@@" + " " * (center - 5 - foliage[0][2]) + "." + " " * (2 + i - thirdHeight)
        elif foliage[0][0] == 2 and (foliage[0][1] == i):
          row += " " * (foliage[0][2] - i - 1 + thirdHeight) + "@@" + " " * (center - 4 - foliage[0][2]) + "." + " " * (2 + i - thirdHeight)
        elif foliage[0][0] == 2 and (foliage[0][1] == i - 1):
          row += " " * (foliage[0][2] - i + thirdHeight) + "@@" + " " * (center - 5 - foliage[0][2]) + "." + " " * (2 + i - thirdHeight)
        elif not i < 2 * thirdHeight + 1 and foliage[0][0] == 2 and foliage[0][1] == i - 2:
          row += " " * (foliage[0][2] - i + thirdHeight + 1) + "|" + " " * (center - 5 - foliage[0][2]) + "." + " " * (2 + i - thirdHeight)
        else:
          row += " " * (center - 3 - i + thirdHeight) + "." + " " * (2 + i - thirdHeight)
      
      
      row += "|" if bar else " "
      row += " " * (2 + i - thirdHeight) + "."
      
      if i < 2 * thirdHeight:
        if foliage[1][0] == 1 and foliage[1][1] == i:
          row += " " * (foliage[1][2]) + "@"
        elif foliage[1][0] == 2 and foliage[1][1] == i:
          row += " " * (foliage[1][2]) + "@"
        elif foliage[1][0] == 2 and foliage[1][1] == i - 1:
          row += " " * (foliage[1][2] - 1) + "|"
      else:
        if foliage[1][0] == 1 and foliage[1][1] == i:
          row += " " * (foliage[1][2]) + "@@"
        elif foliage[1][0] == 2 and (foliage[1][1] == i):
          row += " " * (foliage[1][2]) + "@@"
        elif foliage[1][0] == 2 and (foliage[1][1] == i - 1):
          row += " " * (foliage[1][2] - 1) + "@@"
        elif  not i < 2 * thirdHeight + 1 and foliage[1][0] == 2 and foliage[1][1] == i - 2:
          row += " " * (foliage[1][2] - 1) + "|"
      
      frame.append(row)

    return frame
  
  def colour_frame(self, frame, thirdHeight):
    newFrame = []
    for i in range(0, len(frame)):
      currentRow = frame[i]
      newRow = ''
      colour = 'white' if i < 3 else 'blue'
      for j in range(0, len(currentRow)):
        currentChar = currentRow[j]
        if currentChar == '\n' or currentChar == ' ':
          newRow += currentChar
        elif i < thirdHeight and (currentChar == '/' or currentChar == '\\' or currentChar == '-' or currentChar == '|'):
          newRow += ('<span style="color:' + colour + '">' + currentChar + '</span>')
        elif currentChar == '/' or currentChar == '\\' or currentChar == '|':
          newRow += ('<span style="color:white">' + currentChar + '</span>')
        else:
          newRow += currentChar
      newFrame.append(newRow)
        
    return newFrame
    

  def compile_road_animation(self):
    frames = []
    width, height = shutil.get_terminal_size((80, 24))
    pos = 0
    initialFrame = self.append_mountains(height//3, width - 1)
    initialFrame.append("-" * (width - 1))

    # left and right tree's or bushes, one at a time
    foliage = [[0, 0, 0], [0, 0, 0]]
    # get 60 frames
    for _ in range(60):
      # get current frame
      if foliage[0][0] == 0 and random.randint(1, 8) == 8:
        foliage[0] = [random.randint(1, 2), height - 1, random.randint(width //4, width // 3)]
      elif foliage[1][0] == 0 and random.randint(1, 8) == 8:
        foliage[1] = [random.randint(1, 2), height - 1, random.randint(width //4, width // 3)]
      frame = self.draw_frame_of_road(initialFrame, height, width // 2, pos % 3, foliage)
      colouredFrame = self.colour_frame(frame, height // 3)
      for i in range(0, len(foliage)):
        if foliage[i][0] != 0:
          foliage[i][1] -= 1
        if foliage[i][1] <= height // 3 - 1:
          foliage[i] = [0,0,0]
      # animate
      pos = (pos + 1) % height
      frames.append("\n".join(colouredFrame))
        
    return frames

#if __name__ == "__main__":
#  print(handler().compile_road_animation()[5])