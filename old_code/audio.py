import numpy as np
import sounddevice as sd

# Parameters
duration = 0.1  # Duration of each audio frame in seconds
sample_rate = 44100  # Change this to a supported sample rate
blocksize = 1024  # Buffer size

def estimate_volume(data):
    # Compute root mean square (RMS) of the audio signal
    rms = np.sqrt(np.mean(data**2))
    # Convert RMS to dB
    volume_db = 20 * np.log10(rms)
    # Map dB to a range (0, 100)
    volume = np.interp(volume_db, [-60, 0], [0, 100])
    return volume

def main():
    device_name = "USB PnP Sound Device"  # Replace with your microphone's name
    with sd.InputStream(device=device_name, callback=callback, channels=1, samplerate=sample_rate, blocksize=blocksize):
        while True:
            pass

def callback(indata, frames, time, status):
    if status:
        print(status)
    volume = estimate_volume(indata.flatten())
    print(f"Volume: {int(volume/10)}")

if __name__ == "__main__":
    main()
