import pygame

# Initialize Pygame mixer
print("Initializing Pygame mixer...")
pygame.mixer.init()
print("Pygame mixer initialized.")

def play_sound(file_path, volume=1.0):
    print(f"Playing sound: {file_path}")
    sound = pygame.mixer.Sound(file_path)
    sound.set_volume(volume)
    sound.play()

play_sound("/home/pi/otakiage/drop.wav", 0.5)

# Keep the script running to allow sound to play
import time
time.sleep(5)
