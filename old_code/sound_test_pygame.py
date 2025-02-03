import pygame

# Initialize Pygame mixer
pygame.mixer.init()

# Load and play an audio file
pygame.mixer.music.load("./test.wav")
pygame.mixer.music.play()

# Keep the script running while the music plays
while pygame.mixer.music.get_busy():
    pygame.time.Clock().tick(10)
