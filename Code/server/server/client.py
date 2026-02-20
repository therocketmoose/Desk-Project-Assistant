import socket
import speech_recognition as sr
import edge_tts
import pygame
import asyncio
import keyboard 
import os
import sys
import time
import winsound

# --- CONFIGURATION ---
SERVER_IP = '127.0.0.1' 
SERVER_PORT = 65433
VOICE = "en-US-GuyNeural" # <--- MALE VOICE

def log_event(msg):
    with open("client_debug_log.txt", "a") as f:
        f.write(f"{msg}\n")

async def speak(text):
    print(f"[AI] Speaking...")
    output_file = "reply.mp3"
    
    try:
        communicate = edge_tts.Communicate(text, VOICE)
        await communicate.save(output_file)
        
        # Wake up speakers every time
        try: pygame.mixer.quit()
        except: pass
        
        pygame.mixer.init(frequency=24000)
        pygame.mixer.music.load(output_file)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            if keyboard.is_pressed('q'):
                pygame.mixer.music.stop()
                break
            await asyncio.sleep(0.1)
            
        pygame.mixer.quit()
        try: os.remove(output_file)
        except: pass 
            
    except Exception as e:
        log_event(f"[AUDIO ERROR] {e}")

async def main():
    with open("client_debug_log.txt", "w") as f: f.write("--- START ---\n")
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((SERVER_IP, SERVER_PORT))
    except Exception as e:
        log_event(f"[CONNECT FAIL] {e}")
        return

    r = sr.Recognizer()
    r.dynamic_energy_threshold = True  
    r.pause_threshold = 0.8            

    try:
        # FORCE MIC ID 1 (Intel)
        with sr.Microphone(device_index=1, sample_rate=16000) as source:
            winsound.Beep(400, 200) # Beep
            print("[MIC] Calibrating...")
            try: r.adjust_for_ambient_noise(source, duration=1)
            except: pass
            winsound.Beep(800, 200) # Beep

            while True:
                print("[MIC] Listening...")
                try:
                    audio = r.listen(source, timeout=None)
                    
                    text = r.recognize_google(audio)
                    print(f"You: {text}")
                    
                    # --- INSTANT FEEDBACK LOGIC ---
                    # We speak BEFORE sending the data to the slow server
                    if "create" in text.lower() or "make" in text.lower():
                         # If creating files/folders, say this:
                        await speak("I am working on that now, sir.")
                    elif "bye" in text.lower():
                        pass
                    else:
                        # If asking a question, say this:
                        await speak("Just a moment, let me think.")

                    client_socket.send(text.encode())

                    if "bye" in text.lower():
                        await speak("Goodbye!")
                        break
                    
                    ai_response = client_socket.recv(4096).decode('utf-8')
                    await speak(ai_response)

                except sr.UnknownValueError:
                    pass
                except Exception as e:
                    log_event(f"[LOOP ERROR] {e}")
                    
    except Exception as e:
        log_event(f"[FATAL ERROR] {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        log_event(f"[MAIN ERROR] {e}")