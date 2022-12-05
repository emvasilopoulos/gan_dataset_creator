"""
This is a tutorial on how to have fun with your girlfriend. Be open-minded...
"""


def eleni_function(love_percentage):
    if love_percentage == 100:
        return 'Good for you.'
    elif love_percentage > 100:
        return 'Get married already'
    else:
        return f'Eleni and Manos are stupid. \nTheir total love should be at least 100. Now it is {love_percentage}.\n Please raise it...'


if __name__ == '__main__':
    # Current love at 4/12/2022 is 100 from each
    eleni_love = 100
    manos_love = 100

    eleni_and_manos_love = eleni_love + manos_love  # Pososto agapis

    message = eleni_function(eleni_and_manos_love)

    print(message)
