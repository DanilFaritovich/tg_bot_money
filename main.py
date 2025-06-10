import bot


def get_error():
    try:
        bot.main()
    except Exception as e:
        print(e)
        return get_error()


if __name__ == '__main__':
    get_error()
