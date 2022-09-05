def doubebarrel_conversion(full_name):
    '''
    Takes in a de-slugified name and adds the hyphon to make them doube-barrel if necessary
    :param fullname:
    :return:
    '''

    doublebarrel = ['Pierre Emerick Aubameyang', 'Bailey Peacock Farrell', 'Callum Hudson Odoi',
                    'Jean Philippe Mateta', 'Dominic Calvert Lewin', 'Ruben Loftus Cheek', 'Bobby De Cordova Reid',
                    'Andre Frank Zambo Anguissa', 'Ian Poveda Ocampo', 'Trent Alexander Arnold',
                    'Alex Oxlade Chamberlain', 'Aaron Wan Bissaka', 'Allan Saint Maximin', 'James Ward Prowse',
                    'Kyle Walker Peters', 'Pierre Emile Hojbjerg', 'Son Heung Min', 'Ainsley Maitland Niles',
                    'Hal Robson Kanu', 'Rayan Ait Nouri', 'Ki Jana Hoever', 'Morgan Gibbs White', 'John Mcginn',
                    'Dwight Mcneil', 'Patrick Van Aanholt', 'James Mcarthur', 'James Mccarthy', 'Virgil Van Dijk',
                    'Donny Van De Beek', 'Scott Mctominay', 'Jack Oconnell', 'David Mcgoldrick', 'Oliver Mcburnie',
                    'Alex Mccarthy', 'Daniel Nlundulu', 'Dara Oshea', 'Jean Philippe Gbamin']

    for i, name in enumerate(doublebarrel):
        if i == 0 and full_name == name:
            full_name = name.replace('Pierre Emerick', 'Pierre-Emerick')
        elif i == 1 and full_name == name:
            full_name = name.replace('Peacock Farrell', 'Peacock-Farrell')
        elif i == 2 and full_name == name:
            full_name = name.replace('Hudson Odoi', 'Hudson-Odoi')
        elif i == 3 and full_name == name:
            full_name = name.replace('Jean Philippe', 'Jean-Philippe')
        elif i == 4 and full_name == name:
            full_name = name.replace('Calvert Lewin', 'Calvert-Lewin')
        elif i == 5 and full_name == name:
            full_name = name.replace('Loftus Cheek', 'Loftus-Cheek')
        elif i == 6 and full_name == name:
            full_name = name.replace('Cordova Reid', 'Cordova-Reid')
        elif i == 7 and full_name == name:
            full_name = name.replace('Andre Frank', 'Andre-Frank')
        elif i == 8 and full_name == name:
            full_name = name.replace('Poveda Ocampo', 'Poveda-Ocampo')
        elif i == 9 and full_name == name:
            full_name = name.replace('Alexander Arnold', 'Alexander-Arnold')
        elif i == 10 and full_name == name:
            full_name = name.replace('Oxlade Chamberlain', 'Oxlade-Chamberlain')
        elif i == 11 and full_name == name:
            full_name = name.replace('Wan Bissaka', 'Wan-Bissaka')
        elif i == 12 and full_name == name:
            full_name = name.replace('Saint Maximin', 'Saint-Maximin')
        elif i == 13 and full_name == name:
            full_name = name.replace('Ward Prowse', 'Ward-Prowse')
        elif i == 14 and full_name == name:
            full_name = name.replace('Walker Peters', 'Walker-Peters')
        elif i == 15 and full_name == name:
            full_name = name.replace('Pierre Emile', 'Pierre-Emile')
        elif i == 16 and full_name == name:
            full_name = name.replace('Heung Min', 'Heung-Min')
        elif i == 17 and full_name == name:
            full_name = name.replace('Maitland Niles', 'Maitland-Niles')
        elif i == 18 and full_name == name:
            full_name = name.replace('Robson Kanu', 'Robson-Kanu')
        elif i == 19 and full_name == name:
            full_name = name.replace('Ait Nouri', 'Ait-Nouri')
        elif i == 20 and full_name == name:
            full_name = name.replace('Ki Jana', 'Ki-Jana')
        elif i == 21 and full_name == name:
            full_name = name.replace('Gibbs White', 'Gibbs-White')
        elif i == 22 and full_name == name:
            full_name = name.replace('Mcginn', 'McGinn')
        elif i == 23 and full_name == name:
            full_name = name.replace('Mcneil', 'McNeil')
        elif i == 24 and full_name == name:
            full_name = name.replace('Van Aanholt', 'van Aanholt')
        elif i == 25 and full_name == name:
            full_name = name.replace('Mcarthur', 'McArthur')
        elif i == 26 and full_name == name:
            full_name = name.replace('Mccarthy', 'McCarthy')
        elif i == 27 and full_name == name:
            full_name = name.replace('Van Dijk', 'van Dijk')
        elif i == 28 and full_name == name:
            full_name = name.replace('Van De', 'van de')
        elif i == 29 and full_name == name:
            full_name = name.replace('Mctominay', 'McTominay')
        elif i == 30 and full_name == name:
            full_name = name.replace('Oconnell', 'OConnell')
        elif i == 31 and full_name == name:
            full_name = name.replace('Mcgoldrick', 'McGoldrick')
        elif i == 32 and full_name == name:
            full_name = name.replace('Mcburnie', 'McBurnie')
        elif i == 33 and full_name == name:
            full_name = name.replace('Mccarthy', 'McCarthy')
        elif i == 34 and full_name == name:
            full_name = name.replace('Nlundulu', 'NLundulu')
        elif i == 35 and full_name == name:
            full_name = name.replace('Oshea', 'OShea')
        elif i == 36 and full_name == name:
            full_name = name.replace('Jean Philippe', 'Jean-Philippe')

    return full_name
