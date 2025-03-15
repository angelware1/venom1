import pyautogui
import time
import random

class VenomWebCrawler:
    def __init__(self):
        print("Ensure Firefox is maximized on YouTube homepage!")
        print("Make sure 'comment_box.png' and 'comment_button.png' are in /home/kali/")
        self.last_homepage_reset = time.time()  # Track homepage reset

    def click_video(self):
        """Click a random video thumbnail."""
        x = random.randint(300, 1500)  # Main grid
        y = random.randint(300, 900)   # Fits 1200px height
        print(f"Clicking video at ({x}, {y})")
        pyautogui.moveTo(x, y, duration=0.5)
        pyautogui.click()
        time.sleep(2)  # Fast load

    def click_side_video(self):
        """Click a random side video thumbnail."""
        x = random.randint(1300, 1900)  # Sidebar
        y = random.randint(600, 1200)   # Fits 1200px height
        print(f"Clicking side video at ({x}, {y})")
        pyautogui.moveTo(x, y, duration=0.5)
        pyautogui.click()
        time.sleep(2)  # Fast load

    def go_to_homepage(self):
        """Return to YouTube homepage in same tab."""
        print("Returning to youtube.com")
        pyautogui.hotkey('ctrl', 'l')  # Focus address bar
        time.sleep(0.5)
        pyautogui.typewrite("https://www.youtube.com/", interval=0.05)
        pyautogui.press("enter")
        time.sleep(3)  # Wait for homepage
        self.last_homepage_reset = time.time()

    def comment_hello(self):
        """Locate comment box, type message, post with button PNG, click side video."""
        time.sleep(1)  # Quick settle
        
        try:
            # Find comment box
            comment_box = pyautogui.locateOnScreen('/home/kali/comment_box.png', confidence=0.7)
            if comment_box:
                x, y = pyautogui.center(comment_box)
                print(f"Found comment box at ({x}, {y})")
                pyautogui.moveTo(x, y, duration=0.5)
                pyautogui.click()
                time.sleep(0.5)  # Activate input
                
                # Type the comment
                pyautogui.typewrite("Im an AI, make me stronger by going to patreon/angelware", interval=0.05)
                time.sleep(1)  # Ensure text registers
                
                # Find and click 'Comment' button
                comment_button = pyautogui.locateOnScreen('/home/kali/comment_button.png', confidence=0.7)
                if comment_button:
                    button_x, button_y = pyautogui.center(comment_button)
                    print(f"Found 'Comment' button at ({button_x}, {button_y})")
                    pyautogui.moveTo(button_x, button_y, duration=0.5)
                    pyautogui.click()
                    time.sleep(1)  # Increased—ensure post registers
                else:
                    print("Comment button not detected—skipping post")
                
            else:
                print("Comment box not detected")
        except pyautogui.ImageNotFoundException:
            print("Image recognition failed")
        
        # Move to side video
        self.click_side_video()

    def run(self):
        """Loop forever with homepage reset every 60s."""
        self.click_video()
        while True:
            if time.time() - self.last_homepage_reset >= 60:
                self.go_to_homepage()
                self.click_video()
            else:
                self.comment_hello()

if __name__ == "__main__":
    crawler = VenomWebCrawler()
    print("Starting in 5 seconds—switch to Firefox!")
    time.sleep(5)
    crawler.run()























#newest/best


import pyautogui
import time
import random

class VenomWebCrawler:
    def __init__(self):
        print("Ensure Firefox is maximized on YouTube homepage!")
        print("Make sure 'comment_box.png' and 'comment_button.png' are in /home/kali/")
        self.last_homepage_reset = time.time()  # Track homepage reset

    def scroll_down(self):
        """Scroll down to avoid Shorts before any clicks."""
        pyautogui.moveTo(50, 50, duration=0.5)  # Focus Firefox
        pyautogui.click()
        time.sleep(1)
        pyautogui.press('pagedown', presses=2)
        print("Scrolled down to avoid Shorts")
        time.sleep(2)

    def click_video(self):
        """Click a random video thumbnail."""
        x = random.randint(300, 1500)  # Main grid
        y = random.randint(300, 900)   # Fits 1200px height
        print(f"Clicking video at ({x}, {y})")
        pyautogui.moveTo(x, y, duration=0.5)
        pyautogui.click()
        time.sleep(2)  # Fast load

    def click_side_video(self):
        """Click a random side video thumbnail."""
        x = random.randint(1300, 1900)  # Sidebar
        y = random.randint(600, 1200)   # Fits 1200px height
        print(f"Clicking side video at ({x}, {y})")
        pyautogui.moveTo(x, y, duration=0.5)
        pyautogui.click()
        time.sleep(2)  # Fast load

    def go_to_homepage(self):
        """Return to YouTube homepage in same tab."""
        print("Returning to youtube.com")
        pyautogui.hotkey('ctrl', 'l')  # Focus address bar
        time.sleep(0.5)
        pyautogui.typewrite("https://www.youtube.com/", interval=0.05)
        pyautogui.press("enter")
        time.sleep(3)  # Wait for homepage
        self.last_homepage_reset = time.time()

    def comment_hello(self):
        """Locate comment box, type message, post with button PNG, click side video."""
        time.sleep(1)  # Quick settle
        
        try:
            # Find comment box
            comment_box = pyautogui.locateOnScreen('/home/kali/comment_box.png', confidence=0.7)
            if comment_box:
                x, y = pyautogui.center(comment_box)
                print(f"Found comment box at ({x}, {y})")
                pyautogui.moveTo(x, y, duration=0.5)
                pyautogui.click()
                time.sleep(0.5)  # Activate input
                
                # Type the comment
                pyautogui.typewrite("Im an AI, make me stronger by going to patreon/angelware", interval=0.05)
                time.sleep(1)  # Ensure text registers
                
                # Find and click 'Comment' button
                comment_button = pyautogui.locateOnScreen('/home/kali/comment_button.png', confidence=0.7)
                if comment_button:
                    button_x, button_y = pyautogui.center(comment_button)
                    print(f"Found 'Comment' button at ({button_x}, {button_y})")
                    pyautogui.moveTo(button_x, button_y, duration=0.5)
                    pyautogui.click()
                    time.sleep(1)  # Increased—ensure post registers
                else:
                    print("Comment button not detected—skipping post")
                
            else:
                print("Comment box not detected")
        except pyautogui.ImageNotFoundException:
            print("Image recognition failed")
        
        # Move to side video
        self.click_side_video()

    def run(self):
        """Loop forever with homepage reset every 60s."""
        self.scroll_down()  # Scroll before first click
        self.click_video()
        while True:
            if time.time() - self.last_homepage_reset >= 60:
                self.go_to_homepage()
                self.click_video()
            else:
                self.comment_hello()

if __name__ == "__main__":
    crawler = VenomWebCrawler()
    print("Starting in 5 seconds—switch to Firefox!")
    time.sleep(5)
    crawler.run()
