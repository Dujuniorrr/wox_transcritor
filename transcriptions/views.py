from django.shortcuts import render
import speech_recognition as sr
import spacy
from wordcloud import WordCloud
from nltk import FreqDist
# import matplotlib.pyplot as plt
from textblob import TextBlob
import subprocess
import os
from pathlib import Path
import hashlib

BASE_DIR = Path(__file__).resolve().parent.parent

MEDIA_ROOT =  os.path.join(BASE_DIR, 'files')

import secrets

def generate_random_hash(length=32):
    # Gera uma sequência hexadecimal aleatória com o comprimento especificado
    random_hash = secrets.token_hex(length)
    
    return random_hash

def convert_mp3_to_wav(input_file, output_file):
    # Verifica se o arquivo de saída já existe
    file_exists = os.path.exists(output_file)
    
    # Se o arquivo de saída já existir, gera um nome diferente
    if file_exists:
        file_hash = generate_random_hash()
        file_name, file_ext = os.path.splitext(output_file)
        output_file = f"{file_name}_{file_hash}{file_ext}"
    
    # Converte o arquivo de MP3 para WAV usando o FFmpeg
    subprocess.run(['ffmpeg', '-i', input_file, output_file])
    
    return output_file

def home(request):
    
    if request.method == "POST":
        if 'audio' not in request.FILES:
            return render(request, "transcriptions/home.html", { 'error' : 'Nenhum arquivo de áudio foi enviado.'})

        file = request.FILES['audio']
        # Verificar se o arquivo possui uma extensão suportada
        if file.name == '':
            return render(request, "transcriptions/home.html", { 'error' : 'Nenhum arquivo selecionado.'})

        allowed_extensions = {'mp3', 'mp4', 'wav'}
        if not file.name.lower().rsplit('.', 1)[-1] in allowed_extensions:
            return render(request, "transcriptions/home.html",{ 'error' : 'Formato de arquivo não suportado.'})

        # Salvar o arquivo de áudio temporariamente
        audio_path = os.path.join(MEDIA_ROOT, file.name)
        audio_wav_path = os.path.join(MEDIA_ROOT, file.name + ".wav") 
        
        with open(audio_path, 'wb') as destination:
            # Salve o arquivo no disco
            for chunk in file.chunks():
                destination.write(chunk)
                
        audio_wav_path = convert_mp3_to_wav(audio_path, audio_wav_path)
        
        # Inicializa o objeto de reconhecimento de fala
        r = sr.Recognizer()

        # Carrega o modelo do spaCy para o idioma português
        nlp = spacy.load('pt_core_news_sm')

        with sr.AudioFile(audio_wav_path) as source:
            print("Analisando audio...")
            audio = r.record(source)
            try:
                text = r.recognize_google(audio, language='pt-BR')
                print("Transcrição: ", text)

                # Processa a transcrição utilizando o spaCy
                doc = nlp(text)

                print("\n")
                for token in doc:
                    print("Token: ", token.text)
                    print("Lema: ", token.lemma_)
                    print("Categoria gramatical: ", token.pos_)
                    print("Dependência sintática: ", token.dep_)
                    
                # Cria uma lista de tokens, excluindo as stopwords
                tokens = [token.text for token in doc if not token.is_stop]

                # Calcula a frequência dos termos
                fdist = FreqDist(tokens)

                # Define os pesos personalizados
                weights = {term: freq for term, freq in fdist.items()}
                
                print("\n")
                print(weights)
                # Cria a WordCloud com pesos personalizados
                wordcloud = WordCloud(font_path=os.path.join(BASE_DIR, "static/fonts/DejaVuSans.ttf"), prefer_horizontal=0.9,  width=800, height=400, max_words=50, background_color='white', colormap='Oranges', normalize_plurals=False, random_state=42).generate_from_frequencies(weights)

                # Plota a WordCloud
                # plt.imshow(wordcloud, interpolation='bilinear')
                # plt.axis("off")
                # plt.show()

                wordcloud.to_file(os.path.join(BASE_DIR, "static/wordclouds/wordcloud.png"))
                
                # Realiza a análise de sentimentos no texto transcritos
                sentiment = TextBlob(text).sentiment
                print("\nAnálise de Sentimentos:")
                print("Polaridade: ", sentiment.polarity)
                print("Subjetividade: ", sentiment.subjectivity)

                # Determina o resultado da polaridade
                if sentiment.polarity > 0:
                    polaridade_resultado = "positiva"
                elif sentiment.polarity < 0:
                    polaridade_resultado = "negativa"
                else:
                    polaridade_resultado = "neutra"

                # Determina o resultado da subjetividade
                if sentiment.subjectivity > 0.5:
                    subjetividade_resultado = "subjetiva"
                else:
                    subjetividade_resultado = "objetiva"

                print("Resultado da análise:")
                print("A polaridade do texto é", polaridade_resultado)
                print("A subjetividade do texto é", subjetividade_resultado)

                return render(request, "transcriptions/informations.html", {"transcription" : text, "doc" : doc, "frequency" : weights})
              
            except sr.UnknownValueError:
                print("Não foi possível reconhecer a fala")
            except sr.RequestError as e:
                print("Erro durante a transcrição: {0}".format(e))
            
    return render(request, "transcriptions/home.html")
