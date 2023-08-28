# Librerías
from gpt4all import GPT4All

# Importar modelo
model = GPT4All("C:\\Users\\pjrio\\AppData\\Local\\nomic.ai\\GPT4All\\nous-hermes-13b.ggmlv3.q4_0.bin")

output = model.generate("Me podrías ayudar a hacer un programa de Python para contar de 10 en 10 hasta 1500?")
print(output)
