import prompt

def print_help():
    print("<command> exit - выйти из программы")
    print("<command> help - справочная информация")

def welcome():
    print("Первая попытка запустить проект!")
    print()
    print("***")
    print_help()

    while True:
        command = prompt.string("Введите команду: ").strip()

        if command == "exit":
            break
        elif command == "help":
            print()
            print_help()

