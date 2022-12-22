from pathlib import Path

class Logger():
    def __init__(self):
        self.usuariosLogFilePath = str(Path(__file__).parents[1]) + 'logs/usuariosLog.txt'
        self.vendasLogFilePath = str(Path(__file__).parents[1]) + 'logs/vendasLog.txt'

    def log(self, message, usuarioInfo=True, vendaInfo=False):
        message = message + "\n"
        if vendaInfo:
            with open(self.vendasLogFilePath, "a") as writer:
                writer.write(message)
        else:
            with open(self.usuariosLogFilePath, "a") as writer:
                writer.write(message)

        writer.close()