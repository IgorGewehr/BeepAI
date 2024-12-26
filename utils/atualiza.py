import os

def manage_main_files():
    """
    Gerencia a substituição de arquivos AppIA.exe.
    - Remove o arquivo AppIA_old.exe, se existir.
    - Renomeia AppIA.exe para AppIA_old.exe, se AppIA_new.exe existir.
    - Renomeia AppIA_new.exe para AppIA.exe.
    """
    current_dir = os.getcwd()  # Diretório atual
    main_old = os.path.join(current_dir, 'AppIA_old.exe')
    main_new = os.path.join(current_dir, 'AppIA_new.exe')
    main_main = os.path.join(current_dir, 'AppIA.exe')

    try:
        # Remove AppIA_old.exe se existir
        if os.path.exists(main_old):
            os.remove(main_old)
            print(f"{main_old} foi excluído.")

        # Se AppIA_new.exe existir, faça a substituição
        if os.path.exists(main_new):
            # Verifica se AppIA.exe existe antes de renomear
            if os.path.exists(main_main):
                # Renomeia AppIA.exe para AppIA_old.exe
                os.rename(main_main, main_old)
                print(f"{main_main} foi renomeado para {main_old}.")

            # Renomeia AppIA_new.exe para AppIA.exe
            os.rename(main_new, main_main)
            print(f"{main_new} foi renomeado para {main_main}.")

    except Exception as e:
        print(f"Erro ao gerenciar os arquivos: {e}")
#final
