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
    
    frame = self.append_sun(frame, width)
    
    return frame
  
  def check_covered(self, mountains, i, charPos):
    covered = False
    for j in range(0,i + 1):
      if(mountains[j][charPos] != " "):
        covered = True
    return covered
  
  
  def append_sun(self, mountains, width, radius = 4):
    if(len(mountains) < radius): return mountains
    
    currentWidth = radius + 2
    halfWidth = width // 2
    
    for i in range(0,radius):
      leftCovered = False
      rightCovered = False
      
      copiedLine = mountains[i]
      charPos = halfWidth - currentWidth + 1
      
      leftCovered = self.check_covered(mountains, i, charPos)
      rightCovered = self.check_covered(mountains, i, charPos + 2 * currentWidth - 1)
      
      newLine = copiedLine[:charPos]
      if leftCovered:
        newLine += copiedLine[charPos]
      else:
        newLine += '0'
        
      modifier = 0
        
      if i == radius - 1:
        if not self.check_covered(mountains, i, charPos + 1):
          newLine += '0'
        else:
          newLine += copiedLine[charPos + 1]
        if not self.check_covered(mountains, i, charPos + 2):
          newLine += '0'
        else:
          newLine += copiedLine[charPos + 2]
        if not self.check_covered(mountains, i, charPos + 3):
          newLine += '0'
        else:
          newLine += copiedLine[charPos + 3]
          
      elif i == radius - 2:
        modifier = -2
        if not self.check_covered(mountains, i, charPos + 1):
          newLine += '0'
        else:
          newLine += copiedLine[charPos + 1]
        newLine += copiedLine[charPos + 2:charPos + 2 * currentWidth - 1]
        if not self.check_covered(mountains, i, charPos + 6):
          newLine += '0'
        else:
          newLine += copiedLine[charPos + 6]
        currentWidth -= 1
      else:
        newLine += copiedLine[charPos + 1:charPos + 2 * currentWidth]
      
      
      if rightCovered:
        newLine += copiedLine[charPos + 2 * currentWidth - 1]
      else :
        newLine += '0'
        
      newLine += copiedLine[charPos + 2 * currentWidth - modifier:]
      mountains[i] = newLine
      currentWidth -= 1
      
    currentWidth = radius + 2
    for i in range(0,radius):
      newLine = " " * (halfWidth - currentWidth + 1)
      newLine += "0"
      
      if i == radius - 1:
        newLine += "0" * 3
      elif i == radius - 2:
        newLine += "0"
        newLine += " " * (currentWidth * 2 - 3)
        newLine += "0"
        currentWidth -= 1
      else:
        newLine += " " * (currentWidth * 2 - 1)
      
      newLine += "0"
      mountains.insert(0, newLine)
      currentWidth -= 1
      
    return mountains
    
        
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
    width, height = shutil.get_terminal_size((80, 30))
    height = height - 4 #reserve some space for the sun
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
