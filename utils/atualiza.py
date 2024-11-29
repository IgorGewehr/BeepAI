import os
import subprocess
import sys

def manage_main_files():
    """
    Gerencia a substituição de arquivos AppIA.exe.
    - Remove o arquivo AppIA_old.exe, se existir.
    - Renomeia AppIA.exe para AppIA_old.exe.
    - Renomeia AppIA_new.exe para AppIA.exe.
    - Executa o AppIA.exe atualizado.
    """
    current_dir = os.getcwd()  # Diretório atual
    main_old = os.path.join(current_dir, 'AppIA_old.exe')
    main_new = os.path.join(current_dir, 'AppIA_new.exe')
    main_main = os.path.join(current_dir, 'AppIA.exe')

    try:
        # Verifica se AppIA_old.exe existe e o exclui
        if os.path.exists(main_old):
            os.remove(main_old)
            print(f"{main_old} foi excluído.")

        # Se AppIA_new.exe existir, atualiza os arquivos
        if os.path.exists(main_new):
            if os.path.exists(main_main):
                os.rename(main_main, main_old)
                print(f"{main_main} foi renomeado para {main_old}.")

            os.rename(main_new, main_main)
            print(f"{main_new} foi renomeado para {main_main}.")

            # Executa o novo AppIA.exe
            print(f"Executando {main_main}...")
            subprocess.Popen([main_main], shell=True)

            # Encerra o script atual
            print("Encerrando o backend...")
            sys.exit()

    except Exception as e:
        print(f"Erro ao gerenciar os arquivos: {e}")
