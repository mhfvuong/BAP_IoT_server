
class Preprocessing:
    def __init__(self):
        self.process_func = {'Temperature': self.divide, 'Humidity': self.divide, 'Audio': self.average_audio}
        self.audio_total = 0
        self.audio_samples = 0

    def divide(self, data):
        data = float(data)/100
        return data

    def average_audio(self, data):
        self.audio_total += int(data)
        self.audio_samples += 1
        if self.audio_samples >= 10:
            audio_average = self.audio_total/self.audio_samples
            self.audio_total = 0
            self.audio_samples = 0
            return audio_average
