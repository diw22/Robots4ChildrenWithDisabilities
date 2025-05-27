import pygame
import time
from collections import deque

class MorseCodeTranslator:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((640, 240))
        pygame.display.set_caption("Morse Code Translator")

        self.font = pygame.font.Font(None, 36)
        self.clock = pygame.time.Clock()

        self.press_time = 0
        self.input_buffer = deque()
        self.last_input_time = time.time()
        self.output_text = ""
        self.running = True

        self.dot_dash_threshold = 0.3
        self.letter_idle_threshold = 1.0
        self.word_idle_threshold = 2.0

        self.morse_dict = {
            '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
            '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
            '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
            '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
            '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
            '--..': 'Z', '.----': '1', '..---': '2', '...--': '3',
            '....-': '4', '.....': '5', '-....': '6', '--...': '7',
            '---..': '8', '----.': '9', '-----': '0',
            '.-.-.-': '.', '--..--': ',', '..--..': '?', '-.-.--': '!'
        }

    def translate_buffer(self):
        morse_code = ''.join(self.input_buffer)
        return self.morse_dict.get(morse_code, '?')

    def update_display(self):
        self.screen.fill((30, 30, 30))
        current = ''.join(self.input_buffer)

        buffer_text = self.font.render(f"Current: {current}", True, (200, 200, 200))
        output_rendered = self.font.render(f"Output: {self.output_text}", True, (0, 255, 0))

        self.screen.blit(buffer_text, (20, 50))
        self.screen.blit(output_rendered, (20, 100))
        pygame.display.flip()

    def run(self):
        print("Hold SPACE for dot or dash")
        print("Idle 1s: new letter | Idle 2s: space")
        while self.running:
            now = time.time()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.press_time = time.time()

                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        duration = time.time() - self.press_time
                        self.last_input_time = time.time()
                        if duration < self.dot_dash_threshold:
                            self.input_buffer.append('.')
                        else:
                            self.input_buffer.append('-')

            idle_time = time.time() - self.last_input_time

            if self.input_buffer and idle_time >= self.letter_idle_threshold:
                letter = self.translate_buffer()
                self.output_text += letter
                self.input_buffer.clear()
                self.last_input_time = time.time()

            elif idle_time >= self.word_idle_threshold:
                if self.output_text and not self.output_text.endswith(' '):
                    self.output_text += ' '
                    self.last_input_time = time.time()

            self.update_display()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    MorseCodeTranslator().run()
