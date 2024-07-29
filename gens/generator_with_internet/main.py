# Custom provider for faker that returns random mechanical service name from a predefined set
import os
import csv
from faker import Faker
import random
from datetime import datetime, timedelta
print("Welcome to 193095_190473 Generator \n")

class MechanicalFailureProvider:
    def __init__(self, faker):
        self.faker = faker

    def service_list(self):
        services = []
        with open('serviceList.bulk', 'r', newline='', encoding="UTF-8") as serv:
            reader = csv.reader(serv, delimiter='|')
            for row in reader:
                services.append(row)
            serv.close()
        return random.choice(services)


# linear search used for proper assigning of 'b' - busses to courses and 's' - stops to courses
def find_index(arr, key, flag):
    if flag == 'b':
        for x in range(len(arr)):
            if arr[x][0] == key:
                return x
    elif flag == 's':
        for x in range(len(arr)):
            if arr[x][1] == key:
                return x
    else:
        exit("Bad index in function find_index()")


def gen_stops(courses, stops_name_with_index, users_min_number_stops_per_course, users_max_number_stops_per_course,
              users_date_start, users_date_end):
    array_helper = []  # Array which informs us if we already assign all necessary data for particular bus number
    stops_during_one_course = []  # Array which is saved into stops csv file
    # array_with_bus_number - array which stores all bus numbers used in the array courses
    # It stores number of the bus, flag which informs us if we assign route for the bus number,
    # In the data_base description we decide on simplification,
    # That single bus number can have at most four courses during one day
    # That is why we assign four initial and final hours for the course
    # Four flags in this array inform us if we assign planned arrival time on the bus number's cruise for all stations
    # We store initial and final station
    # We store all stations in the particular course
    # We store planned arrival time
    # stops_during_one_course[bus number, flag if we assign route for the bus number, 4 initial hours, 4 final hours,
    # four flags described in 48 line, initial station, final station, whole route,
    # planned arrival time for four initial hours]
    array_with_bus_numbers = []
    for x in range(len(courses)):
        if [courses[x][1]] not in array_helper:
            # Initial hours are different for night courses
            if courses[x][1][0] == 'N':
                start_hour = [random.randint(0, 6), random.randint(0, 6), random.randint(0, 6),
                              random.randint(0, 6)]
            else:
                start_hour = [random.randint(6, 19), random.randint(6, 19), random.randint(6, 19),
                              random.randint(6, 19)]
            end_hour = [start_hour[0] + 1, start_hour[1] + 1, start_hour[2] + 1, start_hour[3] + 1, ]
            array_helper.append([courses[x][1]])
            array_with_bus_numbers.append([courses[x][1], False, start_hour, end_hour, False, False, False, False,
                                           stops_name_with_index[find_index(stops_name_with_index, courses[x][3],
                                                                            's')][0],
                                           stops_name_with_index[find_index(stops_name_with_index, courses[x][4],
                                                                            's')][0], None, [], [], [], []])

    # In this loop we assign exact route for all buses
    for x in range(len(array_with_bus_numbers)):
        number_of_stops = random.randint(users_min_number_stops_per_course, users_max_number_stops_per_course)
        bus_number_route = [array_with_bus_numbers[x][8]]
        for i in range(1, number_of_stops):
            bus_stop_id = stops_name_with_index[random.choice(range(len(stops_name_with_index)))][0]
            if bus_stop_id not in bus_number_route and bus_stop_id != array_with_bus_numbers[x][9]:
                bus_number_route.append(bus_stop_id)
        bus_number_route.append(array_with_bus_numbers[x][9])
        array_with_bus_numbers[x][10] = bus_number_route

    # In this loop we assign planned arrival time for all bus numbers, on each station
    for x in range(len(array_with_bus_numbers)):
        clean_duration = 0
        start_date = datetime.strptime(users_date_start, "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(users_date_end, "%Y-%m-%d %H:%M:%S")
        random_days = random.randint(0, (end_date - start_date).days)
        beg_hour = 0
        # Each bus number has at most four different courses during one day
        # We have to assign planned arrival time for each one
        for _ in range(4):
            clean_hour = array_with_bus_numbers[x][2][0 + beg_hour]
            tmp = []
            for i in range(len(array_with_bus_numbers[x][10])):
                date = start_date + timedelta(days=random_days)
                current_trip_duration = random.randint(1, 5)
                clean_duration += current_trip_duration
                if clean_duration > 59:
                    clean_duration -= 60
                    clean_hour += 1
                if clean_hour == 24:
                    clean_hour = 0
                date_planned = datetime.strptime(f"{clean_hour}:{clean_duration}:{0}", "%H:%M:%S").time()
                tmp.append(datetime.combine(date, date_planned))
            array_with_bus_numbers[x][11 + beg_hour] = tmp
            beg_hour += 1

    # In this loop we assign values to array stops_during_one_course
    # stops_during_one_course array represents stops entity set in our data base
    need_continuity = False
    for x in range(len(courses)):
        cruise_nr = courses[x][1]  # Numer autobusu w kursie
        index = find_index(array_with_bus_numbers, cruise_nr, 'b')
        if need_continuity:
            # When previous course was unfinished we do not assign all stations to its continuation
            # Initial station for the continuity of the course is the final station of the unfinished course
            for i in range(len(array_with_bus_numbers[index][10]) - shorter_route,
                           len(array_with_bus_numbers[index][10])):
                stops_during_one_course.append([courses[x][0], array_with_bus_numbers[index][10][i]])
            need_continuity = False
        else:
            # If course is finished we assign typical route for the bus number which is used in the course
            if not courses[x][5]:
                for i in range(len(array_with_bus_numbers[index][10])):
                    stops_during_one_course.append([courses[x][0], array_with_bus_numbers[index][10][i]])
            # If course is unfinished we assign shorter route for the bus number which is used in the course
            else:
                # When course is unfinished we create shorter route by 4 to 6 stations
                shorter_route = random.randint(4, 6)
                for i in range(len(array_with_bus_numbers[index][10]) - shorter_route):
                    stops_during_one_course.append([courses[x][0], array_with_bus_numbers[index][10][i]])
                need_continuity = True
    return stops_during_one_course


# Generator of stops which is an implementation of many-to-many db relationship between courses and stations
# the function is designed is such way that buses with line number 122 always have the same list of stations
# with varying time schedules and delays. The same happens in case of a failure described on line 216.
# Another interesting functionality is shown by the need_continuity flag if during one course a bus is unable to
# finish it another course is created for a new bus starting from the station
# on which the old bus failed. Important thing: course is assigned to the bus not the driver.
def gen_stops_and_courses(stops_name_with_index, drivers, buses, users_number_of_courses, users_number_of_bus_lines,
                          users_min_number_stops_per_course, users_max_number_stops_per_course, users_date_start,
                          users_date_end):
    # helping lists
    courses = []
    output = []
    tmp = []
    # here we generate unique bus line numbers and their starting and finishing stations
    for x in range(users_number_of_bus_lines):
        tmp.append([f.unique.bothify(text="?##", letters="N1111111"),
                    stops_name_with_index[random.randint(0, len(stops_name_with_index) - 1)][1],
                    stops_name_with_index[random.randint(0, len(stops_name_with_index) - 1)][1]])

    # need_continuity flag
    need_continuity = False
    # We generate data for courses' entity set
    # array 'tmp' is responsible for storing number of buses and theirs initial and final station
    # array 'output' stores data which is saved into courses CSV file
    # array 'courses' stores the same data as 'output', but it contains additional data needed in the code
    for x in range(users_number_of_courses):
        temp = []
        # After every iteration of the loop we check if we created unfinished course
        # If yes, we create course which is continuity of the old one and Flag responsible for continuity is set as True
        # Variables - route, bus number (tmp[index_of_bus][0]), route, beg_stop, fin_stop are the same
        # Driver and the bus might be different
        # In database report we decide on simplification, continuity of unfinished course cannot have technical issues
        # That is why, flag responsible for unfinished course is set as False
        if need_continuity:
            temp.append(x)
            temp.append(tmp[index_of_bus][0])
            temp.append(route)
            temp.append(beg_stop)
            temp.append(fin_stop)
            temp.append(False)
            driv = drivers[random.randint(0, len(drivers) - 1)][0]
            bus = buses[random.randint(0, len(buses) - 1)][0]
            temp.append(driv)
            temp.append(bus)
            temp.append(False)
            temp.append(True)
            output.append([None, tmp[index_of_bus][0], route, "False", driv, bus, "True"])
            courses.append(temp)
            need_continuity = False
        else:
            temp.append(x)
            # We decide which bus number will be used in a course
            index_of_bus = random.randint(0, users_number_of_bus_lines - 1)
            temp.append(tmp[index_of_bus][0])
            beg_stop = tmp[index_of_bus][1]
            fin_stop = tmp[index_of_bus][2]
            route = beg_stop + ' -> ' + fin_stop
            temp.append(route)
            temp.append(beg_stop)
            temp.append(fin_stop)
            if random.choice(range(0, 15)) <= 1:
                temp.append(True)  # Flag informs us, if this course is unfinished
                helper = "True"
                need_continuity = True
            else:
                temp.append(False)
                helper = "False"
            driv = drivers[random.randint(0, len(drivers) - 1)][0]
            bus = buses[random.randint(0, len(buses) - 1)][0]
            temp.append(driv)
            temp.append(bus)
            temp.append(False)  # Flag informs us, if we assign stations for the course
            temp.append(False)  # Flag informs us, if this course is continuity
            output.append([None, tmp[index_of_bus][0], route, helper, driv, bus, "False"])
            courses.append(temp)

    # Function gen_stops is an implementation of many-to-many db relationship between courses and stations
    stops_during_one_course = gen_stops(courses, stops_name_with_index, users_min_number_stops_per_course,
                                        users_max_number_stops_per_course, users_date_start, users_date_end)

    return [stops_during_one_course, output]


# Generating unique personal data: Pesel, First name, Last name, Email, Phone number (no country prefix)
# In current state maximum number of drivers a user can input is probably 10^9 due to phone number combinations,
# It could be less but no information was found in Faker[pl_PL] docs
def gen_drivers(users_num_of_drivers=100000):
    drivers = [[f.unique.pesel(), f.first_name(), f.last_name(), f.unique.email(),
                f.unique.bothify(text="#########", letters="0123456789")] for _ in range(1, users_num_of_drivers)]

    with open('drivers_gen.bulk', 'w', newline='', encoding="UTF-8") as driversf:
        writer = csv.writer(driversf, delimiter='|')
        writer.writerows(drivers)
        driversf.close()

    return drivers


# Due to unfortunate way of pandas library handling of dataframes we had to rewrite the dataframe manually to enable
# ourselves easy bulk file creation
def write_variants(data):
    hold = []
    # First write whole dataframe to csv whole text as one unfortunately
    data.to_csv('variants.bulk', header=False, index=False, encoding="UTF-8", sep='|')
    # converting the data into a readable and usefull format
    with open('variants.bulk', 'r', newline='', encoding="UTF-8") as varf:
        reader = csv.reader(varf)
        for row in reader:
            ex = row[0].split('|')
            if len(ex) == 3:
                hold.append([None, str(ex[0]), str(ex[1]), str(ex[2])])
        varf.close()
    # creation of destination bulk file
    with open('variants.bulk', 'w', newline='', encoding="UTF-8") as varf:
        writer = csv.writer(varf, delimiter='|')
        for _ in hold:
            writer.writerow(_)
        varf.close()

    return len(hold)


# Here using libraries beautifullsoup4 and pandas we scraped data about real bus variants from wikipedia
def scrape_bus_variants():
    url = "https://en.wikipedia.org/wiki/List_of_buses"
    data = requests.get(url).text
    soup = BeautifulSoup(data, 'html.parser')
    # at this point variable soup contains whole html of site under the url variable

    # empty dataset for future operations
    df = pd.DataFrame(columns=['Name', 'Manufacturer', 'Year'])

    # collecting all tables with html class 'wikitable'
    tables = soup.find_all('table', class_='wikitable')
    for _ in tables:
        # gathering and iterating through every data row of wikipedia's tables
        for row in _.tbody.find_all('tr'):
            columns = row.find_all('td')
            if columns:
                # tables contained more data below we gain what we need
                name = columns[0].text.strip()
                manufacturer = columns[3].text.strip()
                year = (columns[4]).text.strip()[:4]
                if len(year) > 3:
                    if year.isnumeric():
                        df = df._append({'Name': name, 'Manufacturer': manufacturer, 'Year': year}, ignore_index=True)

    return write_variants(df)


# Function used to save the results of generating repairs which are an individual visit of the bus in the workshop
# during it many services can be performed. The price of repair is the sum of service prices. Maximum num_of_services
# due to the real nature of our data is 254 and maximum of users_num_of_buses is 1185
def gen_buses_and_repairs_and_services(users_date_start="2015-01-01 00:00:00", users_date_end="2024-04-15 23:59:59",
                                       users_num_of_services=254, users_num_of_buses=1185, users_num_of_repairs=30000,
                                       users_rep_price_min=0, users_rep_price_max=2000000, users_variants_num=1185):

    # Generating unique number of buses given by the user. Vin, License plate, depot number: business key for the
    # bus transportation company
    buses = [[f.unique.vin(), f.unique.license_plate(), f.unique.bothify(text="#####"),
              random.choice(range(users_variants_num))] for _ in range(users_num_of_buses)]

    repairs = []
    for _ in range(users_num_of_repairs):
        lower_bound = f.date_time_between(datetime.strptime(users_date_start, "%Y-%m-%d %H:%M:%S"),
                                          datetime.strptime(users_date_end, "%Y-%m-%d %H:%M:%S"))
        end_rep = f.date_time_between(lower_bound, datetime.strptime(users_date_end, "%Y-%m-%d %H:%M:%S"))
        repairs.append([None, lower_bound.strftime('%Y-%m-%d %H:%M:%S'), end_rep.strftime('%Y-%m-%d %H:%M:%S'),
                        round(random.uniform(users_rep_price_min, users_rep_price_max), 2),
                        buses[random.choice(range(users_num_of_buses))][0]])

    # Generator of usages which is an implementation of many-to-many db relationship between repairs and services
    usages = []
    for _ in range(len(repairs)):
        temp = []
        for i in range(random.randint(1, 10)):
            x = random.randint(1, users_num_of_services)
            if x not in temp:
                temp.append(x)
                usages.append([_, x])

    with open('buses_gen.bulk', 'w', newline='', encoding="UTF-8") as busf:
        writer = csv.writer(busf, delimiter='|')
        writer.writerows(buses)
        busf.close()

    with open('repairs_gen.bulk', 'w', newline='', encoding="UTF-8") as repairf:
        writer = csv.writer(repairf, delimiter='|')
        writer.writerows(repairs)
        repairf.close()

    with open('usages_gen.bulk', 'w', newline='', encoding="UTF-8") as usagesf:
        writer = csv.writer(usagesf, delimiter='|')
        writer.writerows(usages)
        usagesf.close()

    with open('services_gen.bulk', 'w', newline='', encoding="UTF-8") as servicef:
        writer = csv.writer(servicef, delimiter='|')
        temp = set()
        for j in range(users_num_of_services):
            if mech_prov.service_list()[0] not in temp:
                temp.add(mech_prov.service_list()[0])
                writer.writerow([None, temp.pop(), "Description Lorem Ipsum1"])
        servicef.close()
    return buses


# function used to save the results of generating data for the entity sets: stations, courses, stops where stops is the
# implementation of many-to-many relationship between courses and stations.
def gen_stat_cours_stops(drivers, buses, users_num_of_stations=70000, users_number_of_courses=50000,
                         users_num_of_bus_lines=75, users_min_number_stops_per_course=15,
                         users_max_number_stops_per_course=30, users_date_start="2015-01-01 00:00:00",
                         users_date_end="2024-04-15 23:59:59"):
    fs = Faker(["en_US"])
    # Generating unique names for bus stops in the count specified by user unfortunately not enough Polish street names
    # are available in Faker, so we used american instead.
    stations = [fs.unique.street_name() for _ in range(users_num_of_stations)]

    stations_name_with_index = []
    file_stop = []
    # Indexing stops for future calculations
    for x in range(len(stations)):
        stations_name_with_index.append([x, stations[x]])
        file_stop.append([None, stations[x]])

    [stops_during_one_course, output] = \
        (gen_stops_and_courses(stations_name_with_index, drivers, buses, users_number_of_courses,
                               users_num_of_bus_lines, users_min_number_stops_per_course,
                               users_max_number_stops_per_course, users_date_start, users_date_end))

    with open('stations_gen.bulk', 'w', newline='', encoding="UTF-8") as stationsf:
        writer = csv.writer(stationsf, delimiter='|')
        writer.writerows(file_stop)
        stationsf.close()

    with open('stops_gen.bulk', 'w', newline='', encoding="UTF-8") as stopsf:
        writer = csv.writer(stopsf, delimiter='|')
        writer.writerows(stops_during_one_course)
        stopsf.close()

    with open('courses_gen.bulk', 'w', newline='', encoding="UTF-8") as coursesf:
        writer = csv.writer(coursesf, delimiter='|')
        writer.writerows(output)
        coursesf.close()


# The start point of bus transportation generator the assumption of this program is reality that's why entity sets
# like services, stations, busVariants suffer on their counts, but we didn't find it attractive to put lorem ipsum
# everywhere or other nonsensical data. Nevertheless, above code is easy and readable so modifying it for such approach
# will be non-problematic

def validate(date_text):
    try:
        if date_text != datetime.strptime(date_text, "%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d %H:%M:%S'):
            raise ValueError
        return True
    except ValueError:
        return False


def validate_input(flag):

    match flag:
        case 1:
            params[0] = input("Enter the starting date of generated data (YYYY-MM-DD HH:MM:SS) "
                              "example: 2015-01-01 00:00:00 > ")
            if validate(params[0]):
                return True
            else:
                return False
        case 2:
            params[1] = input("Enter the ending date of generated data (YYYY-MM-DD HH:MM:SS) "
                              "example: 2024-04-15 23:59:59 > ")
            if validate(params[1]) and (datetime.strptime(params[0], "%Y-%m-%d %H:%M:%S")
                                        < datetime.strptime(params[1], "%Y-%m-%d %H:%M:%S")):
                return True
            else:
                return False
        case 3:
            params[2] = input("Enter the number of services you would like to generate, from 2 to 254 > ")
            if params[2].isdigit():
                params[2] = int(params[2])
                if 254 >= params[2] >= 2:
                    return True
                else:
                    return False
        case 4:
            params[3] = input("Enter the number of buses you would like to generate, minimum 2 > ")
            if params[3].isdigit():
                params[3] = int(params[3])
                if params[3] >= 2:
                    return True
                else:
                    return False
        case 5:
            params[4] = input("Enter the number of repairs you would like to generate, minimum 2 > ")
            if params[4].isdigit():
                params[4] = int(params[4])
                if params[4] >= 2:
                    return True
                else:
                    return False
        case 6:
            params[5] = input("Enter the minimal price of a repair(sum of services)"
                              " you would like to generate, minimum 0 > ")
            if params[5].isdigit():
                params[5] = int(params[5])
                if params[5] >= 0:
                    return True
                else:
                    return False
        case 7:
            params[6] = input("Enter the maximal price of a repair(sum of services)"
                              " you would like to generate, minimum 0 > ")
            if params[6].isdigit():
                params[6] = int(params[6])
                if params[6] >= 0 and params[6] >= params[5]:
                    return True
                else:
                    return False
        case 8:
            params[7] = input("Enter the number of bus variants to choose from maximum 1185, minimum 1 > ")
            if params[7].isdigit():
                params[7] = int(params[7])
                if 1185 >= params[7] >= 1:
                    return True
                else:
                    return False
        case 9:
            params[8] = input("Enter the number of drivers you would like to generate minimum 1 > ")
            if params[8].isdigit():
                params[8] = int(params[8])
                if params[8] > 0:
                    return True
                else:
                    return False
        case 10:
            params[9] = input("Enter the number of stations you would like to generate minimum 1 > ")
            if params[9].isdigit():
                params[9] = int(params[9])
                if params[9] > 0:
                    return True
                else:
                    return False
        case 11:
            params[10] = input("Enter the number of courses you would like to generate minimum 0 > ")
            if params[10].isdigit():
                params[10] = int(params[10])
                if params[10] >= 0:
                    return True
                else:
                    return False
        case 12:
            params[11] = input("Enter the number of bus lines you would like to generate minimum: 0, maximum: 200 > ")
            if params[11].isdigit():
                params[11] = int(params[11])
                if 200 >= params[11] >= 0:
                    return True
                else:
                    return False
        case 13:
            params[12] = input("Enter the minimum number of stops per course minimum 1 > ")
            if params[12].isdigit():
                params[12] = int(params[12])
                if params[12] >= 1:
                    return True
                else:
                    return False
        case 14:
            params[13] = input("Enter the maximum number of stops per course > ")
            if params[13].isdigit():
                params[13] = int(params[13])
                if params[13] >= 1 and params[13] >= params[12]:
                    return True
            else:
                return False


def get_params():
    ans = input("Would you like to use default parameters? (y/n): ")
    os.system('cls')
    if ans == 'n':
        i = 1
        while i < 15:
            if validate_input(i):
                i += 1
            else:
                os.system('cls')

        print("Processing data... ")
        # params indexes ->
        # 0 -> startDate
        # 1 -> endDate
        # 2 -> service number
        # 3 -> bus number
        # 4 -> repairs number
        # 5 -> min repair price
        # 6 -> max repair price
        # 7 -> bus variants number
        # 8 -> driver number
        # 9 -> station number
        # 10 -> course number
        # 11 -> bus line number
        # 12 -> min stops per course
        # 13 -> max stops per course

        if internet == 1:
            buses = gen_buses_and_repairs_and_services(params[0], params[1], params[2], params[3], params[4], params[5],
                                                       params[6], variants_number)
        else:
            buses = gen_buses_and_repairs_and_services(params[0], params[1], params[2], params[3], params[4], params[5],
                                                       params[6], params[7])

        gen_stat_cours_stops(gen_drivers(params[8]), buses, params[9], params[10], params[11], params[12], params[13],
                             params[0], params[1])
    else:
        os.system('cls')
        print("Processing data... ")
        buses = gen_buses_and_repairs_and_services()
        gen_stat_cours_stops(gen_drivers(), buses)

internet = 1  # flag if 1 user has internet access if 0 user hasn't switch if necessary
if internet == 1:
    import pandas as pd
    import requests
    from bs4 import BeautifulSoup
    variants_number = scrape_bus_variants()

f = Faker(["pl_PL"])
mech_prov = MechanicalFailureProvider(f)
f.add_provider(mech_prov)
params = [None] * 14
get_params()

input("Generating complete, press any key to exit...")
