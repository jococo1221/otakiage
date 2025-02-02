# This file will script the overarching journey of the seeker (player) through the journey (game)
# It will call the other files and functions to create the game
# It will also be the main file that will be run to start the game

# Importing the necessary files
# leaving blank for now, will fill in later


# Defining the main function

def main():
    # This function will be the main function that will run the game
    # The seeker will have a companion device that will guide them through the journey
    
    # Before the game starts, the device will be idle
    # In this mode, it can accomplish some generic functions, like controlling the room light
 
    device.idle()

    # The device will be waiting for the start tag to be detected

    # This loop will run until the start tag is detected

    while not device.journey_started():
        device.scan() # The device scan for RFID tags
        
        # Arm the device
        # If the device detects the start tag, it will go into "armed" mode, else it will stay idle
        if device.detect_start_tag():
            device.armed()
            break
        # After the device is armed, when the start tag stops being detected, the journey will start
        # The device will go into "journey" mode
        device.journey()=True # This will start the journey

        if device.journey():
            # The journey has started
            # call the journey function

            journey()



# Defining the journey function

def journey():
    
    # JOURNEY INTRO
    # When the journey starts, the intro sequence will play
    # The intro sequence will be a sound and light show that will introduce the seeker to the journey

    # Send commands to the lighting system to play the intro sequence
    lights.intro()
    # The device will play the intro sequence
    device.audio_play("intro")
    
    # When the intro is completed, the device will ask the seeker to choose a path
    
    # CHOOSE A PATH
    # Setting the device to "prompt" mode will play the prompt sound and light sequence
    device.prompt()
    device.audio_play("prompt")
    # Set the light system to "prompt" mode
    lights.prompt()


    # The user will be asked to choose a path, by scanning one of the presented tags
    # Depending on the path chosen, the user will be taken to the respective path

    # Waits for the seeker to choose a path
    # If the tag matches "object09", "object10" or "object16", the seeker will be taken to the respective path
    # If the tag does not match any of the above, the device will prompt the seeker to scan again
    while not device.path_chosen():
        device.scan()
        if device.scanned_tag() == "object09":
            path09()
        if device.scanned_tag() == "object10":
            path10()
        if device.scanned_tag() == "object16":
            path16()

        # If the tag does not match any of the above, the device will prompt the seeker to scan again
        else:
            device.prompt()
            lights.prompt()


# Defining the path01 function

def path09():
    # This function will be called when the seeker chooses path09 - The hermit's path
    # The path will be a series of challenges that the seeker will have to complete to reach the end of the path
    # As a simple example, this path will ask the seeker to look for one tag and scan it to complete the challenge

    # The device will play the path01 intro sequence
    device.mode("intro")
    device.audio_play("path01_intro")


    # The seeker will be presented with the first challenge
    # The device will play the challenge sound and light sequence
    device.mode("prompt")
    device.audio_play("challenge01")

    # The seeker will have to complete the challenge to move forward
    # The device will wait for the seeker to complete the challenge
    while not device.challenge01_completed():
        device.scan()
        if device.scanned_tag() == "object01":
            # If the seeker scans the correct tag, the challenge will be completed
            device.feedback("success")
            device.audio_play("challenge01_completed")
            break
        else:
            # If the seeker scans the wrong tag, the device will prompt the seeker to scan again
            device.feedback("retry")
            device.audio_play("challenge01_failed")


    # The seeker has completed the challenge
    # The device will play the path09 outro sequence
    device.mode("outro")
    device.audio_play("path09_outro")



# Defining the path16 function

def path16():
    # This function will be called when the seeker chooses path16 - La maison dieu
    # This path will be about catharsis

    # The device will play the path16 intro sequence
    device.mode("intro")
    device.audio_play("path16_intro")
    
    # The seeker will be asked to go to a destination
    device.mode("prompt")
    device.audio_play("path16_prompt")
    # The seeker will have to scan the tag of the destination to know they are ready to begin the actual challenge
    while not device.challenge16_completed():
        device.scan()
        if device.scanned_tag() == "object16":
            # If the seeker scans the correct tag, they will be ready to begin the challenge
            device.feedback("success")
            device.audio_play("path16_destination") 
            break
        else:
            # If the seeker scans the wrong tag, the device will prompt the seeker to scan again
            device.feedback("retry")
            device.audio_play("challenge16_retry")
    
    # The seeker has reached the destination
    # The device will play the path16 challenge sequence
    device.mode("challenge")
    device.audio_play("path16_challenge")
    lights.challenge()

    # The seeker will have to complete the challenge to move forward
    # The device will wait for the seeker to complete the challenge  
    while not device.challenge16_completed():
        if lights.challenge_completed():
            # If the seeker completes the challenge, the device will play the path16 outro sequence
            device.mode("outro")
            lights.mode("outro")
            device.audio_play("path16_outro")
        else:
            #if the timer reaches 30 seconds without completing the challenge, the device will play the path16 failure sequence
            if device.timer() >= 30:
                device.mode("failure")
                lights.mode("failure")
                device.audio_play("path16_failure")



    
