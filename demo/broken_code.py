def run():
    try:
        return 10 / 0
    except ZeroDivisionError:
        return 0
run()