def doubebarrel_conversion(full_name):
    '''
    Takes in a de-slugified name and adds the hyphon to make them doube-barrel if necessary
    :param fullname:
    :return:
    '''

    print('FULL NAME:', full_name)

    doublebarrel = ['Aaron Wan Bissaka', 'Addji Keaninkin Marc Israel Guehi', 'Ainsley Maitland Niles', 'Alex Mccarthy',
                    'Alex Oxlade Chamberlain', 'Allan Saint Maximin', 'Andre-Frank Zambo Anguissa',
                    'Bailey Peacock Farrell', 'Bobby De Cordova-Reid', 'Callum Hudson Odoi', 'CJ Egan Riley',
                    'Daniel Nlundulu', 'Dara Oshea', 'David De Gea', 'David Mcgoldrick', 'Deandre Yedlin',
                    'Dominic Calvert Lewin', 'Donny Van De Beek', 'Georges Kevin Nkoudou', 'Hal Robson Kanu',
                    'Hwang Hee Chan', 'Ian Poveda Ocampo', 'Jack Oconnell', 'Jaden Philogene Bidace', 'James Mcarthur',
                    'James Mcatee', 'James Mccarthy', 'James Ward Prowse', 'Jean Philippe Gbamin',
                    'Jean Philippe Mateta', 'Jesurun Rak Sakyi', 'John Mcginn', 'Kasey Mcateer', 'Kenny Mclean',
                    'Ki Jana Hoever', 'Ki Sung-Yueng', 'Kiernan Dewsbury Hall', 'Kyle Walker Peters', 'Liam Mccarron',
                    'Michael Mcgovern', 'Morgan Gibbs White', 'Nathan Young Coombes', 'Ngolo Kante', 'Oliver Mcburnie',
                    'Patrick Van Aanholt', 'Pierre Lees Melou', 'Pierre Emerick Aubameyang', 'Pierre Emile Hojbjerg',
                    'Rayan Ait Nouri', 'Ruben Loftus Cheek', 'Scott Mctominay', 'Son Heung Min', 'Stuart Mckinstry',
                    'Tariqe Fosu Henry', 'Timothy Fosu Mensah', 'Trent Alexander Arnold', 'Virgil Van Dijk',
                    'William Troost Ekong']

    for i, name in enumerate(doublebarrel):
        if i == 0 and full_name == name:
            full_name = name.replace('Wan Bissaka', 'Wan-Bissaka')
        elif i == 1 and full_name == name:
            full_name = name.replace('Marc Israel', 'Marc-Israel')
        elif i == 2 and full_name == name:
            full_name = name.replace('Maitland Niles', 'Maitland-Niles')
        elif i == 3 and full_name == name:
            full_name = name.replace('Mccarthy', 'McCarthy')
        elif i == 4 and full_name == name:
            full_name = name.replace('Oxlade Chamberlain', 'Oxlade-Chamberlain')
        elif i == 5 and full_name == name:
            full_name = name.replace('Saint Maximin', 'Saint-Maximin')
        elif i == 6 and full_name == name:
            full_name = name.replace('Andre Frank', 'Andre-Frank')
        elif i == 7 and full_name == name:
            full_name = name.replace('Peacock Farrell', 'Peacock-Farrell')
        elif i == 8 and full_name == name:
            full_name = name.replace('Cordova Reid', 'Cordova-Reid')
        elif i == 9 and full_name == name:
            full_name = name.replace('Hudson Odoi', 'Hudson-Odoi')
        elif i == 10 and full_name == name:
            full_name = name.replace('Egan Riley', 'Egan-Riley')
        elif i == 11 and full_name == name:
            full_name = name.replace('Nlundulu', 'N\'Lundulu')
        elif i == 12 and full_name == name:
            full_name = name.replace('Oshea', 'O\'Shea')
        elif i == 13 and full_name == name:
            full_name = name.replace('De', 'de')
        elif i == 14 and full_name == name:
            full_name = name.replace('Mcgoldrick', 'McGoldrick')
        elif i == 15 and full_name == name:
            full_name = name.replace('Deandre', 'DeAndre')
        elif i == 16 and full_name == name:
            full_name = name.replace('Calvert Lewin', 'Calvert-Lewin')
        elif i == 17 and full_name == name:
            full_name = name.replace('Van De', 'van de')
        elif i == 18 and full_name == name:
            full_name = name.replace('Georges Kevin', 'Georges-Kevin')
        elif i == 19 and full_name == name:
            full_name = name.replace('Robson Kanu', 'Robson-Kanu')
        elif i == 20 and full_name == name:
            full_name = name.replace('Hee Chan', 'Hee-Chan')
        elif i == 21 and full_name == name:
            full_name = name.replace('Poveda Ocampo', 'Poveda-Ocampo')
        elif i == 22 and full_name == name:
            full_name = name.replace('Oconnell', 'O\'Connell')
        elif i == 23 and full_name == name:
            full_name = name.replace('Philogene Bidace', 'Philogene-Bidace')
        elif i == 24 and full_name == name:
            full_name = name.replace('Mcarthur', 'McArthur')
        elif i == 25 and full_name == name:
            full_name = name.replace('Mcatee', 'McAtee')
        elif i == 26 and full_name == name:
            full_name = name.replace('Mccarthy', 'McCarthy')
        elif i == 27 and full_name == name:
            full_name = name.replace('Ward Prowse', 'Ward-Prowse')
        elif i == 28 and full_name == name:
            full_name = name.replace('Jean Philippe', 'Jean-Philippe')
        elif i == 29 and full_name == name:
            full_name = name.replace('Jean Philippe', 'Jean-Philippe')
        elif i == 30 and full_name == name:
            full_name = name.replace('Rak Sakyi', 'Rak-Sakyi')
        elif i == 31 and full_name == name:
            full_name = name.replace('Mcginn', 'McGinn')
        elif i == 32 and full_name == name:
            full_name = name.replace('Mcateer', 'McAteer')
        elif i == 33 and full_name == name:
            full_name = name.replace('Mclean', 'McLean')
        elif i == 34 and full_name == name:
            full_name = name.replace('Ki Jana', 'Ki-Jana')
        elif i == 35 and full_name == name:
            full_name = name.replace('Sung Yueng', 'Sung-Yueng')
        elif i == 36 and full_name == name:
            full_name = name.replace('Dewsbury Hall', 'Dewsbury-Hall')
        elif i == 37 and full_name == name:
            full_name = name.replace('Walker Peters', 'Walker-Peters')
        elif i == 38 and full_name == name:
            full_name = name.replace('Mccarron', 'McCarron')
        elif i == 39 and full_name == name:
            full_name = name.replace('Mcgovern', 'McGovern')
        elif i == 40 and full_name == name:
            full_name = name.replace('Gibbs White', 'Gibbs-White')
        elif i == 41 and full_name == name:
            full_name = name.replace('Young Coombes', 'Young-Coombes')
        elif i == 42 and full_name == name:
            full_name = name.replace('Ngolo', 'N\'Golo')
        elif i == 43 and full_name == name:
            full_name = name.replace('Mcburnie', 'McBurnie')
        elif i == 44 and full_name == name:
            full_name = name.replace('Van', 'van')
        elif i == 45 and full_name == name:
            full_name = name.replace('Lees Melou', 'Lees-Melou')
        elif i == 46 and full_name == name:
            full_name = name.replace('Pierre Emerick', 'Pierre-Emerick')
        elif i == 47 and full_name == name:
            full_name = name.replace('Pierre Emile', 'Pierre-Emile')
        elif i == 48 and full_name == name:
            full_name = name.replace('Ait Nouri', 'Ait-Nouri')
        elif i == 49 and full_name == name:
            full_name = name.replace('Loftus Cheek', 'Loftus-Cheek')
        elif i == 50 and full_name == name:
            full_name = name.replace('Mctominay', 'McTominay')
        elif i == 51 and full_name == name:
            full_name = name.replace('Heung Min', 'Heung-Min')
        elif i == 52 and full_name == name:
            full_name = name.replace('Mckinstry', 'McKinstry')
        elif i == 53 and full_name == name:
            full_name = name.replace('Fosu Henry', 'Fosu-Henry')
        elif i == 54 and full_name == name:
            full_name = name.replace('Fosu Mensah', 'Fosu-Mensah')
        elif i == 55 and full_name == name:
            full_name = name.replace('Alexander Arnold', 'Alexander-Arnold')
        elif i == 56 and full_name == name:
            full_name = name.replace('Van', 'van')
        elif i == 57 and full_name == name:
            full_name = name.replace('Troost Ekong', 'Troost-Ekong')

    return full_name
