import speech_recognition as sr
import datetime

# Inicializar o reconhecedor
r = sr.Recognizer()

# Capturar áudio do microfone em tempo real e realizar a transcrição
def capturar_audio():
    with sr.Microphone() as source:
        print("Diga algo...")
        while True:
            audio = r.listen(source, phrase_time_limit=6)
            try:
                text = r.recognize_google(audio, language='pt-BR')
                print("Transcrição:", text)

                # Salvar a transcrição em um arquivo .txt
                with open("transcricao.txt", "a", encoding="utf-8") as file:
                    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")
                    file.write(timestamp + text + '\n')
                    print("Transcrição salva no arquivo transcricao.txt")
            except sr.UnknownValueError:
                print("Não foi possível reconhecer a fala")
            except sr.RequestError as e:
                print("Erro durante a transcrição; {0}".format(e))

# Executar a função de captura de áudio
capturar_audio()


